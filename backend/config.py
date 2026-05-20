"""Cross-platform config storage for the desktop app."""
import os
import json
import sys
from pathlib import Path


def get_app_data_dir() -> Path:
    """Returns the per-user app data directory for MindSphere."""
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    elif sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:  # linux
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))

    app_dir = base / "MindSphere"
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


CONFIG_PATH = get_app_data_dir() / "config.json"
DB_PATH = get_app_data_dir() / "mindsphere.db"


def load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text())
        except Exception:
            return {}
    return {}


def save_config(cfg: dict) -> None:
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2))


def get_api_key() -> str | None:
    # Priority: env var (dev mode) > config file (installed app)
    env_key = os.environ.get("GEMINI_API_KEY")
    if env_key:
        return env_key

    # Also try .env file for backward compatibility (dev mode)
    try:
        from dotenv import load_dotenv
        env_file = Path(__file__).parent.parent / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            env_key = os.environ.get("GEMINI_API_KEY")
            if env_key:
                return env_key
    except ImportError:
        pass

    return load_config().get("gemini_api_key")


def set_api_key(key: str) -> None:
    cfg = load_config()
    cfg["gemini_api_key"] = key.strip()
    save_config(cfg)


def has_api_key() -> bool:
    return bool(get_api_key())