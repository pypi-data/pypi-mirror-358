import json
import os
from .crypto import encrypt, decrypt

VAULT_FILE = "vault.json"

def load_vault(password: str) -> dict:
    if not os.path.exists(VAULT_FILE):
        return {}
    with open(VAULT_FILE, "r") as f:
        encrypted = json.load(f)
    try:
        decrypted = decrypt(encrypted, password)
        return json.loads(decrypted)
    except Exception:
        return {}

def save_vault(vault: dict, password: str):
    content = json.dumps(vault)
    encrypted = encrypt(content, password)
    with open(VAULT_FILE, "w") as f:
        json.dump(encrypted, f, indent=2)

def add_secret(name: str, secret: str, password: str):
    vault = load_vault(password)
    vault[name] = secret
    save_vault(vault, password)

def get_secret(name: str, password: str) -> str:
    vault = load_vault(password)
    return vault.get(name)

def delete_secret(name: str, password: str) -> bool:
    vault = load_vault(password)
    if name in vault:
        del vault[name]
        save_vault(vault, password)
        return True
    return False

def list_secrets(password: str) -> list[str]:
    vault = load_vault(password)
    return list(vault.keys())
