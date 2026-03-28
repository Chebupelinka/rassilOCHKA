import json
import hashlib
import os
import sys
from base64 import urlsafe_b64encode
from cryptography.fernet import Fernet
from typing import Optional, Dict

class ConfigManager:
    @staticmethod
    def _get_config_path() -> str:
        """Возвращает путь к config.enc рядом с exe или в папке проекта"""
        if getattr(sys, 'frozen', False):
            base = os.path.dirname(sys.executable)
        else:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base, "config.enc")

    @staticmethod
    def _derive_key(master_password: str) -> bytes:
        return hashlib.sha256(master_password.encode()).digest()

    @staticmethod
    def _get_fernet(master_password: str) -> Fernet:
        key = urlsafe_b64encode(ConfigManager._derive_key(master_password))
        return Fernet(key)

    @staticmethod
    def save_config(master_password: str, sender_email: str, app_password: str):
        data = {
            "sender": sender_email,
            "app_password": app_password,
            "master_hash": hashlib.sha256(master_password.encode()).hexdigest()
        }
        json_str = json.dumps(data)
        fernet = ConfigManager._get_fernet(master_password)
        encrypted = fernet.encrypt(json_str.encode())
        with open(ConfigManager._get_config_path(), "wb") as f:
            f.write(encrypted)

    @staticmethod
    def load_config(master_password: str) -> Optional[Dict[str, str]]:
        path = ConfigManager._get_config_path()
        if not os.path.exists(path):
            return None
        try:
            with open(path, "rb") as f:
                encrypted = f.read()
            fernet = ConfigManager._get_fernet(master_password)
            decrypted = fernet.decrypt(encrypted)
            data = json.loads(decrypted)
            if data.get("master_hash") != hashlib.sha256(master_password.encode()).hexdigest():
                return None
            return data
        except Exception:
            return None

    @staticmethod
    def is_configured() -> bool:
        return os.path.exists(ConfigManager._get_config_path())