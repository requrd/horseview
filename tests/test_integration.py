"""DBと接続する統合テスト.

接続先は環境変数DBで指定する. 未設定の場合はスキップする.
例: DB=mariadb+pymysql://user:pass@host/database uv run pytest
"""

import os
from typing import List

import pytest
from sqlalchemy.orm import joinedload

from jrdb_model import KaisaiData, create_app

pytestmark = pytest.mark.skipif(
    "DB" not in os.environ, reason="環境変数DBが設定されていない"
)


def test_kaisai():
    """開催データのジョインロードのテスト."""
    app = create_app()
    kaisais: List[KaisaiData]
    with app.app_context():
        kaisais = (
            KaisaiData.query.filter(
                KaisaiData.ymd >= 20220101, KaisaiData.ymd <= 20220130
            )
            .options(joinedload("*"))
            .all()
        )
    assert len(kaisais) == 26
    assert kaisais[0].races[0].racehorses[0].result.order_of_arrival == 4
