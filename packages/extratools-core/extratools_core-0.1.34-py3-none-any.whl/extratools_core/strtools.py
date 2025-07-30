import gzip
from base64 import b64decode, b64encode
from collections.abc import Callable, Iterable
from fnmatch import fnmatchcase
from typing import Literal

import simple_zstd as zstd

from .iter import iter_to_grams
from .seq.subseq import common_subseq, enumerate_subseqs


def str_to_grams(
    s: str,
    *,
    n: int,
    pad: str = '',
) -> Iterable[str]:
    if n < 1 or len(pad) > 1:
        raise ValueError

    for c in iter_to_grams(s, n=n, pad=pad or None):
        yield ''.join(c)


def common_substr(a: str, b: str) -> str:
    return ''.join(common_subseq(a, b))


def enumerate_substrs(s: str) -> Iterable[str]:
    return map(str, enumerate_subseqs(s))


def compress(
    s: str,
    compress_func: Callable[[bytes], bytes] = gzip.compress,
) -> str:
    """
    Compress a string by GZip + Base64 encoding.

    https://base64.guru/developers/data-uri/gzip

    Parameters
    ----------
    s : str
        String to compress
    compress_func : Callable[[bytes], bytes]
        Optional function to compress (`gzip.compress` in default)

    Returns
    -------
    str
        Compressed string
    """

    return b64encode(compress_func(s.encode())).decode()


def encode(
    s: str,
    *,
    encoding: Literal["gzip", "zstd"] | None = None,
) -> str:
    match encoding:
        case "gzip":
            return compress(s, gzip.compress)
        case "zstd":
            return compress(s, zstd.compress)
        case None:
            return s
        case _:
            raise ValueError


def decompress(
    s: str,
    decompress_func: Callable[[bytes], bytes] = gzip.decompress,
) -> str:
    """
    Decompress a string with GZip + Base64 encoding.

    https://base64.guru/developers/data-uri/gzip

    Parameters
    ----------
    s : str
        String to decompress
    compress_func : Callable[[bytes], bytes]
        Optional function to decompress (`gzip.decompress` in default)

    Returns
    -------
    str
        Decompressed string
    """

    return decompress_func(b64decode(s.encode())).decode()


def decode(
    s: str,
    *,
    encoding: Literal["gzip", "zstd"] | None = None,
) -> str:
    match encoding:
        case "gzip":
            return decompress(s, gzip.decompress)
        case "zstd":
            return decompress(s, zstd.decompress)
        case None:
            return s
        case _:
            raise ValueError


def wildcard_match(
    key: str,
    *,
    includes: Iterable[str] | None = None,
    excludes: Iterable[str] | None = None,
) -> bool:
    return (
        (
            includes is None
            or any(
                fnmatchcase(key, include)
                for include in includes
            )
        )
        and (
            excludes is None
            or not any(
                fnmatchcase(key, exclude)
                for exclude in excludes

            )
        )
    )
