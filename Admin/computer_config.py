"""Konfigurasi lokasi database untuk komputer utama dan komputer kasir."""

import json
from pathlib import Path


ADMIN_DIR = Path(__file__).resolve().parent
CONFIG_PATH = ADMIN_DIR / "computer.json"
DEFAULT_DATABASE = ADMIN_DIR / "toko.db"


def load_computer_config():
    default = {"mode": "utama", "database_path": str(DEFAULT_DATABASE)}
    if not CONFIG_PATH.is_file():
        return default
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        if data.get("mode") not in ("utama", "kasir"):
            return default
        return {**default, **data}
    except (OSError, ValueError, TypeError):
        return default


def get_database_path():
    config = load_computer_config()
    path = Path(config.get("database_path") or DEFAULT_DATABASE)
    return path.expanduser().resolve()


def save_computer_config(mode, database_path):
    if mode not in ("utama", "kasir"):
        raise ValueError("Mode komputer tidak valid")
    path = Path(database_path).expanduser().resolve()
    CONFIG_PATH.write_text(
        json.dumps({"mode": mode, "database_path": str(path)}, indent=2),
        encoding="utf-8",
    )
    return path
