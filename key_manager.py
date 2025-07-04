import os
import json
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Dict, Any
from threading import Lock

WAITING_LIST_FILE = 'waiting_list.json'
LOG_FILE = 'key_rotation.log'
lock = Lock()

class KeyManager:
    def __init__(self, key_type: str, total_keys: int = 50):
        self.key_type = key_type  # Ex: 'MISTRALAI_MISTRAL_7B_INSTRUCT_FREE_KEY', 'BING_AUTH_COOKIE'
        self.total_keys = total_keys
        self.keys = self._load_keys()
        self.waiting_list = self._load_waiting_list()

    def _load_keys(self) -> List[Any]:
        keys = []
        if self.key_type.startswith('BING_AUTH_COOKIE'):
            # Para Bing, rotaciona pares de cookies
            for i in range(1, self.total_keys + 1):
                cookie1 = os.getenv(f'BING_AUTH_COOKIE_{i}', '').strip()
                cookie2 = os.getenv(f'BING_AUTH_COOKIE_SRCHHPGUSR_{i}', '').strip()
                if cookie1 and cookie2:
                    keys.append((f'BING_AUTH_COOKIE_{i}', cookie1, f'BING_AUTH_COOKIE_SRCHHPGUSR_{i}', cookie2))
        else:
            # Para texto, rotaciona chaves individuais
            for i in range(1, self.total_keys + 1):
                env_key = f'{self.key_type}_{i}'
                value = os.getenv(env_key, '').strip()
                if value:
                    keys.append((env_key, value))
        return keys

    def _load_waiting_list(self) -> dict:
        if not os.path.exists(WAITING_LIST_FILE):
            return {}
        with open(WAITING_LIST_FILE, 'r') as f:
            return json.load(f)

    def _save_waiting_list(self):
        with open(WAITING_LIST_FILE, 'w') as f:
            json.dump(self.waiting_list, f, indent=2)

    def _log(self, message: str):
        with open(LOG_FILE, 'a') as f:
            f.write(f'{datetime.now().isoformat()} - {message}\n')

    def _clean_waiting_list(self):
        now = datetime.now()
        changed = False
        for key in list(self.waiting_list.keys()):
            dt = datetime.fromisoformat(self.waiting_list[key])
            if now - dt > timedelta(hours=24):
                del self.waiting_list[key]
                changed = True
        if changed:
            self._save_waiting_list()

    def get_next_key(self) -> Optional[Any]:
        with lock:
            self._clean_waiting_list()
            if self.key_type.startswith('BING_AUTH_COOKIE'):
                available_keys = [k for k in self.keys if k[0] not in self.waiting_list and k[2] not in self.waiting_list]
            else:
                available_keys = [k for k in self.keys if k[0] not in self.waiting_list]
            if not available_keys:
                self._log('Todas as chaves bloqueadas ou inválidas. Reiniciando waiting list.')
                self.waiting_list = {}
                self._save_waiting_list()
                self.keys = self._load_keys()
                if self.key_type.startswith('BING_AUTH_COOKIE'):
                    available_keys = [k for k in self.keys if k[0] not in self.waiting_list and k[2] not in self.waiting_list]
                else:
                    available_keys = [k for k in self.keys if k[0] not in self.waiting_list]
                if not available_keys:
                    return None
                return available_keys[0]
            return available_keys[0]

    def block_key(self, key_name: str):
        with lock:
            self.waiting_list[key_name] = datetime.now().isoformat()
            self._save_waiting_list()

# Exemplo de uso para texto:
# key_manager = KeyManager('MISTRALAI_MISTRAL_7B_INSTRUCT_FREE_KEY')
# key_name, key_value = key_manager.get_next_key()
#
# Exemplo de uso para imagem (Bing):
# key_manager = KeyManager('BING_AUTH_COOKIE')
# cookie1_name, cookie1, cookie2_name, cookie2 = key_manager.get_next_key()
