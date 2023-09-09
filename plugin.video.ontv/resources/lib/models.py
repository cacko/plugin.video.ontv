from dataclasses import dataclass
from typing import Optional
from enum import StrEnum


class ITEM_MODE(StrEnum):
    SEARCH = "search"
    FAVOURITES = "favourites"
    ADD_FAVOURITE = "add_favourite"
    REM_FAVOURITE = "rem_favourites"
    CATEGORIES = "categories"
    CATEGORY = "category"
    STREAM = "stream"
    MAIN = "main"

    @classmethod
    def _missing_(cls, value: Optional[str] = ""):
        return cls.MAIN


@dataclass
class MenuItem:
    name: str
    mode: ITEM_MODE
    icon: Optional[str] = None


@dataclass
class Settings:
    username: str
    password: str
    host: str
    http_port: int
    https_port: int


@dataclass
class Category:
    category_id: str
    category_name: str
    parent_id: int


@dataclass
class Stream:
    num: int
    name: str
    stream_type: str
    stream_id: int
    stream_icon: str
    epg_channel_id: str
    added: str
    is_adult: int
    category_id: str
    category_ids: list[int]
    custom_sid: Optional[str] = None
    tv_archive: Optional[int] = None
    direct_source: Optional[str] = None
    tv_archive_duration: Optional[int] = None


@dataclass
class Userinfo:
    username: str
    password: str
    message: str
    auth: int
    status: str
    exp_date: str
    is_trial: str
    active_cons: str
    created_at: str
    max_connections: str
    allowed_output_formats: list[str]


@dataclass
class Serverinfo:
    url: str
    port: str
    https_port: str
    server_protocol: str
    rtmp_port: str
    timezone: str
    timestamp_now: int
    time_now: str
    process: bool


@dataclass
class ApiInfo:
    user_info: Userinfo
    server_info: Serverinfo


main_menu = [
    MenuItem(name="Categories", mode=ITEM_MODE.CATEGORIES),
    MenuItem(name="Favourites", mode=ITEM_MODE.FAVOURITES, icon="DefaultAddonsInstalled.png"),
    MenuItem(name="Search", mode=ITEM_MODE.SEARCH, icon="DefaultAddonsSearch.png")
]
