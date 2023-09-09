from dataclasses import dataclass
from typing import Optional
from enum import StrEnum


class ITEM_MODE(StrEnum):
    SEARCH = "search"
    FAVOURITES = "favourites"
    CATEGORIES = "categories"
    CATEGORY = "category"
    STREAM = "stream"
    MAIN = "main"

    @classmethod
    def _missing_(cls, value: Optional[str] = ""):
        return cls.MAIN


@dataclass
class MENU_ITEM:
    name: str
    mode: ITEM_MODE


@dataclass
class API_INFO:
    username: str
    password: str
    host: str
    http_port: int
    https_port: int


@dataclass
class API_CATEGORY:
    category_id: str
    category_name: str
    parent_id: int


@dataclass
class API_STREAM:
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


main_menu = [
    MENU_ITEM(name="Categories", mode=ITEM_MODE.CATEGORIES),
    MENU_ITEM(name="Favourites", mode=ITEM_MODE.FAVOURITES),
    MENU_ITEM(name="Search", mode=ITEM_MODE.SEARCH)
]
