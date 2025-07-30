from __future__ import annotations

import shutil
from collections.abc import Callable, Iterable
from datetime import UTC, datetime, timedelta
from enum import IntEnum
from io import StringIO
from pathlib import Path
from stat import S_IFMT

from .typing import PathLike


def clear_dir(curr_dir: PathLike) -> None:
    """
    Based on example in https://docs.python.org/3/library/pathlib.html#pathlib.Path.walk
    """

    if not curr_dir.is_dir():
        raise ValueError

    for parent, dirs, files in curr_dir.walk(top_down=False):
        for filename in files:
            (parent / filename).unlink()
        for dirname in dirs:
            (parent / dirname).rmdir()


def rm_with_empty_parents(
    curr: PathLike,
    *,
    stop: PathLike | None = None,
) -> None:
    curr.unlink()

    for parent in curr.parents:
        if parent == stop:
            return

        if parent.is_dir() and next(iter(parent.iterdir()), None) is None:
            parent.rmdir()


def cleanup_dir_by_ttl(
    curr_dir: PathLike,
    ttl: timedelta | datetime,
    *,
    include_empty_parents: bool = True,
    return_before_delete: bool = False,
) -> Iterable[tuple[PathLike, datetime]]:
    if not curr_dir.is_dir():
        raise ValueError

    now: datetime = datetime.now(UTC)

    for parent, _, files in curr_dir.walk(top_down=False):
        for filename in files:
            f: PathLike = (parent / filename)

            last_modified_time: datetime = datetime.fromtimestamp(f.stat().st_mtime, UTC)
            if isinstance(ttl, timedelta):
                ttl = now - ttl

            if last_modified_time < ttl:
                if return_before_delete:
                    yield (f, last_modified_time)

                if include_empty_parents:
                    rm_with_empty_parents(f, stop=curr_dir)
                else:
                    f.unlink()

                if not return_before_delete:
                    yield (f, last_modified_time)


def read_text_by_pattern(
    *patterns: str,
    pwd: Path | str | None = None,
    seperator: str | None = None,
    add_newline: bool = True,
) -> str:
    sio = StringIO()

    pwd = Path() if not pwd else Path(pwd).expanduser()
    for pattern in patterns:
        for path in pwd.glob(pattern):
            if not path.is_file():
                continue

            file_content = path.read_text()
            sio.write(file_content)

            if add_newline and file_content[-1] != "\n":
                sio.write("\n")

            if seperator:
                sio.write(seperator)

    content: str = sio.getvalue()
    sio.close()
    return content


def __find_sibling(
    curr: PathLike,
    *,
    match_type: bool = True,
    match_dot_prefix: bool = True,
    cmp_op: Callable[[str, str], bool],
    min_max_func: Callable[..., PathLike],
) -> PathLike | None:
    # Must use absolute path to be able to get get name and parent correctly
    curr = curr.absolute()
    parent: PathLike = curr.parent

    result: PathLike | None = None
    for sibling in parent.iterdir():
        if match_type and (
            PathType.get(curr) != PathType.get(sibling)
        ):
            continue
        if match_dot_prefix and (
            (curr.name.startswith(".") and not sibling.name.startswith("."))
            or (not curr.name.startswith(".") and sibling.name.startswith("."))
        ):
            continue
        if not cmp_op(curr.name, sibling.name):
            continue

        result = (
            min_max_func(sibling, result, key=lambda x: x.name) if result
            else sibling
        )

    return result


def find_next_sibling(
    curr: PathLike,
    *,
    match_type: bool = True,
    match_dot_prefix: bool = True,
) -> PathLike | None:
    return __find_sibling(
        curr,
        match_type=match_type,
        match_dot_prefix=match_dot_prefix,
        cmp_op=lambda curr_name, sibling_name: curr_name < sibling_name,
        min_max_func=min,
    )


def find_previous_sibling(
    curr: PathLike,
    *,
    match_type: bool = True,
    match_dot_prefix: bool = True,
) -> PathLike | None:
    return __find_sibling(
        curr,
        match_type=match_type,
        match_dot_prefix=match_dot_prefix,
        cmp_op=lambda curr_name, sibling_name: curr_name > sibling_name,
        min_max_func=max,
    )


class PathType(IntEnum):
    # Defined in `stat` in standard library
    DIR = 0o040000
    CHAR_DEVICE = 0o020000
    BLOCK_DEVICE = 0o060000
    FILE = 0o100000
    FIFO = 0o010000
    SYM_LINK = 0o120000
    SOCKET = 0o140000
    UNKNOWN = 0

    @staticmethod
    def get(path: PathLike) -> PathType:
        if isinstance(path, Path):
            return PathType(S_IFMT(path.stat().st_mode))

        if path.is_dir():
            return PathType.DIR
        if path.is_file():
            return PathType.FILE
        return PathType.UNKNOWN


class LocalPath(Path):
    def rmtree(self) -> None:
        shutil.rmtree(self)

    def path_type(self) -> PathType:
        return PathType.get(self)
