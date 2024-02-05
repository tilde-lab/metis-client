"""Compatibility layer"""

import sys

if sys.version_info < (3, 9):  # pragma: no cover
    from typing import Awaitable, Callable, Dict, List, Mapping, Sequence
else:  # pragma: no cover
    from collections.abc import Awaitable, Callable, Mapping, Sequence

    Dict = dict
    List = list


if sys.version_info < (3, 10):  # pragma: no cover
    from typing_extensions import TypeGuard
else:  # pragma: no cover
    from typing import TypeGuard

if sys.version_info < (3, 11):  # pragma: no cover
    from typing_extensions import Concatenate, NotRequired, ParamSpec, TypedDict, Unpack
else:  # pragma: no cover
    from typing import Concatenate, NotRequired, ParamSpec, TypedDict, Unpack


__all__ = [
    "Awaitable",
    "Callable",
    "Concatenate",
    "Dict",
    "List",
    "Mapping",
    "NotRequired",
    "ParamSpec",
    "Sequence",
    "TypeGuard",
    "TypedDict",
    "Unpack",
]
