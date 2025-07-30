import pytest

from extratools_core.json import JsonDict, flatten, get_by_path, merge_json, set_by_path


def test_flatten() -> None:
    d = {
        "a": 1,
        "b": [
            2,
            {
                "c": 3,
                "d": [4],
            },
        ],
    }

    assert flatten(d) == {
        "a": 1,
        "b[0]": 2,
        "b[1].c": 3,
        "b[1].d[0]": 4,
    }

    assert flatten([1]) == {
        "[0]": 1,
    }

    assert flatten(1) == {
        ".": 1,
    }


def test_merge_json() -> None:
    assert merge_json(
        {},
        {},
    ) == merge_json(
        {},
        None,
    ) == {}

    assert merge_json(
        None,
        None,
    ) is None

    with pytest.raises(ValueError):
        merge_json(
            {},
            [],
        )

    assert merge_json(
        {
            "name": "Ada",
            "age": 20,
            "address": {
                "country": "US",
                "city": None,
            },
            "items": [1, 2],
        },
        {
            "name": "Bob",
            "address": {
                "country": "Canada",
                "city": "Vancouver",
                "zipCode": None,
            },
            "items": None,
        },
        {
            "name": "Chad",
            "age": 30,
            "items": [3],
        },
    ) == {
        "name": "Chad",
        "age": 30,
        "address": {
            "country": "Canada",
            "city": "Vancouver",
            "zipCode": None,
        },
        "items": [1, 2, 3],
    }

    assert merge_json(
        {
            "items": [1, 2],
        },
        {
            "items": None,
        },
        {
            "items": [3],
        },
        concat_lists=False,
    ) == {
        "items": [3],
    }


def test_get_by_path() -> None:
    data: JsonDict = {
        "name": "Chad",
        "age": 30,
        "address": {
            "country": "Canada",
            "city": "Vancouver",
            "zipCode": None,
        },
        "items": [1, 2, 3],
    }

    with pytest.raises(ValueError):
        get_by_path(data, "whatever")

    assert get_by_path(data, ".name") == "Chad"

    assert get_by_path(data, ".age") == 30

    assert get_by_path(data, ".address") == {
        "country": "Canada",
        "city": "Vancouver",
        "zipCode": None,
    }

    with pytest.raises(LookupError):
        get_by_path(data, ".address[0]")

    assert get_by_path(data, ".address.city") == "Vancouver"

    assert get_by_path(data, ".items") == [1, 2, 3]

    with pytest.raises(LookupError):
        get_by_path(data, ".items.name")

    assert get_by_path(data, ".items[1]") == 2

    with pytest.raises(LookupError):
        get_by_path(data, ".items[3]")

    data2: JsonDict = {
        "addresses": [{
            "country": "Canada",
            "city": "Vancouver",
            "zipCode": None,
        }],
    }

    assert get_by_path(data2, ".addresses[0].city") == "Vancouver"


def test_set_by_path() -> None:
    data: JsonDict = {
        "name": "Chad",
        "age": 30,
        "address": {
            "country": "Canada",
            "city": "Vancouver",
        },
        "items": [1, 2, 3],
    }

    with pytest.raises(ValueError):
        set_by_path(data, "whatever", "something")

    set_by_path(data, ".name", "Bob")
    assert data == {
        "name": "Bob",
        "age": 30,
        "address": {
            "country": "Canada",
            "city": "Vancouver",
        },
        "items": [1, 2, 3],
    }

    set_by_path(data, ".lastName", "Cat")
    assert data == {
        "name": "Bob",
        "lastName": "Cat",
        "age": 30,
        "address": {
            "country": "Canada",
            "city": "Vancouver",
        },
        "items": [1, 2, 3],
    }

    set_by_path(data, ".address.city", "Toronto")
    assert data == {
        "name": "Bob",
        "lastName": "Cat",
        "age": 30,
        "address": {
            "country": "Canada",
            "city": "Toronto",
        },
        "items": [1, 2, 3],
    }

    with pytest.raises(LookupError):
        set_by_path(data, ".address[0]", "Toronto")

    set_by_path(data, ".address.zipCode", "12345")
    assert data == {
        "name": "Bob",
        "lastName": "Cat",
        "age": 30,
        "address": {
            "country": "Canada",
            "city": "Toronto",
            "zipCode": "12345",
        },
        "items": [1, 2, 3],
    }

    set_by_path(data, ".items[1]", -2)
    assert data == {
        "name": "Bob",
        "lastName": "Cat",
        "age": 30,
        "address": {
            "country": "Canada",
            "city": "Toronto",
            "zipCode": "12345",
        },
        "items": [1, -2, 3],
    }

    with pytest.raises(LookupError):
        set_by_path(data, ".items[0].name", "Toronto")

    with pytest.raises(LookupError):
        set_by_path(data, ".items[3]", 4)

    data2: JsonDict = {
        "addresses": [{
            "country": "Canada",
            "city": "Vancouver",
        }],
    }

    set_by_path(data2, ".addresses[0].city", "Toronto")
    assert data2 == {
        "addresses": [{
            "country": "Canada",
            "city": "Toronto",
        }],
    }

    set_by_path(data2, ".job.title", "CEO")
    assert data2 == {
        "addresses": [{
            "country": "Canada",
            "city": "Toronto",
        }],
        "job": {
            "title": "CEO",
        },
    }
