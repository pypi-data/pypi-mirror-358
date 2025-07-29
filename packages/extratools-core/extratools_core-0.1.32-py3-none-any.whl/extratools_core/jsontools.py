import json
import re
import tomllib
from csv import DictWriter
from io import StringIO
from pathlib import Path
from re import Match, Pattern
from types import NoneType
from typing import Any, TypedDict

import yaml
from toolz.itertoolz import groupby

type JsonDict = dict[str, Any]

type DictOfJsonDicts = dict[str, JsonDict]
type ListOfJsonDicts = list[JsonDict]


class DictOfJsonDictsDiffUpdate(TypedDict):
    old: JsonDict
    new: JsonDict


class DictOfJsonDictsDiff(TypedDict):
    deletes: dict[str, JsonDict]
    inserts: dict[str, JsonDict]
    updates: dict[str, DictOfJsonDictsDiffUpdate]


class ListOfJsonDictsDiff(TypedDict):
    deletes: list[JsonDict]
    inserts: list[JsonDict]


def flatten(data: Any) -> Any:
    def flatten_rec(data: Any, path: str) -> None:
        if isinstance(data, dict):
            for k, v in data.items():
                flatten_rec(v, path + (f".{k}" if path else k))
        elif isinstance(data, list):
            for i, v in enumerate(data):
                flatten_rec(v, path + f"[{i}]")
        else:
            flatten_dict[path or "."] = data

    flatten_dict: JsonDict = {}
    flatten_rec(data, "")
    return flatten_dict


def json_to_csv(
    data: DictOfJsonDicts | ListOfJsonDicts,
    /,
    csv_path: Path | str | None = None,
    *,
    key_field_name: str = "_key",
) -> str:
    if isinstance(data, dict):
        data = [
            {
                # In case there is already a key field in each record,
                # the new key field will be overwritten.
                # It is okay though as the existing key field is likely
                # serving the purpose of containing keys.
                key_field_name: key,
                **value,
            }
            for key, value in data.items()
        ]

    fields: set[str] = set()
    for record in data:
        fields.update(record.keys())

    sio = StringIO()

    writer = DictWriter(sio, fieldnames=fields)
    writer.writeheader()
    writer.writerows(data)

    csv_str: str = sio.getvalue()

    if csv_path:
        Path(csv_path).write_text(csv_str)

    return csv_str


def dict_of_json_dicts_diff(
    old: DictOfJsonDicts,
    new: DictOfJsonDicts,
) -> DictOfJsonDictsDiff:
    inserts: dict[str, JsonDict] = {}
    updates: dict[str, DictOfJsonDictsDiffUpdate] = {}

    for new_key, new_value in new.items():
        old_value: dict[str, Any] | None = old.get(new_key, None)
        if old_value is None:
            inserts[new_key] = new_value
        elif json.dumps(old_value) != json.dumps(new_value):
            updates[new_key] = {
                "old": old_value,
                "new": new_value,
            }

    deletes: dict[str, JsonDict] = {
        old_key: old_value
        for old_key, old_value in old.items()
        if old_key not in new
    }

    return {
        "deletes": deletes,
        "inserts": inserts,
        "updates": updates,
    }


def list_of_json_dicts_diff(
    old: ListOfJsonDicts,
    new: ListOfJsonDicts,
) -> ListOfJsonDictsDiff:
    old_dict: DictOfJsonDicts = {
        json.dumps(d): d
        for d in old
    }
    new_dict: DictOfJsonDicts = {
        json.dumps(d): d
        for d in new
    }

    inserts: list[JsonDict] = [
        new_value
        for new_key, new_value in new_dict.items()
        if new_key not in old_dict
    ]
    deletes: list[JsonDict] = [
        old_value
        for old_key, old_value in old_dict.items()
        if old_key not in new_dict
    ]

    return {
        "deletes": deletes,
        "inserts": inserts,
    }


def merge_json(
    *values: Any,
    concat_lists: bool = True,
) -> Any:
    def merge_json_dicts(*jds: JsonDict) -> JsonDict:
        groups: dict[str, list[JsonDict]] = groupby(
            lambda kv_tuple: kv_tuple[0],
            (
                kv_tuple
                for jd in jds
                for kv_tuple in jd.items()
            ),
        )

        return {
            key: merge_json(
                *[value for _, value in kv_tuples],
                concat_lists=concat_lists,
            )
            for key, kv_tuples in groups.items()
        }

    first_value_type: type | None = None

    not_none_values = []

    for value in values:
        value_type: type = type(value)
        if value_type is NoneType:
            continue

        if first_value_type is None:
            first_value_type = value_type
        elif first_value_type != value_type:
            raise ValueError

        not_none_values.append(value)

    if first_value_type is None or first_value_type is NoneType:
        return None

    if first_value_type is dict:
        return merge_json_dicts(*not_none_values)

    if first_value_type is list and concat_lists:
        return [
            item
            for value in not_none_values
            for item in value
        ]

    return not_none_values[-1]


__PATH_PATTERN: Pattern = re.compile(r"(?:\.(?P<field>\w+)|\[(?P<index>[0-9]+)\])(?P<remaining>.*)")


def get_by_path(data: Any, path: str) -> Any:
    match: Match | None = __PATH_PATTERN.fullmatch(path)
    if not match:
        raise ValueError

    new_data: Any
    try:
        if field := match.group("field"):
            if not isinstance(data, dict):
                raise LookupError

            new_data = data[field]
        elif index := match.group("index"):
            if not isinstance(data, list):
                raise LookupError

            new_data = data[int(index)]
        else:
            # This should be unreachable
            raise NotImplementedError
    except (IndexError, KeyError) as e:
        raise LookupError from e

    remaining_path: str = match.group("remaining")
    if remaining_path:
        return get_by_path(new_data, remaining_path)

    return new_data


def set_by_path(data: Any, path: str, value: Any) -> None:
    match: Match | None = __PATH_PATTERN.fullmatch(path)
    if not match:
        raise ValueError

    remaining_path: str = match.group("remaining")

    try:
        if field := match.group("field"):
            if not isinstance(data, dict):
                raise LookupError

            if field not in data and remaining_path:
                data[field] = {}

            if remaining_path:
                set_by_path(data[field], remaining_path, value)
            else:
                data[field] = value
        elif index := match.group("index"):
            if not isinstance(data, list):
                raise LookupError

            index = int(index)

            if remaining_path:
                set_by_path(data[index], remaining_path, value)
            else:
                data[index] = value
        else:
            # This should be unreachable
            raise NotImplementedError
    except (IndexError, KeyError) as e:
        raise LookupError from e


def read_json_from(path: Path | str) -> Any:
    path = Path(path).expanduser()

    content: str = path.read_text()
    match path.suffix.lower():
        case ".json":
            return json.loads(content)
        case ".toml":
            return tomllib.loads(content)
        case ".yaml" | ".yml":
            return yaml.safe_load(content)
        case _:
            raise ValueError
