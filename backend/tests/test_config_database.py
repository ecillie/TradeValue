"""Tests for app/database.py and targeted app/config.py reload (else branch, docker host)."""
import importlib
import os
from unittest.mock import patch

import app.config
from app.database import Base, engine, get_db, init_db


class TestConfigReload:
    def test_database_url_without_password_branch(self, monkeypatch):
        """Line 35: else branch when DB_PASSWORD is unset (dotenv must not re-inject it)."""
        monkeypatch.setenv("DB_USER", "u")
        monkeypatch.setenv("DB_NAME", "n")
        monkeypatch.setenv("DB_HOST", "localhost")
        monkeypatch.setenv("DB_PORT", "5432")
        monkeypatch.delenv("DB_PASSWORD", raising=False)

        # Must delegate to the real getenv captured *before* patching os.getenv — otherwise
        # os.getenv inside the side_effect is the mock and we recurse or read wrong values.
        _real_getenv = os.getenv

        def getenv_no_db_password(key, default=None):
            if key == "DB_PASSWORD":
                return None
            return _real_getenv(key, default)

        # load_dotenv() merges backend/.env; getenv patch forces no password for this reload.
        with patch("app.config.load_dotenv"):
            with patch("os.getenv", side_effect=getenv_no_db_password):
                importlib.reload(app.config)
        try:
            assert app.config.DATABASE_URL == "postgresql+psycopg2://u@localhost:5432/n"
        finally:
            monkeypatch.setenv("DB_USER", "test")
            monkeypatch.setenv("DB_NAME", "test")
            monkeypatch.setenv("DB_PASSWORD", "test")
            importlib.reload(app.config)

    def test_db_host_unchanged_when_running_inside_docker(self, monkeypatch):
        monkeypatch.setenv("DB_USER", "u")
        monkeypatch.setenv("DB_NAME", "n")
        monkeypatch.setenv("DB_PASSWORD", "p")
        monkeypatch.setenv("DB_HOST", "host.docker.internal")
        monkeypatch.setattr(
            "app.config.os.path.exists",
            lambda path: path == "/.dockerenv",
        )
        importlib.reload(app.config)
        try:
            assert app.config.DB_HOST == "host.docker.internal"
        finally:
            monkeypatch.setenv("DB_HOST", "localhost")
            importlib.reload(app.config)


class TestDatabase:
    def test_get_db_yields_and_closes_session(self):
        gen = get_db()
        session = next(gen)
        assert session is not None
        gen.close()

    @patch("app.database.Base.metadata.create_all")
    def test_init_db_calls_create_all(self, mock_create_all):
        init_db()
        mock_create_all.assert_called_once_with(bind=engine)
