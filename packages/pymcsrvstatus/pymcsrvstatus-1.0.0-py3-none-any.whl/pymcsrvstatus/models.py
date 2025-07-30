from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Debug(BaseModel):
    ping: bool
    query: bool
    bedrock: bool
    srv: bool
    query_mismatch: bool = Field(alias="querymismatch")
    ip_in_srv: bool = Field(alias="ipinsrv")
    cname_in_srv: bool = Field(alias="cnameinsrv")
    animated_motd: bool = Field(alias="animatedmotd")
    cache_hit: bool = Field(alias="cachehit")
    cache_time: datetime = Field(alias="cachetime")
    cache_expire: datetime = Field(alias="cacheexpire")
    api_version: int = Field(alias="apiversion")


class Protocol(BaseModel):
    version: int
    name: Optional[str] = None


class Object(BaseModel):
    raw: str
    clean: str
    html: str


class ListObject(BaseModel):
    raw: List[str]
    clean: List[str]
    html: List[str]


class Player(BaseModel):
    name: str
    uuid: str


class Players(BaseModel):
    online: int
    max: int
    players: Optional[List[Player]] = None


class Mod(BaseModel):
    name: str
    version: str


class ServerStatus(BaseModel):
    """ServerStatus class"""

    online: bool
    debug: Debug
    ip: Optional[str] = None
    port: Optional[int] = None
    hostname: Optional[str] = None
    version: Optional[str] = None
    protocol: Optional[Protocol] = None
    icon: Optional[str] = None
    software: Optional[str] = None
    map: Optional[Object] = None
    gamemode: Optional[str] = None
    server_id: Optional[str] = Field(default=None, alias="serverid")
    eula_blocked: Optional[bool] = None
    motd: Optional[ListObject] = None
    players: Optional[Players] = None
    plugins: Optional[List[Mod]] = None
    mods: Optional[List[Mod]] = None
    info: Optional[ListObject] = None

    def is_bedrock(self) -> bool:
        if self.server_id or self.gamemode:
            return True
        return False

    def is_java(self) -> bool:
        return not self.is_bedrock()
