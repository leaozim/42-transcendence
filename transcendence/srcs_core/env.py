"""
Environment-driven configuration shared by the settings modules.

The project no longer depends on Docker: every external service is optional.

* Database: PostgreSQL is used when POSTGRES_HOST is set, otherwise a local
  SQLite file (SQLITE_PATH, default ``<project root>/data/db.sqlite3``).
* Channel layer: Redis is used when REDIS_URL is set, otherwise an in-memory
  layer. The in-memory layer only works when HTTP and WebSocket traffic are
  served by the same single process (which is what ``scripts/start.sh`` does).
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def env_list(name, default):
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return list(default)
    return [item.strip() for item in value.split(",") if item.strip()]


def database_config():
    if os.getenv("POSTGRES_HOST"):
        return {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_NAME"),
            "USER": os.getenv("POSTGRES_USER"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
            "HOST": os.getenv("POSTGRES_HOST"),
            "PORT": os.getenv("POSTGRES_PORT"),
        }

    sqlite_path = Path(os.getenv("SQLITE_PATH") or PROJECT_ROOT / "data" / "db.sqlite3")
    if not sqlite_path.is_absolute():
        sqlite_path = PROJECT_ROOT / sqlite_path
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    return {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(sqlite_path),
        # Game/chat consumers and HTTP views write concurrently; wait for locks
        # instead of failing immediately with "database is locked".
        "OPTIONS": {"timeout": 20},
    }


def media_root():
    """Directory for user uploads (avatars). Default: <project root>/data/media."""
    path = Path(os.getenv("MEDIA_ROOT") or PROJECT_ROOT / "data" / "media")
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return str(path)


def channel_layers_config():
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        return {
            "default": {
                "BACKEND": "channels_redis.core.RedisChannelLayer",
                "CONFIG": {"hosts": [redis_url]},
            }
        }
    return {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
