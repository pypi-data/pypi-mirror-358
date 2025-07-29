from extratools_core.seq import add_until


def test_add_until() -> None:
    assert add_until([], lambda _: True) == []

    def cond_str(e: str) -> bool:
        return len(e) >= 3

    assert add_until(["a"], cond_str) == ["a"]
    assert add_until(["a", "b"], cond_str) == ["ab"]
    assert add_until(["a", "b", "c"], cond_str) == ["abc"]
    assert add_until(["a", "b", "c", "d"], cond_str) == ["abcd"]
    assert add_until(["a", "b", "c", "d", "e"], cond_str) == ["abcde"]
    assert add_until(["a", "b", "c", "d", "e", "f"], cond_str) == ["abc", "def"]

    assert add_until(["a"], cond_str, include_all=False) == []
    assert add_until(["a", "b"], cond_str, include_all=False) == []
    assert add_until(["a", "b", "c"], cond_str, include_all=False) == ["abc"]

    assert add_until(["abc", "d"], cond_str) == ["abcd"]
    assert add_until(["abc", "d", "e"], cond_str) == ["abcde"]
    assert add_until(["abc", "d", "ef"], cond_str) == ["abc", "def"]
    assert add_until(["abc", "d", "efg"], cond_str) == ["abc", "defg"]
    assert add_until(["a", "bcd"], cond_str) == ["abcd"]
    assert add_until(["a", "bcd", "e"], cond_str) == ["abcde"]
    assert add_until(["a", "bcd", "e", "f"], cond_str) == ["abcdef"]
    assert add_until(["a", "bcd", "e", "f", "g"], cond_str) == ["abcd", "efg"]

    assert add_until(["", "a", "", "b", "", "cde", "", "f", ""], cond_str) == ["abcdef"]

    def cond_int(e: int) -> bool:
        return e >= 3

    assert add_until([1], cond_int) == [1]
    assert add_until([1, 1], cond_int) == [2]
    assert add_until([1, 1, 1], cond_int) == [3]
    assert add_until([1, 1, 1, 1], cond_int) == [4]
    assert add_until([1, 1, 1, 1, 1], cond_int) == [5]
    assert add_until([1, 1, 1, 1, 1, 1], cond_int) == [3, 3]
