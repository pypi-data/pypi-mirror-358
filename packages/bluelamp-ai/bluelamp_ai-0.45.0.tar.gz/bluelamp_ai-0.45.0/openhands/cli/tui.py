# CLI TUI input and output functions
# Handles all input and output to the console
# CLI Settings are handled separately in cli_settings.py

import asyncio
import logging
import sys
import threading
import time
from typing import Generator

from prompt_toolkit import PromptSession, print_formatted_text
from prompt_toolkit.application import Application
from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import HTML, FormattedText, StyleAndTextTuples
from prompt_toolkit.input import create_input
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.shortcuts import print_container
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Frame, TextArea

from openhands import __version__
from openhands.cli.branding import (
    BLUELAMP_BANNER,
    STYLE_DICT,
    MESSAGES,
    COMMAND_DESCRIPTIONS,
    get_message,
    get_color,
)
from openhands.core.config import OpenHandsConfig
from openhands.core.schema import AgentState
from openhands.events import EventSource, EventStream
from openhands.events.action import (
    Action,
    ActionConfirmationStatus,
    ChangeAgentStateAction,
    CmdRunAction,
    MessageAction,
)
from openhands.events.event import Event
from openhands.events.observation import (
    AgentStateChangedObservation,
    CmdOutputObservation,
    ErrorObservation,
    FileEditObservation,
    FileReadObservation,
)
from openhands.llm.metrics import Metrics

# Get logger for debug output
logger = logging.getLogger('bluelamp.cli.tui')

ENABLE_STREAMING = False  # FIXME: this doesn't work

# Global TextArea for streaming output
streaming_output_text_area: TextArea | None = None

# Color and styling constants - BlueLamp theme
COLOR_GOLD = get_color('primary')  # Map old gold to primary blue
COLOR_GREY = get_color('grey')
DEFAULT_STYLE = Style.from_dict(STYLE_DICT)

COMMANDS = COMMAND_DESCRIPTIONS

print_lock = threading.Lock()


class UsageMetrics:
    def __init__(self) -> None:
        self.metrics: Metrics = Metrics()
        self.session_init_time: float = time.time()


class CustomDiffLexer(Lexer):
    """Custom lexer for the specific diff format."""

    def lex_document(self, document: Document) -> StyleAndTextTuples:
        lines = document.lines

        def get_line(lineno: int) -> StyleAndTextTuples:
            line = lines[lineno]
            if line.startswith('+'):
                return [('ansigreen', line)]
            elif line.startswith('-'):
                return [('ansired', line)]
            elif line.startswith('[') or line.startswith('('):
                # Style for metadata lines like [Existing file...] or (content...)
                return [('bold', line)]
            else:
                # Default style for other lines
                return [('', line)]

        return get_line


# CLI initialization and startup display functions
def display_runtime_initialization_message(runtime: str) -> None:
    print_formatted_text('')
    if runtime == 'local':
        print_formatted_text(HTML('<grey>⚙️ Starting local runtime...</grey>'))
    elif runtime == 'docker':
        print_formatted_text(HTML('<grey>🐳 Starting Docker runtime...</grey>'))
    print_formatted_text('')


def display_initialization_animation(text: str, is_loaded: asyncio.Event) -> None:
    ANIMATION_FRAMES = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']

    i = 0
    while not is_loaded.is_set():
        sys.stdout.write('\n')
        sys.stdout.write(
            f'\033[s\033[J\033[38;2;255;215;0m[{ANIMATION_FRAMES[i % len(ANIMATION_FRAMES)]}] {text}\033[0m\033[u\033[1A'
        )
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1

    sys.stdout.write('\r' + ' ' * (len(text) + 10) + '\r')
    sys.stdout.flush()


def display_banner(session_id: str) -> None:
    import os
    cwd = os.getcwd()
    print_formatted_text(HTML(BLUELAMP_BANNER), style=DEFAULT_STYLE)
    print_formatted_text('')
    print_formatted_text(HTML(f'<grey>ディレクトリ: {cwd}</grey>'))
    print_formatted_text('')


def display_welcome_message(message: str = '') -> None:
    print_formatted_text(
        HTML(f"<blue>{get_message('lets_start')}</blue>\n"), style=DEFAULT_STYLE
    )
    if message:
        print_formatted_text(
            HTML(f'{message} <grey>ヘルプは /help と入力してください</grey>'),
            style=DEFAULT_STYLE,
        )
    else:
        print_formatted_text(
            HTML(f'{get_message("build_prompt")} <grey>ヘルプは /help と入力してください</grey>'),
            style=DEFAULT_STYLE,
        )


def display_initial_user_prompt(prompt: str) -> None:
    print_formatted_text(
        FormattedText(
            [
                ('', '\n'),
                (COLOR_GOLD, '> '),
                ('', prompt),
            ]
        )
    )


# Prompt output display functions
def display_event(event: Event, config: OpenHandsConfig) -> None:
    global streaming_output_text_area
    with print_lock:
        if isinstance(event, Action):
            if hasattr(event, 'thought'):
                display_message(event.thought)
            if hasattr(event, 'final_thought'):
                display_message(event.final_thought)
        if isinstance(event, MessageAction):
            if event.source == EventSource.AGENT:
                display_message(event.content)

        if isinstance(event, CmdRunAction):
            # Only display the command if it's not already confirmed
            # Commands are always shown when AWAITING_CONFIRMATION, so we don't need to show them again when CONFIRMED
            if event.confirmation_state != ActionConfirmationStatus.CONFIRMED:
                display_command(event)

            if event.confirmation_state == ActionConfirmationStatus.CONFIRMED:
                initialize_streaming_output()
        elif isinstance(event, CmdOutputObservation):
            display_command_output(event.content)
        elif isinstance(event, FileEditObservation):
            display_file_edit(event)
        elif isinstance(event, FileReadObservation):
            display_file_read(event)
        elif isinstance(event, AgentStateChangedObservation):
            display_agent_state_change_message(event.agent_state)
        elif isinstance(event, ErrorObservation):
            display_error(event.content)


def display_message(message: str) -> None:
    message = message.strip()

    if message:
        print_formatted_text(f'\n{message}')


def display_error(error: str) -> None:
    error = error.strip()

    if error:
        container = Frame(
            TextArea(
                text=error,
                read_only=True,
                style='ansired',
                wrap_lines=True,
            ),
            title='Error',
            style='ansired',
        )
        print_formatted_text('')
        print_container(container)


def display_command(event: CmdRunAction) -> None:
    container = Frame(
        TextArea(
            text=f'$ {event.command}',
            read_only=True,
            style=COLOR_GREY,
            wrap_lines=True,
        ),
        title='Command',
        style='ansiblue',
    )
    print_formatted_text('')
    print_container(container)


def display_command_output(output: str) -> None:
    lines = output.split('\n')
    formatted_lines = []
    for line in lines:
        if line.startswith('[Python Interpreter') or line.startswith('openhands@'):
            # TODO: clean this up once we clean up terminal output
            continue
        formatted_lines.append(line)
        formatted_lines.append('\n')

    # Remove the last newline if it exists
    if formatted_lines:
        formatted_lines.pop()

    container = Frame(
        TextArea(
            text=''.join(formatted_lines),
            read_only=True,
            style=COLOR_GREY,
            wrap_lines=True,
        ),
        title='Command Output',
        style=f'fg:{COLOR_GREY}',
    )
    print_formatted_text('')
    print_container(container)


def display_file_edit(event: FileEditObservation) -> None:
    container = Frame(
        TextArea(
            text=event.visualize_diff(n_context_lines=4),
            read_only=True,
            wrap_lines=True,
            lexer=CustomDiffLexer(),
        ),
        title='File Edit',
        style=f'fg:{COLOR_GREY}',
    )
    print_formatted_text('')
    print_container(container)


def display_file_read(event: FileReadObservation) -> None:
    content = event.content.replace('\t', ' ')
    container = Frame(
        TextArea(
            text=content,
            read_only=True,
            style=COLOR_GREY,
            wrap_lines=True,
        ),
        title='File Read',
        style=f'fg:{COLOR_GREY}',
    )
    print_formatted_text('')
    print_container(container)


def initialize_streaming_output():
    """Initialize the streaming output TextArea."""
    if not ENABLE_STREAMING:
        return
    global streaming_output_text_area
    streaming_output_text_area = TextArea(
        text='',
        read_only=True,
        style=COLOR_GREY,
        wrap_lines=True,
    )
    container = Frame(
        streaming_output_text_area,
        title='Streaming Output',
        style=f'fg:{COLOR_GREY}',
    )
    print_formatted_text('')
    print_container(container)


def update_streaming_output(text: str):
    """Update the streaming output TextArea with new text."""
    global streaming_output_text_area

    # Append the new text to the existing content
    if streaming_output_text_area is not None:
        current_text = streaming_output_text_area.text
        streaming_output_text_area.text = current_text + text


# Interactive command output display functions
def display_help() -> None:
    # Version header and introduction
    print_formatted_text(
        HTML(
            f'\n<grey>OpenHands CLI v{__version__}</grey>\n'
            '<gold>OpenHands CLI lets you interact with the OpenHands agent from the command line.</gold>\n'
        )
    )

    # Usage examples
    print_formatted_text('Things that you can try:')
    print_formatted_text(
        HTML(
            '• Ask questions about the codebase <grey>> How does main.py work?</grey>\n'
            '• Edit files or add new features <grey>> Add a new function to ...</grey>\n'
            '• Find and fix issues <grey>> Fix the type error in ...</grey>\n'
        )
    )

    # Tips section
    print_formatted_text(
        'Some tips to get the most out of OpenHands:\n'
        '• Be as specific as possible about the desired outcome or the problem to be solved.\n'
        '• Provide context, including relevant file paths and line numbers if available.\n'
        '• Break large tasks into smaller, manageable prompts.\n'
        '• Include relevant error messages or logs.\n'
        '• Specify the programming language or framework, if not obvious.\n'
    )

    # Commands section
    print_formatted_text(HTML('Interactive commands:'))
    commands_html = ''
    for command, description in COMMANDS.items():
        commands_html += f'<gold><b>{command}</b></gold> - <grey>{description}</grey>\n'
    print_formatted_text(HTML(commands_html))

    # Footer
    print_formatted_text(
        HTML(
            '<grey>Learn more at: https://docs.all-hands.dev/usage/getting-started</grey>'
        )
    )


def display_usage_metrics(usage_metrics: UsageMetrics) -> None:
    cost_str = f'${usage_metrics.metrics.accumulated_cost:.6f}'
    input_tokens_str = (
        f'{usage_metrics.metrics.accumulated_token_usage.prompt_tokens:,}'
    )
    cache_read_str = (
        f'{usage_metrics.metrics.accumulated_token_usage.cache_read_tokens:,}'
    )
    cache_write_str = (
        f'{usage_metrics.metrics.accumulated_token_usage.cache_write_tokens:,}'
    )
    output_tokens_str = (
        f'{usage_metrics.metrics.accumulated_token_usage.completion_tokens:,}'
    )
    total_tokens_str = f'{usage_metrics.metrics.accumulated_token_usage.prompt_tokens + usage_metrics.metrics.accumulated_token_usage.completion_tokens:,}'

    labels_and_values = [
        ('   合計コスト (USD):', cost_str),
        ('', ''),
        ('   入力トークン数:', input_tokens_str),
        ('      キャッシュヒット:', cache_read_str),
        ('      キャッシュ書込:', cache_write_str),
        ('   出力トークン数:', output_tokens_str),
        ('', ''),
        ('   合計トークン数:', total_tokens_str),
    ]

    # Calculate max widths for alignment
    max_label_width = max(len(label) for label, _ in labels_and_values)
    max_value_width = max(len(value) for _, value in labels_and_values)

    # Construct the summary text with aligned columns
    summary_lines = [
        f'{label:<{max_label_width}} {value:<{max_value_width}}'
        for label, value in labels_and_values
    ]
    summary_text = '\n'.join(summary_lines)

    container = Frame(
        TextArea(
            text=summary_text,
            read_only=True,
            style=COLOR_GREY,
            wrap_lines=True,
        ),
        title='利用状況',
        style=f'fg:{COLOR_GREY}',
    )

    print_container(container)


def get_session_duration(session_init_time: float) -> str:
    current_time = time.time()
    session_duration = current_time - session_init_time
    hours, remainder = divmod(session_duration, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f'{int(hours)}h {int(minutes)}m {int(seconds)}s'


def display_shutdown_message(usage_metrics: UsageMetrics, session_id: str) -> None:
    duration_str = get_session_duration(usage_metrics.session_init_time)

    print_formatted_text(HTML('<grey>現在の会話を終了しています...</grey>'))
    print_formatted_text('')
    display_usage_metrics(usage_metrics)
    print_formatted_text('')
    print_formatted_text(HTML(f'<grey>会話時間: {duration_str}</grey>'))
    print_formatted_text('')
    print_formatted_text(HTML(f'<grey>会話を終了しました: {session_id}</grey>'))
    print_formatted_text('')


def display_status(usage_metrics: UsageMetrics, session_id: str) -> None:
    duration_str = get_session_duration(usage_metrics.session_init_time)

    print_formatted_text('')
    print_formatted_text(HTML(f'<grey>Conversation ID: {session_id}</grey>'))
    print_formatted_text(HTML(f'<grey>Uptime:          {duration_str}</grey>'))
    print_formatted_text('')
    display_usage_metrics(usage_metrics)


def display_agent_running_message() -> None:
    print_formatted_text('')
    print_formatted_text(
        HTML(f'<blue>{get_message("agent_running")}</blue> <grey>(Press Ctrl-P to pause)</grey>')
    )


def display_agent_state_change_message(agent_state: str) -> None:
    if agent_state == AgentState.PAUSED:
        print_formatted_text('')
        print_formatted_text(
            HTML(
                '<gold>Agent paused...</gold> <grey>(Enter /resume to continue)</grey>'
            )
        )
    elif agent_state == AgentState.FINISHED:
        print_formatted_text('')
        print_formatted_text(HTML(f'<blue>{get_message("agent_finished")}</blue>'))
    elif agent_state == AgentState.AWAITING_USER_INPUT:
        print_formatted_text('')
        print_formatted_text(HTML(f'<blue>{get_message("agent_waiting")}</blue>'))


async def prompt_for_api_key() -> str | None:
    """Prompt user for Portal API key."""
    kb = KeyBindings()
    
    @kb.add('c-c')
    def _(event: KeyPressEvent) -> None:
        """Handle Ctrl+C to cancel."""
        event.app.exit(exception=KeyboardInterrupt())
    
    try:
        session = PromptSession(
            key_bindings=kb,
            style=DEFAULT_STYLE,
        )
        api_key = await session.prompt_async(
            'APIキー: ',
            is_password=True,  # Hide the API key input
        )
        return api_key.strip() if api_key else None
    except (KeyboardInterrupt, EOFError):
        return None


# Common input functions
class CommandCompleter(Completer):
    """Custom completer for commands."""

    def __init__(self, agent_state: str) -> None:
        super().__init__()
        self.agent_state = agent_state

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Generator[Completion, None, None]:
        text = document.text_before_cursor.lstrip()
        if text.startswith('/'):
            available_commands = dict(COMMANDS)
            if self.agent_state != AgentState.PAUSED:
                available_commands.pop('/resume', None)

            for command, description in available_commands.items():
                if command.startswith(text):
                    yield Completion(
                        command,
                        start_position=-len(text),
                        display_meta=description,
                        style='bg:ansidarkgray fg:blue',
                    )


def create_prompt_session() -> PromptSession[str]:
    return PromptSession(style=DEFAULT_STYLE)


async def read_prompt_input(agent_state: str, multiline: bool = False) -> str:
    try:
        logger.info("CTRL+C_DEBUG: Starting prompt input")
        prompt_session = create_prompt_session()
        prompt_session.completer = (
            CommandCompleter(agent_state) if not multiline else None
        )

        if multiline:
            kb = KeyBindings()

            @kb.add('c-d')
            def _(event: KeyPressEvent) -> None:
                event.current_buffer.validate_and_handle()

            @kb.add('c-c')
            def _(event: KeyPressEvent) -> None:
                logger.info("CTRL+C_DEBUG: CTRL+C pressed in multiline input")
                event.app.exit(exception=KeyboardInterrupt())

            with patch_stdout():
                print_formatted_text('')
                message = await prompt_session.prompt_async(
                    HTML(
                        '<gold>Enter your message and press Ctrl-D to finish:</gold>\n'
                    ),
                    multiline=True,
                    key_bindings=kb,
                )
        else:
            kb = KeyBindings()
            
            @kb.add('c-c')
            def _(event: KeyPressEvent) -> None:
                logger.info("CTRL+C_DEBUG: CTRL+C pressed in single line input")
                event.app.exit(exception=KeyboardInterrupt())
            
            with patch_stdout():
                print_formatted_text('')
                message = await prompt_session.prompt_async(
                    HTML('<gold>> </gold>'),
                    key_bindings=kb,
                )
        logger.info("CTRL+C_DEBUG: Prompt input completed normally")
        return message if message is not None else ''
    except (KeyboardInterrupt, EOFError):
        logger.info("CTRL+C_DEBUG: KeyboardInterrupt/EOFError caught in read_prompt_input")
        return '/exit'


async def read_confirmation_input() -> str:
    try:
        logger.info("CTRL+C_DEBUG: Starting confirmation input")
        prompt_session = create_prompt_session()
        
        kb = KeyBindings()
        
        @kb.add('c-c')
        def _(event: KeyPressEvent) -> None:
            logger.info("CTRL+C_DEBUG: CTRL+C pressed in confirmation input")
            event.app.exit(exception=KeyboardInterrupt())

        with patch_stdout():
            print_formatted_text('')
            confirmation: str = await prompt_session.prompt_async(
                HTML('<gold>Proceed with action? (y)es/(n)o/(a)lways > </gold>'),
                key_bindings=kb,
            )

            confirmation = '' if confirmation is None else confirmation.strip().lower()

            if confirmation in ['y', 'yes']:
                return 'yes'
            elif confirmation in ['n', 'no']:
                return 'no'
            elif confirmation in ['a', 'always']:
                return 'always'
            else:
                return 'no'
    except (KeyboardInterrupt, EOFError):
        logger.info("CTRL+C_DEBUG: KeyboardInterrupt/EOFError caught in read_confirmation_input")
        return 'no'


async def read_agent_switch_confirmation(agent_name: str = '', task_completed: bool = True) -> str:
    """Read agent switch confirmation input from user.
    
    Args:
        agent_name: Name of the current agent
        task_completed: Whether the current task is completed
    
    Returns:
        'yes', 'no', or 'always'
    """
    try:
        logger.info("CTRL+C_DEBUG: Starting agent switch confirmation input")
        prompt_session = create_prompt_session()
        
        kb = KeyBindings()
        
        @kb.add('c-c')
        def _(event: KeyPressEvent) -> None:
            logger.info("CTRL+C_DEBUG: CTRL+C pressed in agent switch confirmation")
            event.app.exit(exception=KeyboardInterrupt())

        with patch_stdout():
            print_formatted_text('')
            
            # Create appropriate message based on context
            if task_completed and agent_name:
                message = f'{agent_name}のタスクが完了しました。オーケストレーターに戻りますか？'
            else:
                message = 'エージェントを切り替えますか？'
            
            confirmation: str = await prompt_session.prompt_async(
                HTML(f'<gold>{message} (h)はい/(i)いいえ/(t)つねに許可 > </gold>'),
                key_bindings=kb,
            )

            confirmation = '' if confirmation is None else confirmation.strip().lower()

            if confirmation in ['h', 'はい', 'y', 'yes']:
                return 'yes'
            elif confirmation in ['i', 'いいえ', 'n', 'no']:
                return 'no'
            elif confirmation in ['t', 'つねに', 'つねに許可', 'a', 'always']:
                return 'always'
            else:
                return 'no'
    except (KeyboardInterrupt, EOFError):
        logger.info("CTRL+C_DEBUG: KeyboardInterrupt/EOFError caught in read_agent_switch_confirmation")
        return 'no'


def log_agent_switch(from_agent: str, to_agent: str, reason: str = '', switch_type: str = 'delegate') -> None:
    """Log agent switch with visual formatting.
    
    Args:
        from_agent: Name of the agent being switched from
        to_agent: Name of the agent being switched to
        reason: Reason for the switch
        switch_type: Type of switch ('delegate', 'return', 'error')
    """
    try:
        # Determine the appropriate icon and color based on switch type
        if switch_type == 'delegate':
            icon = '🔄'
            color = 'blue'
            direction = '→'
        elif switch_type == 'return':
            icon = '🔄'
            color = 'green'
            direction = '←'
        elif switch_type == 'error':
            icon = '⚠️'
            color = 'red'
            direction = '→'
        else:
            icon = '🔄'
            color = 'gold'
            direction = '↔'
        
        # Format the main switch message
        switch_message = f'{icon} <{color}>エージェント切り替え</color>: {from_agent} {direction} {to_agent}'
        
        # Add reason if provided
        if reason:
            if switch_type == 'delegate':
                reason_icon = '📋'
            elif switch_type == 'return':
                reason_icon = '✅'
            elif switch_type == 'error':
                reason_icon = '❌'
            else:
                reason_icon = '📝'
            
            reason_message = f'{reason_icon} <{color}>理由</color>: {reason}'
        else:
            reason_message = ''
        
        # Print the formatted messages
        with patch_stdout():
            print_formatted_text('')
            print_formatted_text(HTML(switch_message))
            if reason_message:
                print_formatted_text(HTML(reason_message))
            print_formatted_text('')
            
    except Exception as e:
        # Fallback to simple logging if formatting fails
        logger.info(f'Agent switch: {from_agent} -> {to_agent} ({reason})')


async def process_agent_pause(done: asyncio.Event, event_stream: EventStream) -> None:
    logger.info("CTRL+C_DEBUG: Starting agent pause monitoring")
    input = create_input()

    def keys_ready() -> None:
        for key_press in input.read_keys():
            if (
                key_press.key == Keys.ControlP
                or key_press.key == Keys.ControlC
                or key_press.key == Keys.ControlD
                or key_press.key == Keys.Escape
            ):
                logger.info(f"CTRL+C_DEBUG: Control key pressed: {key_press.key}")
                print_formatted_text('')
                if key_press.key == Keys.ControlC:
                    print_formatted_text(HTML('<gold>Shutdown requested...</gold>'))
                    # Import the shutdown flag from main module
                    try:
                        from openhands.cli.main import _shutdown_requested
                        _shutdown_requested.set()
                        logger.info("CTRL+C_DEBUG: Shutdown flag set from process_agent_pause")
                    except ImportError:
                        logger.warning("CTRL+C_DEBUG: Could not import shutdown flag")
                elif key_press.key == Keys.Escape:
                    logger.info("ESC_INTERRUPT: ESC key pressed, requesting user interrupt")
                    # Import the interrupt handler
                    try:
                        from openhands.cli.interrupt_handler import request_user_interrupt
                        request_user_interrupt()
                        logger.info("ESC_INTERRUPT: User interrupt flag set from process_agent_pause")
                    except ImportError:
                        logger.warning("ESC_INTERRUPT: Could not import interrupt handler")
                else:
                    print_formatted_text(HTML('<gold>Pausing the agent...</gold>'))
                    event_stream.add_event(
                        ChangeAgentStateAction(AgentState.PAUSED),
                        EventSource.USER,
                    )
                done.set()

    with input.raw_mode():
        with input.attach(keys_ready):
            await done.wait()
    
    logger.info("CTRL+C_DEBUG: Agent pause monitoring ended")


def cli_confirm(
    question: str = 'Are you sure?', choices: list[str] | None = None
) -> int:
    """Display a confirmation prompt with the given question and choices.

    Returns the index of the selected choice.
    """
    if choices is None:
        choices = ['Yes', 'No']
    selected = [0]  # Using list to allow modification in closure

    def get_choice_text() -> list:
        return [
            ('class:question', f'{question}\n\n'),
        ] + [
            (
                'class:selected' if i == selected[0] else 'class:unselected',
                f'{"> " if i == selected[0] else "  "}{choice}\n',
            )
            for i, choice in enumerate(choices)
        ]

    kb = KeyBindings()

    @kb.add('up')
    def _(event: KeyPressEvent) -> None:
        selected[0] = (selected[0] - 1) % len(choices)

    @kb.add('down')
    def _(event: KeyPressEvent) -> None:
        selected[0] = (selected[0] + 1) % len(choices)

    @kb.add('enter')
    def _(event: KeyPressEvent) -> None:
        event.app.exit(result=selected[0])

    style = Style.from_dict({'selected': COLOR_GOLD, 'unselected': ''})

    layout = Layout(
        HSplit(
            [
                Window(
                    FormattedTextControl(get_choice_text),
                    always_hide_cursor=True,
                )
            ]
        )
    )

    app = Application(
        layout=layout,
        key_bindings=kb,
        style=style,
        mouse_support=True,
        full_screen=False,
    )

    return app.run(in_thread=True)


def kb_cancel() -> KeyBindings:
    """Custom key bindings to handle ESC as a user cancellation."""
    bindings = KeyBindings()

    @bindings.add('escape')
    def _(event: KeyPressEvent) -> None:
        event.app.exit(exception=UserCancelledError, style='class:aborting')

    return bindings


class UserCancelledError(Exception):
    """Raised when the user cancels an operation via key binding."""

    pass
