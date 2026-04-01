# app/config.py
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from backend/.env
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)


def _resolve_db_host() -> str:
    """
    host.docker.internal resolves inside Docker (to reach Postgres on the host machine).
    When running Python on the host (no /.dockerenv), that hostname fails — use localhost.
    """
    host = os.getenv("DB_HOST", "localhost")
    if host in ("host.docker.internal", "docker.for.mac.localhost"):
        if not os.path.exists("/.dockerenv"):
            return "localhost"
    return host


DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASSWORD")
DB_HOST = _resolve_db_host()
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

if not DB_USER or not DB_NAME:  # pragma: no cover
    raise RuntimeError("DB_USER or DB_NAME missing from .env")

if DB_PASS:
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}"



