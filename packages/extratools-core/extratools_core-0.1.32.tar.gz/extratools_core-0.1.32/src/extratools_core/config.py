from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import timedelta
from enum import IntEnum
from os import environ
from pathlib import Path
from typing import Any, NamedTuple

from cachetools import TTLCache, cached
from sortedcontainers import SortedList

from .json import JsonDict, get_by_path, merge_json, read_json_from, set_by_path


class ConfigLevel(IntEnum):
    DEFAULT = 0
    CONFIG_FILE = 1
    ENV = 2
    DYNAMIC = 3
    ADHOC = 4


class ConfigSource(NamedTuple):
    name: str
    level: ConfigLevel
    data: Callable[[], JsonDict] | JsonDict

    @staticmethod
    def sort_key(t: ConfigSource) -> tuple[ConfigLevel, str]:
        return (t.level, t.name)


class Config:
    def __init__(
        self,
        *,
        register_env: bool = True,
        config_files: Iterable[Path | str] | None = None,
        ttl: timedelta = timedelta(minutes=10),
    ) -> None:
        self.sources: SortedList = SortedList(key=ConfigSource.sort_key)

        self.__cache = TTLCache(maxsize=1, ttl=ttl.total_seconds())

        @cached(cache=self.__cache)
        def raw() -> JsonDict:
            return merge_json(*[
                (
                    source.data() if isinstance(source.data, Callable)
                    else source.data
                )
                for source in self.sources
            ])

        self.raw: Callable[[], JsonDict] = raw

        for config_file in config_files or []:
            config_file = Path(config_file).expanduser()

            self.register_source(ConfigSource(
                name=config_file.name,
                level=ConfigLevel.CONFIG_FILE,
                data=read_json_from(config_file),
            ))

        if register_env:
            self.register_source(ConfigSource(
                name="env",
                level=ConfigLevel.ENV,
                data={
                    "env": environ.copy(),
                },
            ))

        self.adhoc: JsonDict = {}
        self.register_source(ConfigSource(
            name="adhoc",
            level=ConfigLevel.ADHOC,
            data=self.adhoc,
        ))

    def register_source(
        self,
        source: ConfigSource,
    ) -> None:
        self.sources.add(source)

        self.__cache.clear()

    def get(self, path: str) -> Any:
        if path.lstrip('.') == path:
            path = '.' + path

        return get_by_path(self.raw(), path)

    def set_in_adhoc(self, path: str, value: Any) -> None:
        if path.lstrip('.') == path:
            path = '.' + path

        set_by_path(self.adhoc, path, value)

        self.__cache.clear()
