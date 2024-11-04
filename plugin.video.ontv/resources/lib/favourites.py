from pathlib import Path
from typing import Any
import json
from resources.lib.models import Stream
from resources.lib.api import Api as Client
from resources.lib.ensure import ensure

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
        self.__favourites = []

    @property
    def json_path(self) -> Path:
        return self.__profile / "favourites.json"

    @property
    def favourites(self) -> list[Stream]:
        if not self.__favourites:
            try:
                with self.json_path.open("r") as fp:
                    data = json.load(fp)
                    ensure(data).is_not_none()
                    if len(data):
                        streams = Client.streams
                        self.__favourites = list(map(lambda x: streams.get_data(stream_id=int(x)), data))
            except FileNotFoundError:
                pass
            except Exception:
                pass
        return self.__favourites

    def get_is_in(self, stream_id: str) -> bool:
        ids = list(map(lambda x: str(x.stream_id), self.favourites))
        return stream_id in ids

    def do_add(self, stream_id: str):
        items = self.favourites
        ids = list(map(lambda x: str(x.stream_id), items))
        ids.append(stream_id)
        with self.json_path.open("w") as fp:
            json.dump(ids, fp)
            self.__favourites = None

    def do_remove(self, stream_id: str):
        ids = list(map(lambda x: str(x.stream_id), self.favourites))
        ids.remove(stream_id)
        with self.json_path.open("w") as fp:
            json.dump(ids, fp)
            self.__favourites = None
