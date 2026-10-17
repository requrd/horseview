"""DBと接続するためのモジュール."""

import os
from collections.abc import Mapping
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class Base(DeclarativeBase, MappedAsDataclass):
    """公式推奨のベースクラス.

    Args:
        DeclarativeBase (_type_): _description_
        MappedAsDataclass (_type_): _description_

    """

    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


db = SQLAlchemy(model_class=Base)

if TYPE_CHECKING:
    from flask_sqlalchemy.model import Model as _FSAModel

    class Model(Base, _FSAModel):
        """型チェック用のdb.Model相当クラス."""

else:
    Model = db.Model

migrate = Migrate()


# プール内の接続がサーバー側で切断されていても(wait_timeout, DBの再起動など)
# 再接続できるよう、使用前に疎通確認する
DEFAULT_ENGINE_OPTIONS: Mapping[str, Any] = MappingProxyType({"pool_pre_ping": True})


def create_app(engine_options: Mapping[str, Any] | None = None) -> Flask:
    """DBとの接続を初期化する.

    Args:
        engine_options: create_engineに渡す設定. DEFAULT_ENGINE_OPTIONSを上書きする.

    """
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DB"]
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        **DEFAULT_ENGINE_OPTIONS,
        **(engine_options or {}),
    }
    db.init_app(app)
    migrate.init_app(app, db)
    return app
