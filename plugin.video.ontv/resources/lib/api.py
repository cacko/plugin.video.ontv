from pathlib import Path
from typing import Any
import pickle
import requests
from resources.lib.models import Settings, Category, Stream, ApiInfo


class ApiMeta(type):

    __instance: 'Api' = None
    __api_info: Settings = None
    __profile_path: Path = None

    def __call__(cls, *args: Any, **kwds: Any) -> Any:
        if not cls.__instance:
            cls.__instance = type.__call__(
                cls,
                cls.__api_info,
                cls.__profile_path,
                *args,
                **kwds
            )
        return cls.__instance

    def register(cls, info: Settings, profile: Path):
        cls.__api_info = info
        cls.__profile_path = profile

    @property
    def info(cls) -> ApiInfo:
        return cls().get_info()

    @property
    def categories(cls) -> list[Category]:
        return cls().get_categories()

    @property
    def streams(cls) -> list[Stream]:
        return cls().get_streams()

    def stream_url(cls, stream_id) -> str:
        return cls().get_stream_url(stream_id)


class Api(object, metaclass=ApiMeta):

    def __init__(self, info: Settings, profile: Path) -> None:
        self.__username = info.username
        self.__password = info.password
        self.__hostname = info.host
        self.__port = info.http_port
        self.__https_port = info.https_port
        self.__profile = profile

    @property
    def player_api(self) -> str:
        return f"http://{self.__hostname}:{self.__port}/player_api.php"

    @property
    def stream_api(self) -> str:
        return f"http://{self.__hostname}:{self.__port}/live/{self.__username}/{self.__password}"

    @property
    def cache_categories(self) -> Path:
        return self.__profile / "categories.data"

    @property
    def cache_streams(self) -> Path:
        return self.__profile / "streams.data"

    @property
    def cache_info(self) -> Path:
        return self.__profile / "apinfo.data"

    def __save(self, cp: Path, data: Any):
        with cp.open("wb") as fp:
            pickle.dump(data, fp)

    def __load(self, cp: Path) -> Any:
        with cp.open("rb") as fp:
            return pickle.load(fp)

    def __get(self, url, params: dict[str, Any] = {}) -> dict[str, Any]:
        res = requests.get(
            url=url,
            params=params
        )
        return res.json()

    def get_categories(self) -> list[Category]:
        if not self.cache_categories.exists():
            data = self.__get(
                self.player_api,
                dict(
                    username=self.__username,
                    password=self.__password,
                    action="get_live_categories"
                )
            )
            result = [Category(**ct) for ct in data]
            self.__save(self.cache_categories, result)
            return result
        return self.__load(self.cache_categories)

    def get_streams(self) -> list[Stream]:
        if not self.cache_streams.exists():
            data = self.__get(
                self.player_api,
                dict(
                    username=self.__username,
                    password=self.__password,
                    action="get_live_streams"
                )
            )
            result = [Stream(**ct) for ct in data]
            self.__save(self.cache_streams, result)
            return result
        return self.__load(self.cache_streams)

    def get_info(self) -> ApiInfo:
        if not self.cache_info.exists():
            data = self.__get(
                self.player_api,
                dict(
                    username=self.__username,
                    password=self.__password,
                )
            )
            result = ApiInfo(**data)
            self.__save(self.cache_info, result)
            return result
        return self.__load(self.cache_info)

    def get_stream_url(self, stream_id) -> str:
        base_url = f"{self.stream_api}/{stream_id}.ts"
        return base_url
        res = requests.get(base_url, allow_redirects=False)
        return res.headers.get("Location")
