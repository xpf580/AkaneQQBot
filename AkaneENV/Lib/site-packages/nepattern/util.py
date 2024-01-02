from __future__ import annotations

import sys
import dataclasses
import sre_compile
from typing import TYPE_CHECKING, List, Pattern, Union
from pathlib import Path
from tarina.lang import lang

if sys.version_info >= (3, 9):  # pragma: no cover
    from types import GenericAlias as CGenericAlias  # noqa
else:
    CGenericAlias: type = type(List[int])  # noqa

if sys.version_info >= (3, 10):   # pragma: no cover
    from types import UnionType as CUnionType  # noqa
else:
    CUnionType: type = type(Union[int, str])  # noqa

if TYPE_CHECKING:
    TPattern = Pattern[str]
else:
    TPattern: type[Pattern[str]] = type(sre_compile.compile("", 0))
GenericAlias: type = type(List[int])
UnionType: type = type(Union[int, str])


class _All:
    """泛匹配"""

    def __repr__(self):
        return "AllParam"


AllParam = _All()


@dataclasses.dataclass
class RawStr:
    value: str


lang.load(Path(__file__).parent / "i18n")
