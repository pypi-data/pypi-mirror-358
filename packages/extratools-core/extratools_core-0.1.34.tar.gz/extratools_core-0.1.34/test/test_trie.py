from random import random
from uuid import uuid4

from extratools_core.test import (
    is_proper_mapping,
    is_proper_mutable_mapping,
    is_proper_searchable_mapping,
)
from extratools_core.trie import TrieDict


def test_TrieDict() -> None:  # noqa: N802
    is_proper_mapping(TrieDict, key_cls=str, value_cls=int)

    is_proper_mapping(
        lambda: TrieDict({str(uuid4()): random()}),
        key_cls=lambda: str(uuid4()),
        value_cls=random,
    )

    is_proper_searchable_mapping(
        lambda: TrieDict({f"test-{i}": i for i in range(5)}),
        filter_cls=lambda: "test",
        keys_func=lambda filter_body: [f"{filter_body}-{i}" for i in range(10)],
    )

    is_proper_mutable_mapping(dict, key_cls=str, value_cls=int)

    is_proper_mutable_mapping(
        lambda: TrieDict({str(uuid4()): random()}),
        key_cls=lambda: str(uuid4()),
        value_cls=random,
    )


def test_TrieDict_search() -> None:  # noqa: N802
    td = TrieDict({"ada": 1, "bob": 2, "chad": 3, "cecil": 4})

    assert list(td) == list(td.search()) == ["ada", "bob", "chad", "cecil"]

    assert list(td.search("a")) == ["ada"]

    assert list(td.search("b")) == ["bob"]

    assert list(td.search("c")) == ["chad", "cecil"]
