"""create_appのエンジン設定のテスト.

MySQLサーバーを用意せずに検証するため、SQLiteのファイルDBを利用する.
"""

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest
from flask import Flask
from sqlalchemy import Engine, text
from sqlalchemy.exc import DBAPIError

from jrdb_model import create_app, db
from jrdb_model.sessioncontroll import DEFAULT_ENGINE_OPTIONS


@pytest.fixture(autouse=True)
def database_uri(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> str:
    """接続先を一時ディレクトリのSQLiteにする."""
    uri = f"sqlite:///{tmp_path / 'test.db'}"
    monkeypatch.setenv("DB", uri)
    return uri


@contextmanager
def engine_of(app: Flask) -> Iterator[Engine]:
    """アプリのエンジンを提供し、終了時に破棄する."""
    with app.app_context():
        try:
            yield db.engine
        finally:
            db.session.remove()
            db.engine.dispose()


def close_pooled_connection(engine: Engine) -> None:
    """プール内の接続をサーバー側で切断された状態にする."""
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
        dbapi_connection = conn.connection.dbapi_connection
    # プールへ返却した後に切断する
    assert dbapi_connection is not None
    dbapi_connection.close()


def test_pre_ping_is_enabled_by_default():
    """既定でpool_pre_pingが有効になる."""
    app = create_app()

    assert app.config["SQLALCHEMY_ENGINE_OPTIONS"] == {"pool_pre_ping": True}
    with engine_of(app) as engine:
        assert engine.pool._pre_ping is True


def test_engine_options_override_defaults():
    """引数の設定が既定値を上書きし、既定値自体は変わらない."""
    app = create_app({"pool_pre_ping": False, "pool_recycle": 3600})

    assert app.config["SQLALCHEMY_ENGINE_OPTIONS"] == {
        "pool_pre_ping": False,
        "pool_recycle": 3600,
    }
    assert DEFAULT_ENGINE_OPTIONS == {"pool_pre_ping": True}
    with engine_of(app) as engine:
        assert engine.pool._pre_ping is False
        assert engine.pool._recycle == 3600


def test_reconnects_after_server_side_disconnect():
    """プール内の接続が切断されていても、再接続してクエリを実行できる."""
    app = create_app()

    with engine_of(app) as engine:
        close_pooled_connection(engine)

        assert db.session.scalar(text("SELECT 1")) == 1


def test_fails_after_server_side_disconnect_without_pre_ping():
    """pre_pingを無効にすると切断済みの接続を再利用して失敗する.

    上のテストが設定の効果を検証できていることを確認する.
    """
    app = create_app({"pool_pre_ping": False})

    with engine_of(app) as engine:
        close_pooled_connection(engine)

        with pytest.raises(DBAPIError):
            db.session.scalar(text("SELECT 1"))
