from __future__ import annotations

import inspect
import re
from collections.abc import Mapping as ABCMap
from collections.abc import MutableMapping as ABCMuMap
from collections.abc import MutableSequence as ABCMuSeq
from collections.abc import MutableSet as ABCMuSet
from collections.abc import Sequence as ABCSeq
from collections.abc import Set as ABCSet
from contextlib import suppress
from copy import deepcopy
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from types import FunctionType, LambdaType, MethodType
from typing import Any, Literal, TypeVar, Union, runtime_checkable

from tarina import Empty
from tarina.lang import lang

try:
    from typing import Annotated, get_args, get_origin  # type: ignore
except ImportError:
    from typing_extensions import Annotated, get_args, get_origin

from .base import (
    DirectPattern,
    MappingPattern,
    RegexPattern,
    SequencePattern,
    SwitchPattern,
    UnionPattern
)
from .context import all_patterns, global_patterns
from .core import BasePattern, MatchMode
from .util import (
    AllParam,
    CGenericAlias,
    CUnionType,
    GenericAlias,
    RawStr,
    TPattern
)

_Contents = (Union, CUnionType, Literal)


AnyOne = BasePattern(model=MatchMode.KEEP, origin=Any, alias="any")
"""匹配任意内容的表达式"""

AnyString = BasePattern(model=MatchMode.TYPE_CONVERT, origin=str, alias="any_str")
"""匹配任意内容并转为字符串的表达式"""

STRING = BasePattern(model=MatchMode.KEEP, origin=str, alias="str", accepts=[str])

INTEGER = BasePattern(
    r"(\-?\d+)", MatchMode.REGEX_CONVERT, int, lambda _, x: int(x[1]), "int"
)
"""整形数表达式，只能接受整数样式的量"""

FLOAT = BasePattern(
    r"(\-?\d+\.?\d*)", MatchMode.REGEX_CONVERT, float, lambda _, x: float(x[1]), "float"
)
"""浮点数表达式"""

NUMBER = BasePattern(
    r"(\-?\d+(?P<float>\.\d*)?)",
    MatchMode.REGEX_CONVERT, 
    Union[int, float], 
    lambda _, x: float(x[1]) if x["float"] else int(x[1]),
    "number",
)
"""一般数表达式，既可以浮点数也可以整数"""

_Bool = BasePattern(
    r"(?i:True|False)",
    MatchMode.REGEX_CONVERT,
    bool,
    lambda _, x: x[0].lower() == "true",
    "bool",
)
_List = BasePattern(r"(\[.+?\])", MatchMode.REGEX_CONVERT, list, alias="list")
_Tuple = BasePattern(r"(\(.+?\))", MatchMode.REGEX_CONVERT, tuple, alias="tuple")
_Set = BasePattern(r"(\{.+?\})", MatchMode.REGEX_CONVERT, set, alias="set")
_Dict = BasePattern(r"(\{.+?\})", MatchMode.REGEX_CONVERT, dict, alias="dict")

EMAIL = BasePattern(r"(?:[\w\.+-]+)@(?:[\w\.-]+)\.(?:[\w\.-]+)", MatchMode.REGEX_MATCH, alias="email")
"""匹配邮箱地址的表达式"""

IP = BasePattern(
    r"(?:(?:[01]{0,1}\d{0,1}\d|2[0-4]\d|25[0-5])\.){3}(?:[01]{0,1}\d{0,1}\d|2[0-4]\d|25[0-5]):?(?:\d+)?",
    MatchMode.REGEX_MATCH,
    alias="ip",
)
"""匹配Ip地址的表达式"""

URL = BasePattern(
    r"(?:\w+://)?[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(?:\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+(?::[0-9]{1,5})?[-a-zA-Z0-9()@:%_\\\+\.~#?&//=]*",
    MatchMode.REGEX_MATCH,
    alias="url",
)
"""匹配网页链接的表达式"""

HEX = BasePattern(
    r"((?:0x)?[0-9a-fA-F]+)",
    MatchMode.REGEX_CONVERT,
    int,
    lambda _, x: int(x[1], 16),
    "hex",
)
"""匹配16进制数的表达式"""

HEX_COLOR = BasePattern(
    r"(#[0-9a-fA-F]{6})", MatchMode.REGEX_CONVERT, str, lambda _, x: x[1][1:], "color"
)
"""匹配16进制颜色代码的表达式"""

MILLI_SECOND = 1
SECOND = MILLI_SECOND * 1000
MINUTE = SECOND * 60
HOUR = MINUTE * 60
DAY = HOUR * 24
WEEK = DAY * 7

NUMERIC = r"\d+(?:\.\d+)?"
TIME_REGEXP = re.compile(
    "^"
    + "".join(
        map(
            lambda unit: f"({NUMERIC}{unit})?",
            [
                "w(?:eek(?:s)?)?",
                "d(?:ay(?:s)?)?",
                "h(?:our(?:s)?)?",
                "m(?:in(?:ute)?(?:s)?)?",
                "s(?:ec(?:ond)?(?:s)?)?",
            ],
        )
    )
)

def _parse_time(x: str) -> datetime:  # pragma: no cover

    if capture := TIME_REGEXP.match(x):
        if stamp := (
            float(capture[1] or 0) * WEEK
            + float(capture[2] or 0) * DAY
            + float(capture[3] or 0) * HOUR
            + float(capture[4] or 0) * MINUTE
            + float(capture[5] or 0) * SECOND
        ):
            return datetime.now() + timedelta(milliseconds=stamp)
    if re.match(r"^\d{1,2}(:\d{1,2}){1,2}$", x):
        return datetime.fromisoformat(f"{datetime.now().strftime('%Y-%m-%d')}-{x}")
    if re.match(r"^\d{1,2}-\d{1,2}-\d{1,2}(:\d{1,2}){1,2}$", x):
        return datetime.fromisoformat(f"{datetime.now().year}-{x}")
    return datetime.fromisoformat(x)


DATETIME = BasePattern(
    model=MatchMode.TYPE_CONVERT,
    origin=datetime,
    alias="datetime",
    accepts=[str, int, FLOAT],
    converter=lambda _, x: datetime.fromtimestamp(x)
    if isinstance(x, (int, float))
    else _parse_time(x),
)
"""匹配时间的表达式"""

global_patterns().update(
    {
        Any: AnyOne,
        Ellipsis: AnyOne,
        object: AnyOne,
        "any": AnyOne,
        "any_str": AnyString,
        "email": EMAIL,
        "color": HEX_COLOR,
        "hex": HEX,
        "ip": IP,
        "url": URL,
        "...": AnyOne,
        "datetime": DATETIME,
    }
)

StrPath = BasePattern(
    model=MatchMode.TYPE_CONVERT, origin=Path, alias="path", accepts=[str]
)
PathFile = BasePattern(
    model=MatchMode.TYPE_CONVERT,
    origin=bytes,
    alias="file",
    accepts=[Path],
    previous=StrPath,
    converter=lambda _, x: x.read_bytes() if x.exists() and x.is_file() else None,  # type: ignore
)
global_patterns().set(PathFile)


global_patterns().sets([STRING, INTEGER, FLOAT, _Bool, _List, _Tuple, _Set, _Dict], no_alias=True)
global_patterns()["number"] = NUMBER


def _generic_parser(item: GenericAlias, extra: str) -> BasePattern:  # type: ignore
    origin = get_origin(item)
    if origin is Annotated:
        org, *meta = get_args(item)
        if not isinstance(_o := type_parser(org, extra), BasePattern):  # type: ignore  # pragma: no cover
            raise TypeError(_o)
        _arg = deepcopy(_o)
        _arg.alias = (
            al[-1] if (al := [i for i in meta if isinstance(i, str)]) else _arg.alias
        )
        _arg.validators.extend(i for i in meta if callable(i))
        return _arg
    if origin in _Contents:
        _args = {type_parser(t, extra) for t in get_args(item)}
        return (_args.pop() if len(_args) == 1 else UnionPattern(_args)) if _args else AnyOne
    if origin in (dict, ABCMap, ABCMuMap):
        if args := get_args(item):
            return MappingPattern(
                arg_key=type_parser(args[0], "ignore"),
                arg_value=type_parser(args[1], "allow"),
            )
        return MappingPattern(AnyOne, AnyOne)  # pragma: no cover
    _args = type_parser(args[0], "allow") if (args := get_args(item)) else AnyOne
    if origin in (ABCMuSeq, list):
        return SequencePattern(list, _args)
    if origin in (ABCSeq, tuple):
        return SequencePattern(tuple, _args)
    if origin in (ABCMuSet, ABCSet, set):
        return SequencePattern(set, _args)
    return BasePattern("", 0, origin, alias=f"{repr(item).split('.')[-1]}", accepts=[origin])  # type: ignore


def _typevar_parser(item: TypeVar):
    return BasePattern(model=MatchMode.KEEP, origin=Any, alias=f'{item}'[1:], accepts=[item])  # type: ignore


def _protocol_parser(item: type):
    if not getattr(item, '_is_runtime_protocol', True):  # pragma: no cover
        item = runtime_checkable(deepcopy(item))  # type: ignore
    return BasePattern(model=MatchMode.KEEP, origin=Any, alias=f'{item}', accepts=[item])


def type_parser(item: Any, extra: str = "allow") -> BasePattern:
    """对数类型的检查， 将一般数据类型转为 BasePattern 或者特殊类型"""
    if isinstance(item, BasePattern) or item is AllParam:
        return item
    with suppress(TypeError):
        if item and (pat := all_patterns().get(item, None)):
            return pat
    with suppress(TypeError):
        if isinstance(item, (GenericAlias, CGenericAlias, CUnionType)):
            return _generic_parser(item, extra)
    if isinstance(item, TypeVar):
        return _typevar_parser(item)
    if getattr(item, "_is_protocol", False):
        return _protocol_parser(item)
    if isinstance(item, (FunctionType, MethodType, LambdaType)):
        if len((sig := inspect.signature(item)).parameters) not in (1, 2):  # pragma: no cover
            raise TypeError(f"{item} can only accept 1 or 2 argument")
        anno = list(sig.parameters.values())[-1].annotation
        return BasePattern(
            accepts=[]
            if anno == Empty
            else list(_)
            if (_ := get_args(anno))
            else [anno],
            origin=Any if sig.return_annotation == Empty else sig.return_annotation,
            converter=item if len(sig.parameters) == 2 else lambda _, x: item(x),
            model=MatchMode.TYPE_CONVERT,
        )
    if isinstance(item, TPattern):  # type: ignore
        return RegexPattern(item.pattern, alias=f"'{item.pattern}'")
    if isinstance(item, str):
        if item.startswith("re:"):
            pat = item[3:]
            return BasePattern(pat, MatchMode.REGEX_MATCH, alias=f"'{pat}'")
        if item.startswith("rep:"):
            pat = item[4:]
            return RegexPattern(pat, alias=f"'{pat}'")
        if "|" in item:
            names = item.split("|")
            return UnionPattern(all_patterns().get(i, i) for i in names if i)
        return DirectPattern(item)
    if isinstance(item, RawStr):
        return DirectPattern(item.value, alias=f"'{item.value}'")
    if isinstance(
        item, (list, tuple, set, ABCSeq, ABCMuSeq, ABCSet, ABCMuSet)
    ):  # Args[foo, [123, int]]
        return UnionPattern(
            map(lambda x: type_parser(x) if inspect.isclass(x) else x, item)
        )
    if isinstance(item, (dict, ABCMap, ABCMuMap)):
        return SwitchPattern(dict(item))
    if item is None or type(None) == item:
        return Empty  # type: ignore
    if extra == "ignore":
        return AnyOne
    elif extra == "reject":
        raise TypeError(lang.require("nepattern", "validate_reject").format(target=item))
    return BasePattern.of(item) if inspect.isclass(item) else BasePattern.on(item)


class Bind:
    __slots__ = ()

    def __new__(cls, *args, **kwargs):  # pragma: no cover
        raise TypeError("Type Bind cannot be instantiated.")

    @classmethod
    @lru_cache(maxsize=None)
    def __class_getitem__(cls, params) -> BasePattern:
        if not isinstance(params, tuple) or len(params) < 2:
            raise TypeError(
                "Bind[...] should be used with only two arguments (a type and an annotation)."
            )
        if not (
            pattern := params[0]
            if isinstance(params[0], BasePattern)
            else all_patterns().get(params[0])
        ):
            raise ValueError("Bind[...] first argument should be a BasePattern.")
        if not all(callable(i) or isinstance(i, str) for i in params[1:]):
            raise TypeError("Bind[...] second argument should be a callable or str.")
        pattern = deepcopy(pattern)
        pattern.alias = (
            al[0]
            if (al := [i for i in params[1:] if isinstance(i, str)])
            else pattern.alias
        )
        pattern._repr = pattern.__calc_repr__()
        pattern._hash = hash(pattern._repr)
        pattern.validators.extend(filter(callable, params[1:]))
        return pattern


__all__ = [
    "Bind",
    "AnyString",
    "type_parser",
    "AnyOne",
    "StrPath",
    "PathFile",
    "STRING",
    "NUMBER",
    "HEX",
    "HEX_COLOR",
    "IP",
    "URL",
    "EMAIL",
    "DATETIME",
    "INTEGER",
    "FLOAT",
]
