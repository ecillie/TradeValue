# app/config.py
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from backend/.env
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASSWORD") 
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

if not DB_USER or not DB_NAME:
    raise RuntimeError("DB_USER or DB_NAME missing from .env")

if DB_PASS:
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}"



