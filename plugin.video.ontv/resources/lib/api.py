from pathlib import Path
from typing import Any, Optional
from datetime import datetime, timedelta, timezone
import pickle
import requests
from resources.lib.models import Settings, Category, Stream, ApiInfo
from functools import reduce


class RequiresReload(Exception):
    pass


class ApiResourceType(type):

    __instances: dict[str, 'ApiResourceType'] = {}
    profile_path: Path = None

    def __call__(cls, *args, **kwds) -> Any:
        k = cls.__name__
        if k not in cls.__instances:
            cls.__instances[k] = type.__call__(cls, *args, **kwds)
        return cls.__instances[k]

    def register(cls, profile: Path):
        cls.profile_path = profile

    def update(cls, data: Any):
        cls().do_save(data)

    def validate(cls, force=False):
        cls().do_validate(force)


class BaseApiResource(object, metaclass=ApiResourceType):

    _struct: Any = None
    _lifetime: timedelta = timedelta(hours=10)

    @property
    def path(self) -> Path:
        raise NotImplementedError

    def get_data(self, *args, **kwds) -> Any:
        raise NotImplementedError

    def do_save(self, data: Any):
        with self.path.open("wb") as fp:
            pickle.dump(data, fp)
            self._struct = None

    def _load(self) -> Any:
        try:
            assert self._struct is None
            assert self.path.exists()
            with self.path.open("rb") as fp:
                self._struct = pickle.load(fp)
        except AssertionError:
            pass
        return self._struct

    def do_validate(self, force=False):
        try:
            assert not force
            assert self.path.exists()
            mtime = datetime.fromtimestamp(self.path.lstat().st_mtime)
            assert datetime.now(tz=timezone.utc) - mtime < self._lifetime
        except AssertionError:
            raise RequiresReload


class CategoriesResource(BaseApiResource):

    _struct: list[Category] = None

    @property
    def path(self) -> Path:
        return self.__class__.profile_path / "categories.data"

    def get_data(self, *args, **kwds) -> Optional[list[Category]]:
        return self._load()


class StreamsResource(BaseApiResource):

    _struct: dict[str, list[Stream]] = None

    @property
    def path(self) -> Path:
        return self.__class__.profile_path / "streams.data"

    def get_data(self, category_id: str, *args, **kwds) -> Optional[list[Stream]]:
        return self._load().get(category_id, [])

    def _load(self) -> Any:
        try:
            assert self._struct is None
            assert self.path.exists()
            with self.path.open("rb") as fp:
                struct: list[Stream] = pickle.load(fp)
                self._struct = reduce(lambda r, x: {**r, **{x.category_id: r.get(x.category_id, [])+[x]}}, struct, {})
        except AssertionError:
            pass
        return self._struct


class ApiInfoResource(BaseApiResource):

    struct: ApiInfo = None

    @property
    def path(self) -> Path:
        return self.__class__.profile_path / "apinfo.data"

    def get_data(self, *args, **kwds) -> Optional[ApiInfo]:
        return self._load()


class ApiMeta(type):

    __instance: 'Api' = None
    __api_info: Settings = None

    def __call__(cls, *args: Any, **kwds: Any) -> Any:
        if not cls.__instance:
            cls.__instance = type.__call__(
                cls,
                cls.__api_info,
                *args,
                **kwds
            )
        return cls.__instance

    def register(cls, info: Settings, profile: Path):
        cls.__api_info = info
        BaseApiResource.register(profile=profile)

    @property
    def info(cls) -> ApiInfoResource:
        return cls().get_info()

    @property
    def categories(cls) -> CategoriesResource:
        return cls().get_categories()

    @property
    def streams(cls) -> StreamsResource:
        return cls().get_streams()

    def stream_url(cls, stream_id) -> str:
        return cls().get_stream_url(stream_id)

    def reload(cls):
        yield (0, "Reloading categories")
        cls().get_categories(True)
        yield (50, "Reloading streams")
        cls().get_streams(True)
        yield (100, "Reload one")


class Api(object, metaclass=ApiMeta):

    def __init__(self, info: Settings) -> None:
        self.__username = info.username
        self.__password = info.password
        self.__hostname = info.host
        self.__port = info.http_port
        self.__https_port = info.https_port

    @property
    def player_api(self) -> str:
        return f"http://{self.__hostname}:{self.__port}/player_api.php"

    @property
    def stream_api(self) -> str:
        return f"http://{self.__hostname}:{self.__port}/live/{self.__username}/{self.__password}"

    def __get(self, url, params: dict[str, Any] = {}) -> dict[str, Any]:
        res = requests.get(
            url=url,
            params=params
        )
        return res.json()

    def get_categories(self, reload=False) -> CategoriesResource:
        try:
            CategoriesResource.validate(reload)
        except RequiresReload:
            data = self.__get(
                self.player_api,
                dict(
                    username=self.__username,
                    password=self.__password,
                    action="get_live_categories"
                )
            )
            result = [Category(**ct) for ct in data]
            CategoriesResource.update(result)
        return CategoriesResource()

    def get_streams(self, reload=False) -> StreamsResource:
        try:
            StreamsResource.validate(reload)
        except RequiresReload:
            data = self.__get(
                self.player_api,
                dict(
                    username=self.__username,
                    password=self.__password,
                    action="get_live_streams"
                )
            )
            result = [Stream(**ct) for ct in data]
            StreamsResource.update(result)
        return StreamsResource()

    def get_info(self) -> ApiInfo:
        try:
            ApiInfoResource.validate(True)
        except RequiresReload:
            data = self.__get(
                self.player_api,
                dict(
                    username=self.__username,
                    password=self.__password,
                )
            )
            result = ApiInfo(**data)
            ApiInfoResource.update(result)
        return ApiInfoResource

    def get_stream_url(self, stream_id) -> str:
        base_url = f"{self.stream_api}/{stream_id}.ts"
        return base_url
        res = requests.get(base_url, allow_redirects=False)
        return res.headers.get("Location")
