"""DBを使わない(SQLiteインメモリで完結する)ユニットテスト."""

import dataclasses
from collections.abc import Iterator
from typing import Any

import pytest
from flask import Flask
from sqlalchemy import inspect
from sqlalchemy.orm import configure_mappers, joinedload

import jrdb_model
from jrdb_model import (
    BangumiData,
    KaisaiData,
    RacehorseData,
    SeisekiData,
    SeisekiRaceData,
    create_app,
    db,
)

_DUMMY_BY_TYPE: dict[type, Any] = {int: 0, float: 0.0, str: "", dict: {}}


def build[T](model: type[T], **values: Any) -> T:
    """必須の列をダミー値で埋めてモデルを生成する."""
    mapper = inspect(model)
    assert mapper is not None
    columns = mapper.columns
    for field in dataclasses.fields(model):  # type: ignore[arg-type]
        if field.name in values or not field.init:
            continue
        if (
            field.default is not dataclasses.MISSING
            or field.default_factory is not dataclasses.MISSING
        ):
            continue
        python_type = columns[field.name].type.python_type
        values[field.name] = _DUMMY_BY_TYPE[python_type]
    return model(**values)


@pytest.fixture
def app(monkeypatch: pytest.MonkeyPatch) -> Iterator[Flask]:
    """SQLiteインメモリDBに接続したアプリを返す."""
    monkeypatch.setenv("DB", "sqlite://")
    app = create_app()
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.engine.dispose()


def test_all_exports_exist():
    """__all__に挙げた名前がすべてimportできる."""
    missing = [name for name in jrdb_model.__all__ if not hasattr(jrdb_model, name)]
    assert missing == []


def test_mappers_configure():
    """全モデルのリレーションが解決できる."""
    configure_mappers()


def test_create_app_reads_db_from_env(monkeypatch: pytest.MonkeyPatch):
    """接続先は環境変数DBから読む."""
    monkeypatch.setenv("DB", "sqlite:///example.db")
    app = create_app()
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///example.db"


def test_create_app_requires_db_env(monkeypatch: pytest.MonkeyPatch):
    """環境変数DBがなければ起動しない."""
    monkeypatch.delenv("DB", raising=False)
    with pytest.raises(KeyError):
        create_app()


@pytest.mark.usefixtures("app")
def test_create_all_creates_every_table():
    """全モデルのテーブルが作成される."""
    tables = set(inspect(db.engine).get_table_names())
    assert tables == set(db.metadata.tables)
    assert {"kaisai", "bangumi", "racehorse", "seiseki"} <= tables


@pytest.mark.usefixtures("app")
def test_load_kaisai_with_nested_relations():
    """開催から出走馬の成績までジョインロードで辿れる."""
    kaisai = build(KaisaiData, kaisaikey="kaisai1", ymd=20220105)
    race = build(BangumiData, racekey="race1", kaisaikey="kaisai1", ymd=20220105)
    horse = build(RacehorseData, racehorsekey="horse1", racekey="race1")
    result = build(
        SeisekiData,
        racehorsekey="horse1",
        order_of_arrival=4,
        seisekirace=build(SeisekiRaceData, racekey="race1"),
    )
    db.session.add_all([kaisai, race, horse, result])
    db.session.commit()
    db.session.expunge_all()

    loaded = (
        KaisaiData.query.filter(KaisaiData.ymd >= 20220101)
        .options(joinedload(KaisaiData.races))
        .one()
    )
    racehorse = loaded.races[0].racehorses[0]
    assert racehorse.result.order_of_arrival == 4
    assert racehorse.bangumi.kaisai.kaisaikey == "kaisai1"


@pytest.mark.usefixtures("app")
def test_kaisai_split_into_two_days():
    """代替競馬では同じ開催キーの開催が日ごとに別の行になり、レースも日ごとに分かれる."""
    db.session.add_all(
        [
            build(KaisaiData, kaisaikey="062032", ymd=20200329, precipitation=5.5),
            build(KaisaiData, kaisaikey="062032", ymd=20200331, precipitation=0.0),
            build(BangumiData, racekey="06203201", kaisaikey="062032", ymd=20200329),
            build(BangumiData, racekey="06203203", kaisaikey="062032", ymd=20200331),
        ]
    )
    db.session.commit()
    db.session.expunge_all()

    loaded = {
        kaisai.ymd: kaisai
        for kaisai in KaisaiData.query.options(joinedload(KaisaiData.races)).all()
    }
    assert [race.racekey for race in loaded[20200329].races] == ["06203201"]
    assert [race.racekey for race in loaded[20200331].races] == ["06203203"]
    assert loaded[20200329].precipitation == 5.5


@pytest.mark.usefixtures("app")
def test_decimal_columns_keep_fraction():
    """小数の列は小数点以下を保つ."""
    db.session.add_all(
        [
            build(KaisaiData, kaisaikey="kaisai1", ymd=20220105, turf_length=12.5),
            build(BangumiData, racekey="race1", kaisaikey="kaisai1", ymd=20220105),
            build(RacehorseData, racehorsekey="horse1", racekey="race1"),
            build(
                SeisekiData,
                racehorsekey="horse1",
                this_money=55.5,
                seisekirace=build(SeisekiRaceData, racekey="race1"),
            ),
        ]
    )
    db.session.commit()
    db.session.expunge_all()

    assert db.session.get(KaisaiData, ("kaisai1", 20220105)).turf_length == 12.5
    assert db.session.get(SeisekiData, "horse1").this_money == 55.5


@pytest.mark.parametrize(
    ("model", "name", "columns"),
    [
        (RacehorseData, "ix_racehorse_racekey", ["racekey"]),
        (RacehorseData, "ix_racehorse_blood", ["blood"]),
        (SeisekiData, "ix_seiseki_racekey", ["racekey"]),
        (BangumiData, "ix_bangumi_kaisaikey_ymd", ["kaisaikey", "ymd"]),
    ],
)
def test_foreign_keys_have_indexes(model: Any, name: str, columns: list[str]) -> None:
    """外部キーの列に索引がある(Postgresは外部キーに自動で索引を作らない)."""
    indexes = {index.name: index for index in model.__table__.indexes}
    assert [column.name for column in indexes[name].columns] == columns
