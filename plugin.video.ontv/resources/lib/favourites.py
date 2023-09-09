from pathlib import Path
from typing import Any
import json
from resources.lib.models import Stream
from resources.lib.api import Api as Client


class FavouritesMeta(type):
    __instance: 'Favourites' = None
    __profile_path: Path = None

    def __call__(cls, *args: Any, **kwds: Any) -> Any:
        if not cls.__instance:
            cls.__instance = type.__call__(cls, cls.__profile_path, *args, **kwds)
        return cls.__instance

    def register(cls, profile: Path):
        cls.__profile_path = profile

    @property
    def items(cls) -> list[Stream]:
        return cls().favourites

    def is_in(cls, stream_id: str) -> bool:
        return cls().get_is_in(stream_id)

    def add(cls, stream_id: str):
        return cls().do_add(stream_id)

    def remove(cls, stream_id: str):
        return cls().do_remove(stream_id)


class Favourites(object, metaclass=FavouritesMeta):

    def __init__(self, profile: Path) -> None:
        self.__profile = profile

    @property
    def json_path(self) -> Path:
        return self.__profile / "favourites.json"

    @property
    def favourites(self) -> list[Stream]:
        result = []
        try:
            with self.json_path.open("r") as fp:
                data = json.load(fp)
                assert data
                if len(data):
                    streams = Client.streams
                    result = list(filter(lambda x: str(x.stream_id) in data, streams))
        except FileNotFoundError:
            pass
        except Exception:
            pass
        return result

    def get_is_in(self, stream_id: str) -> bool:
        ids = list(map(lambda x: str(x.stream_id), self.favourites))
        return stream_id in ids

    def do_add(self, stream_id: str):
        items = self.favourites
        items.append(stream_id)
        with self.json_path.open("w") as fp:
            json.dump(items, fp)

    def do_remove(self, stream_id: str):
        ids = list(map(lambda x: str(x.stream_id), self.favourites))
        ids.remove(stream_id)
        with self.json_path.open("w") as fp:
            json.dump(ids, fp)
