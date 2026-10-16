"""マスターコード."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from ..sessioncontroll import Model


class BacodeMaster(Model):
    """場コードマスタ."""

    __tablename__ = "bacodemaster"
    bacode: Mapped[int] = mapped_column(primary_key=True)
    baname: Mapped[str] = mapped_column(String(255))


class JuryoMaster(Model):
    """重量マスタ."""

    __tablename__ = "juryomaster"
    juryo: Mapped[int] = mapped_column(primary_key=True)
    juryo_name: Mapped[str] = mapped_column(String(255))


class JokenMaster(Model):
    """条件マスタ."""

    __tablename__ = "jokenmaster"
    joken: Mapped[str] = mapped_column(String(255), primary_key=True)
    joken_group: Mapped[int] = mapped_column()
    joken_name: Mapped[str] = mapped_column(String(255))


class JokenGroupMaster(Model):
    """条件グループマスタ."""

    __tablename__ = "jokengroupmaster"
    joken_group: Mapped[int] = mapped_column(primary_key=True)
    joken_group_name: Mapped[str] = mapped_column(String(255))


class ShubetsuMaster(Model):
    """競走種別マスタ."""

    __tablename__ = "shubetsumaster"
    shubetsu: Mapped[int] = mapped_column(primary_key=True)
    shubetsu_name: Mapped[str] = mapped_column(String(255))


class IjokbnMaster(Model):
    """異常区分マスタ."""

    __tablename__ = "ijokbnmaster"
    ijo_kbn: Mapped[int] = mapped_column(primary_key=True)
    ijo_kbn_name: Mapped[str] = mapped_column(String(255))


class TenkoMaster(Model):
    """天候マスタ."""

    __tablename__ = "tenkomaster"
    tenko: Mapped[int] = mapped_column(primary_key=True)
    tenko_name: Mapped[str] = mapped_column(String(255))


class RestreasoncodeMaster(Model):
    """休養理由コードマスタ."""

    __tablename__ = "restreasoncodemaster"
    rest_reason_code: Mapped[int] = mapped_column(primary_key=True)
    rest_reason_name: Mapped[str] = mapped_column(String(255))


class LegtypeMaster(Model):
    """脚質マスタ."""

    __tablename__ = "legtypemaster"
    leg_type: Mapped[int] = mapped_column(primary_key=True)
    race_leg_type: Mapped[str] = mapped_column(String(255))
    leg_type_name: Mapped[str] = mapped_column(String(255))


class DistanceadjustMaster(Model):
    """距離適性マスタ."""

    __tablename__ = "distanceadjustmaster"
    distance_adjust: Mapped[int] = mapped_column(primary_key=True)
    distance_name: Mapped[str] = mapped_column(String(255))
