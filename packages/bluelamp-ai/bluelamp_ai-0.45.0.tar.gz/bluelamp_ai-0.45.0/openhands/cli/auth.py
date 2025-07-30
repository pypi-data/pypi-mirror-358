"""
Portal認証機能を提供するモジュール

このモジュールは、BlueLamp CLIとPortalの認証連携を管理します。
APIキーの保存、読み込み、検証機能を提供します。
"""
import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import aiohttp
import asyncio
from datetime import datetime

logger = logging.getLogger('bluelamp.cli.auth')


class PortalAuthenticator:
    """Portal認証を管理するクラス"""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Args:
            base_url: PortalのベースURL（例: https://portal.example.com/api）
        """
        self.base_url = base_url or os.getenv("PORTAL_BASE_URL", "https://bluelamp-235426778039.asia-northeast1.run.app/api")
        self.auth_file = Path.home() / ".config" / "bluelamp" / "auth.json"
        self.api_key: Optional[str] = None
        self.user_info: Optional[Dict[str, Any]] = None
        self._last_check: Optional[datetime] = None
        
    def _ensure_config_dir(self):
        """設定ディレクトリが存在することを確認"""
        self.auth_file.parent.mkdir(parents=True, exist_ok=True)
        
    def save_api_key(self, api_key: str) -> None:
        """
        APIキーをファイルに保存
        
        Args:
            api_key: 保存するAPIキー
        """
        self._ensure_config_dir()
        
        # APIキーの形式を検証
        if not self._validate_api_key_format(api_key):
            raise ValueError("Invalid API key format. Must start with 'CLI_' and be 68 characters long.")
        
        auth_data = {
            "api_key": api_key,
            "saved_at": datetime.now().isoformat()
        }
        
        # ファイルに保存（パーミッションを制限）
        with open(self.auth_file, 'w') as f:
            json.dump(auth_data, f, indent=2)
        
        # ファイルのパーミッションを600に設定（所有者のみ読み書き可能）
        os.chmod(self.auth_file, 0o600)
        
        self.api_key = api_key
        logger.info("API key saved successfully")
        
    def load_api_key(self) -> Optional[str]:
        """
        保存されたAPIキーを読み込む
        
        Returns:
            APIキー（存在しない場合はNone）
        """
        if not self.auth_file.exists():
            logger.debug("Auth file not found")
            return None
            
        try:
            with open(self.auth_file, 'r') as f:
                auth_data = json.load(f)
                api_key = auth_data.get("api_key")
                
                if api_key and self._validate_api_key_format(api_key):
                    self.api_key = api_key
                    logger.debug("API key loaded successfully")
                    return api_key
                else:
                    logger.warning("Invalid API key format in auth file")
                    return None
                    
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load auth file: {e}")
            return None
            
    def _validate_api_key_format(self, api_key: str) -> bool:
        """
        APIキーの形式を検証
        
        Args:
            api_key: 検証するAPIキー
            
        Returns:
            形式が正しい場合True
        """
        if not api_key:
            return False
            
        # CLI_で始まり、全体で68文字
        if not api_key.startswith("CLI_"):
            return False
            
        if len(api_key) != 68:
            return False
            
        # CLI_の後は16進数文字列（小文字）
        hex_part = api_key[4:]
        try:
            int(hex_part, 16)
            return hex_part == hex_part.lower()
        except ValueError:
            return False
            
    async def verify_api_key(self, api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        APIキーを検証
        
        Args:
            api_key: 検証するAPIキー（省略時は保存済みのキーを使用）
            
        Returns:
            検証結果の辞書
            
        Raises:
            aiohttp.ClientError: ネットワークエラー
            ValueError: APIキーが無効
        """
        if api_key is None:
            api_key = self.api_key
            
        if not api_key:
            raise ValueError("No API key provided")
            
        url = f"{self.base_url}/simple/auth/cli-verify"
        headers = {"X-API-Key": api_key}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=headers) as response:
                    data = await response.json()
                    
                    if response.status == 200:
                        self.user_info = data.get("user")
                        self._last_check = datetime.now()
                        logger.info(f"Authentication successful for user: {self.user_info.get('name')}")
                        return data
                        
                    elif response.status == 401:
                        error_msg = data.get("error", "Invalid API key")
                        logger.error(f"Authentication failed: {error_msg}")
                        raise ValueError(f"Authentication failed: {error_msg}")
                        
                    elif response.status == 403:
                        error_msg = data.get("error", "User is disabled")
                        logger.error(f"Access forbidden: {error_msg}")
                        raise ValueError(f"Access forbidden: {error_msg}")
                        
                    else:
                        logger.error(f"Unexpected response status: {response.status}")
                        raise ValueError(f"Unexpected response status: {response.status}")
                        
            except aiohttp.ClientError as e:
                logger.error(f"Network error during authentication: {e}")
                raise
                
    def clear_auth(self) -> None:
        """認証情報をクリア"""
        if self.auth_file.exists():
            self.auth_file.unlink()
            
        self.api_key = None
        self.user_info = None
        self._last_check = None
        logger.info("Authentication cleared")
        
    def is_authenticated(self) -> bool:
        """
        認証済みかどうかを確認
        
        Returns:
            認証済みの場合True
        """
        return self.api_key is not None and self.user_info is not None
        
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """
        ユーザー情報を取得
        
        Returns:
            ユーザー情報の辞書（未認証の場合None）
        """
        return self.user_info


# シングルトンインスタンス
_authenticator: Optional[PortalAuthenticator] = None


def get_authenticator(base_url: Optional[str] = None) -> PortalAuthenticator:
    """
    認証インスタンスを取得（シングルトン）
    
    Args:
        base_url: PortalのベースURL
        
    Returns:
        PortalAuthenticatorインスタンス
    """
    global _authenticator
    if _authenticator is None:
        _authenticator = PortalAuthenticator(base_url)
    return _authenticator