from extratools_core.path import LocalPath, PathType, find_next_sibling, find_previous_sibling


def test_find_sibling() -> None:
    p = LocalPath("src")

    np = find_next_sibling(p)
    assert np
    assert np.samefile(LocalPath("test"))
    pp = find_previous_sibling(np)
    assert pp
    assert pp.samefile(p)
    assert not find_next_sibling(np)

    p = LocalPath("mise.toml")

    np = find_next_sibling(p)
    assert np
    assert np.samefile(LocalPath("pyproject.toml"))
    pp = find_previous_sibling(np)
    assert pp
    assert pp.samefile(p)


def test_localpath_path_type() -> None:
    assert LocalPath().path_type() == PathType.DIR

    assert LocalPath("src").path_type() == PathType.DIR

    assert LocalPath("pyproject.toml").path_type() == PathType.FILE
