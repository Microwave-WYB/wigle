from datetime import date, datetime
from typing import Literal

from pydantic import Field, field_serializer, field_validator

from wigle.core import Query, endpoint
from wigle.schemas import BluetoothSearchResponse, NetSearchResponse

__all__ = ["BluetoothSearch", "BluetoothDetail"]


@endpoint("GET", "https://api.wigle.net/api/v2/network/detail", NetSearchResponse)
class BluetoothDetail(Query[NetSearchResponse]):
    netId: str | None = None
    reverseAddress: str | None = None


@endpoint("GET", "https://api.wigle.net/api/v2/bluetooth/search", BluetoothSearchResponse)
class BluetoothSearch(Query[BluetoothSearchResponse]):
    onlymine: Literal["true", "false"] | None = None
    notmine: Literal["true", "false"] | None = None
    latrange1: float | None = Field(default=None, ge=-90, le=90)
    latrange2: float | None = Field(default=None, ge=-90, le=90)
    longrange1: float | None = Field(default=None, ge=-180, le=180)
    longrange2: float | None = Field(default=None, ge=-180, le=180)
    closestLat: float | None = Field(default=None, ge=-90, le=90)
    closestLong: float | None = Field(default=None, ge=-180, le=180)
    lastupdt: datetime | str | None = None
    firsttime: datetime | str | None = None
    lasttime: datetime | None = None
    startTransID: str | date | None = None
    endTransID: str | date | None = None
    netid: str | None = Field(default=None, min_length=8, max_length=17)
    name: str | None = None
    namelike: str | None = None
    showBt: Literal["true", "false"] | None = None
    showBle: Literal["true", "false"] | None = None
    minQoS: int | None = Field(default=None, ge=0, le=7)
    variance: float | None = Field(default=None, ge=0.001, le=0.2)
    mfgrIdMinimum: int | None = None
    mfgrIdMaximum: int | None = None
    housenumber: str | None = None
    road: str | None = None
    city: str | None = None
    region: str | None = None
    postalCode: str | None = None
    country: str | None = None
    resultsPerPage: int | None = None
    searchAfter: str | None = None

    @field_serializer("lastupdt", "firsttime", "lasttime")
    def serialize_datetime(cls, v: datetime | str | None) -> str | None:
        match v:
            case None:
                return None
            case datetime():
                return v.strftime("%Y%m%d%H%M%S")
            case _:
                return v

    @field_validator("lastupdt", "firsttime", "lasttime")
    def validate_datetime(cls, v: datetime | str | None) -> datetime | None:
        match v:
            case None:
                return None
            case str():
                return datetime.strptime(v, "%Y%m%d%H%M%S")
            case _:
                return v

    @field_validator("startTransID", "endTransID")
    def validate_transid(cls, v: date | str | None) -> date | None:
        match v:
            case None:
                return None
            case str():
                return datetime.strptime(v, "%Y%m%d-00000").date()
            case _:
                return v

    @field_serializer("startTransID", "endTransID")
    def serialize_transid(cls, v: date | str | None) -> str | None:
        match v:
            case None:
                return v
            case date():
                return v.strftime("%Y%m%d-00000")
            case _:
                return v
