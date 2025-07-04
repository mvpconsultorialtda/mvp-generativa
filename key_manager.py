import os
import json
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from threading import Lock

WAITING_LIST_FILE = 'waiting_list.json'
LOG_FILE = 'key_rotation.log'
lock = Lock()

class KeyManager:
    def __init__(self, key_type: str, total_keys: int = 50):
        self.key_type = key_type  # 'TEXT_KEY' ou 'IMAGE_KEY'
        self.total_keys = total_keys
        self.keys = self._load_keys()
        self.waiting_list = self._load_waiting_list()

    def _load_keys(self) -> List[Tuple[str, str]]:
        keys = []
        for i in range(1, self.total_keys + 1):
            env_key = f'{self.key_type}_{i}'
            value = os.getenv(env_key, '')
            # Redundância: só adiciona se existir e não for vazio
            if value is not None and value.strip() != '':
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

    def get_next_key(self) -> Optional[Tuple[str, str]]:
        with lock:
            self._clean_waiting_list()
            # Redundância: filtra apenas chaves realmente válidas
            available_keys = [k for k in self.keys if k[0] not in self.waiting_list and k[1] and k[1].strip() != '']
            if not available_keys:
                # Todas as chaves estão na waiting list ou não existem válidas, resetar
                self._log('Todas as chaves bloqueadas ou inválidas. Reiniciando waiting list.')
                self.waiting_list = {}
                self._save_waiting_list()
                # Recarrega as chaves do .env após reset
                self.keys = self._load_keys()
                available_keys = [k for k in self.keys if k[1] and k[1].strip() != '']
                if not available_keys:
                    # Nenhuma chave válida disponível
                    return None
                return available_keys[0]
            return available_keys[0]

    def block_key(self, key_name: str):
        with lock:
            self.waiting_list[key_name] = datetime.now().isoformat()
            self._save_waiting_list()

# Uso:
# key_manager = KeyManager('TEXT_KEY')
# key, value = key_manager.get_next_key()
# ...
# key_manager.block_key(key)
