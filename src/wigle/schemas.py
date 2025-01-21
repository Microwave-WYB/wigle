from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Network(BaseModel):
    trilat: float
    trilong: float
    ssid: Optional[str] = Field(default=None)
    qos: int
    transid: str
    firsttime: datetime
    lasttime: datetime
    lastupdt: datetime
    netid: str
    name: Optional[str] = Field(default=None)
    type: str
    comment: Optional[str] = Field(default=None)
    wep: Optional[str] = Field(default=None)
    bcninterval: Optional[int] = Field(default=None)
    freenet: Optional[str] = Field(default=None)
    dhcp: Optional[str] = Field(default=None)
    paynet: Optional[str] = Field(default=None)
    userfound: Optional[bool] = Field(default=None)
    channel: Optional[int] = Field(default=None)
    rcois: Optional[str] = Field(default=None)
    encryption: Optional[str] = Field(default=None)
    country: Optional[str] = Field(default=None)
    region: Optional[str] = Field(default=None)
    road: Optional[str] = Field(default=None)
    city: Optional[str] = Field(default=None)
    housenumber: Optional[str] = Field(default=None)
    postalcode: Optional[str] = Field(default=None)


class NetSearchResponse(BaseModel):
    success: bool
    totalResults: int
    first: int
    last: int
    resultCount: int
    results: list[Network]
    searchAfter: Optional[str]


class BluetoothSearchResponse(BaseModel):
    success: bool
    totalResults: int
    first: int
    last: int
    resultCount: int
    results: list[Network]
    searchAfter: Optional[str]
