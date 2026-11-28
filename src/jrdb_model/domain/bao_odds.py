"""馬王のオッズデータ(三連単・馬単).

馬王の表(O6 の 三連単オッズT、O6-OLD の 三連単オッズT_OLD、O4 の 馬単オッズT)と
1対1の写し. 1行 = 1レース. 全オッズは源の文字列のまま持ち、組み合わせごとには分けない.
レースは馬王の競走コードで識別し、JRDB の racekey には結び付けない(bangumi への外部キーも無い).
"""

from datetime import datetime

from sqlalchemy import SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..sessioncontroll import Model


class BaoOddsColumns(Model):
    """馬王のオッズの表に共通の列.

    列とその並びは馬王の表の列(データ区分・データ作成年月日・競走コード・発表時刻・登録頭数・
    出走頭数・発売フラグ・全オッズ・票数合計)と同じ. 競走コードのほかは NULL を許す
    (データ区分が空の行は、ほかの列もすべて空).
    """

    __abstract__ = True

    data_kbn: Mapped[str | None] = mapped_column(String(1), default=None)
    data_created_at: Mapped[datetime | None] = mapped_column(default=None)
    # 主キー. 馬王の並び(3番目)に置くため、既定値の無い項目をキーワードで渡す
    race_code: Mapped[str] = mapped_column(String(11), primary_key=True, kw_only=True)
    announced_at: Mapped[datetime | None] = mapped_column(default=None)
    registered_horses: Mapped[int | None] = mapped_column(SmallInteger, default=None)
    ran_horses: Mapped[int | None] = mapped_column(SmallInteger, default=None)
    sold_flg: Mapped[int | None] = mapped_column(SmallInteger, default=None)
    odds: Mapped[str | None] = mapped_column(Text, default=None)
    votes: Mapped[int | None] = mapped_column(default=None)


class SanrentanOddsData(BaoOddsColumns):
    """三連単オッズ(馬王 BaoZ-O6.mdb の 三連単オッズT. JRA は 2015年〜)."""

    __tablename__ = "sanrentan_odds"


class SanrentanOddsOldData(BaoOddsColumns):
    """三連単オッズ(馬王 BaoZ-O6-OLD.mdb の 三連単オッズT_OLD. JRA は 2010〜2014年)."""

    __tablename__ = "sanrentan_odds_old"


class UmatanOddsData(BaoOddsColumns):
    """馬単オッズ(馬王 BaoZ-O4.mdb の 馬単オッズT)."""

    __tablename__ = "umatan_odds"
