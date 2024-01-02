from __future__ import annotations

import re
from typing import Any, Dict, Iterable, Literal, TypeVar, Match

from tarina import Empty
from tarina.lang import lang

from .core import BasePattern, MatchMode, ValidateResult, ResultFlag
from .exception import MatchFailed
from .util import TPattern


class DirectPattern(BasePattern):
    """直接判断"""
    def __init__(self, target: Any, alias: str | None = None):
        self.target = target
        super().__init__(model=MatchMode.TYPE_CONVERT, origin=type(target), alias=alias or str(target))

    def prefixed(self):
        if isinstance(self.target, str):
            return BasePattern(self.target, MatchMode.REGEX_MATCH, alias=self.alias).prefixed()
        return self

    def suffixed(self):
        if isinstance(self.target, str):
            return BasePattern(self.target, MatchMode.REGEX_MATCH, alias=self.alias).suffixed()
        return self

    def match(self, input_: Any):
        if input_ != self.target:
            raise MatchFailed(
                lang.require("nepattern", "content_error").format(target=input_)
            )
        return input_

    def validate(self, input_: Any, default: Any = None):
        if input_ == self.target:
            return ValidateResult(input_, flag=ResultFlag.VALID)
        e = MatchFailed(
            lang.require("nepattern", "content_error").format(target=input_)
        )
        if default is None:
            return ValidateResult(error=e, flag=ResultFlag.ERROR)
        return ValidateResult(
            value=None if default is Empty else default, flag=ResultFlag.DEFAULT  # type: ignore
        )

    def invalidate(self, input_: Any, default: Any = None) -> ValidateResult[Any]:
        if input_ == self.target:
            e = MatchFailed(
                lang.require("nepattern", "content_error").format(target=input_)
            )
            if default is None:
                return ValidateResult(error=e, flag=ResultFlag.ERROR)
            return ValidateResult(
                value=None if default is Empty else default, flag=ResultFlag.DEFAULT  # type: ignore
            )
        return ValidateResult(input_, flag=ResultFlag.VALID)

class RegexPattern(BasePattern[Match[str]]):
    """针对正则的特化匹配，支持正则组"""

    def __init__(self, pattern: str | TPattern, alias: str | None = None):
        super().__init__("", origin=Match[str], alias=alias or "regex[:group]")  # type: ignore
        self.regex_pattern = re.compile(pattern)
        self.pattern = self.regex_pattern.pattern

    def match(self, input_: Any) -> Match[str]:
        if not isinstance(input_, str):
            raise MatchFailed(
                lang.require("nepattern", "type_error").format(target=input_)
            )
        if mat := self.regex_pattern.match(input_):
            return mat
        raise MatchFailed(
            lang.require("nepattern", "content_error").format(target=input_)
        )


class UnionPattern(BasePattern):
    """多类型参数的匹配"""

    optional: bool
    base: list[BasePattern | object | str]
    for_validate: list[BasePattern]
    for_equal: list[str | object]

    def __init__(self, base: Iterable[BasePattern | object | str], anti: bool = False):
        self.base = list(base)
        self.optional = False
        self.for_validate = []
        self.for_equal = []

        for arg in self.base:
            if arg == Empty:
                self.optional = True
                self.for_equal.append(None)
            elif isinstance(arg, BasePattern):
                self.for_validate.append(arg)
            else:
                self.for_equal.append(arg)
        alias_content = "|".join(
            [repr(a) for a in self.for_validate] + [repr(a) for a in self.for_equal]
        )
        super().__init__(model=MatchMode.KEEP, origin=str, alias=alias_content, anti=anti)

    def match(self, text: Any):
        if not text:
            text = None
        if text not in self.for_equal:
            for pat in self.for_validate:
                if (res := pat.validate(text)).success:
                    return res.value
            raise MatchFailed(
                lang.require("nepattern", "content_error").format(target=text)
            )
        return text

    def __calc_repr__(self):
        return ("!" if self.anti else "") + (
            "|".join(repr(a) for a in (*self.for_validate, *self.for_equal))
        )

    def prefixed(self) -> UnionPattern:
        from .main import type_parser

        return UnionPattern(
            [pat.prefixed() for pat in self.for_validate]
            + [
                type_parser(eq).prefixed() if isinstance(eq, str) else eq  # type: ignore
                for eq in self.for_equal
            ],
            self.anti,
        )

    def suffixed(self) -> UnionPattern:
        from .main import type_parser

        return UnionPattern(
            [pat.suffixed() for pat in self.for_validate]
            + [
                type_parser(eq).suffixed() if isinstance(eq, str) else eq  # type: ignore
                for eq in self.for_equal
            ],
            self.anti,
        )


TSeq = TypeVar("TSeq", list, tuple, set)


class SequencePattern(BasePattern[TSeq]):
    """匹配列表或者元组或者集合"""

    base: BasePattern
    _mode: Literal["pre", "suf", "all"]

    def __init__(self, form: type[TSeq], base: BasePattern):
        self.base = base
        self._mode = "all"
        if form is list:
            super().__init__(
                r"\[(.+?)\]", MatchMode.REGEX_CONVERT, form, alias=f"list[{base}]"
            )
        elif form is tuple:
            super().__init__(
                r"\((.+?)\)", MatchMode.REGEX_CONVERT, form, alias=f"tuple[{base}]"
            )
        elif form is set:
            super().__init__(
                r"\{(.+?)\}", MatchMode.REGEX_CONVERT, form, alias=f"set[{base}]"
            )
        else:
            raise ValueError(
                lang.require("nepattern", "sequence_form_error").format(
                    target=str(form)
                )
            )

    def match(self, text: Any):
        _res = super().match(text)
        _max = 0
        success: list[tuple[int, Any]] = []
        fail: list[tuple[int, MatchFailed]] = []
        for _max, s in enumerate(
            re.split(r"\s*,\s*", _res) if isinstance(_res, str) else _res
        ):
            try:
                success.append((_max, self.base.match(s)))
            except MatchFailed:
                fail.append((_max, MatchFailed(f"{s} is not matched with {self.base}")))

        if (
            (self._mode == "all" and fail)
            or (self._mode == "pre" and fail and fail[0][0] == 0)
            or (self._mode == "suf" and fail and fail[-1][0] == _max)
        ):
            raise fail[0][1]
        if self._mode == "pre" and fail:
            return self.origin(i[1] for i in success if i[0] < fail[0][0])
        if self._mode == "suf" and fail:
            return self.origin(i[1] for i in success if i[0] > fail[-1][0])
        return self.origin(i[1] for i in success)

    def __calc_repr__(self):
        return f"{self.origin.__name__}[{self.base}]"

    def prefixed(self) -> SequencePattern:
        self._mode = "pre"
        return super(SequencePattern, self).prefixed()

    def suffixed(self) -> SequencePattern:
        self._mode = "suf"
        return super(SequencePattern, self).suffixed()


TKey = TypeVar("TKey")
TVal = TypeVar("TVal")


class MappingPattern(BasePattern[Dict[TKey, TVal]]):
    """匹配字典或者映射表"""

    key: BasePattern[TKey]
    value: BasePattern[TVal]
    _mode: Literal["pre", "suf", "all"]

    def __init__(self, arg_key: BasePattern[TKey], arg_value: BasePattern[TVal]):
        self.key = arg_key
        self.value = arg_value
        self._mode = "all"
        super().__init__(
            r"\{(.+?)\}",
            MatchMode.REGEX_CONVERT,
            dict,
            alias=f"dict[{self.key}, {self.value}]",
        )
        self.converter = lambda _, x: x[1]

    def match(self, text: Any):
        _res = super().match(text)
        success: list[tuple[int, Any, Any]] = []
        fail: list[tuple[int, MatchFailed]] = []
        _max = 0

        def _generator_items(res: str | dict):
            if isinstance(res, dict):
                yield from res.items()
                return
            for m in re.split(r"\s*,\s*", res):
                yield re.split(r"\s*[:=]\s*", m)

        for _max, item in enumerate(_generator_items(_res)):
            k, v = item
            try:
                success.append((_max, self.key.match(k), self.value.match(v)))
            except MatchFailed:
                fail.append(
                    (
                        _max,
                        MatchFailed(
                            f"{k}: {v} is not matched with {self.key}: {self.value}"
                        ),
                    )
                )
        if (
            (self._mode == "all" and fail)
            or (self._mode == "pre" and fail and fail[0][0] == 0)
            or (self._mode == "suf" and fail and fail[-1][0] == _max)
        ):
            raise fail[0][1]
        if self._mode == "pre" and fail:
            return {i[1]: i[2] for i in success if i[0] < fail[0][0]}
        if self._mode == "suf" and fail:
            return {i[1]: i[2] for i in success if i[0] > fail[-1][0]}
        return {i[1]: i[2] for i in success}

    def __calc_repr__(self):
        return f"dict[{self.key.origin.__name__}, {self.value}]"

    def prefixed(self) -> MappingPattern:
        self._mode = "pre"
        return super(MappingPattern, self).prefixed()

    def suffixed(self) -> MappingPattern:
        self._mode = "suf"
        return super(MappingPattern, self).suffixed()


_TCase = TypeVar("_TCase")


class SwitchPattern(BasePattern[_TCase]):
    switch: dict[Any, _TCase]

    def __init__(self, data: dict[Any | ellipsis, _TCase]):
        self.switch = data
        super().__init__(model=MatchMode.TYPE_CONVERT, origin=type(list(data.values())[0]))

    def __calc_repr__(self):
        return "|".join(f"{k}" for k in self.switch if k != Ellipsis)

    def match(self, input_: Any) -> _TCase:
        try:
            return self.switch[input_]
        except KeyError as e:
            if Ellipsis in self.switch:
                return self.switch[...]
            raise MatchFailed(
                lang.require("nepattern", "content_error").format(target=input_)
            ) from e


__all__ = [
    "DirectPattern",
    "RegexPattern",
    "UnionPattern",
    "SequencePattern",
    "MappingPattern",
    "SwitchPattern",
]
