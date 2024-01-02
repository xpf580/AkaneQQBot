from __future__ import annotations

import re
from copy import deepcopy
from enum import Enum, IntEnum
from typing import Any, Callable, Generic, TypeVar, Literal, overload, TYPE_CHECKING

from tarina import Empty, generic_isinstance
from tarina.lang import lang
from typing_extensions import Annotated, Self, get_origin

from .exception import MatchFailed
from .util import TPattern


class MatchMode(IntEnum):
    """参数表达式匹配模式"""

    REGEX_CONVERT = 3
    """正则匹配并转换"""
    TYPE_CONVERT = 2
    """传入值直接转换"""
    REGEX_MATCH = 1
    """正则匹配"""
    KEEP = 0
    """保持传入值"""


class ResultFlag(str, Enum):
    """参数表达式验证结果标识符"""

    VALID = "valid"
    "验证通过"
    ERROR = "error"
    "验证失败"
    DEFAULT = "default"
    "默认值"


T = TypeVar("T")
TOrigin = TypeVar("TOrigin")
TVOrigin = TypeVar("TVOrigin")
TDefault = TypeVar("TDefault")


class ValidateResult(Generic[TVOrigin]):
    """参数表达式验证结果"""
    def __init__(
        self,
        value: TVOrigin | type[Empty] = Empty,
        error: Exception | type[Empty] = Empty,
        flag: ResultFlag = ResultFlag.VALID,
    ):
        self._value = value
        self._error = error
        self.flag = flag

    __slots__ = ("_value", "_error", "flag")

    @property
    def value(self) -> TVOrigin:
        if self.flag == ResultFlag.ERROR or self._value == Empty:
            raise RuntimeError("cannot access value")
        return self._value  # type: ignore

    @property
    def error(self) -> Exception | None:
        if self.flag == ResultFlag.ERROR and self._error != Empty:
            assert isinstance(self._error, Exception)
            return self._error

    @property
    def success(self) -> bool:
        return self.flag == ResultFlag.VALID

    @property
    def failed(self) -> bool:
        return self.flag == ResultFlag.ERROR

    @property
    def or_default(self) -> bool:
        return self.flag == ResultFlag.DEFAULT

    @overload
    def step(self, other: BasePattern[T]) -> ValidateResult[T]:
        ...

    @overload
    def step(self, other: type[T]) -> T:
        ...

    @overload
    def step(self, other: Callable[[TVOrigin], T]) -> T:
        ...

    @overload
    def step(self, other: Any) -> Self:
        ...

    def step(
        self, other: type[T] | Callable[[TVOrigin], T] | Any | BasePattern[T]
    ) -> T | Self | ValidateResult[T]:
        if other is bool:
            return self.success  # type: ignore
        if callable(other) and self.success:
            return other(self.value)
        return other.exec(self.value) if isinstance(other, BasePattern) else self

    @overload
    def __rshift__(self, other: BasePattern[T]) -> ValidateResult[T]:
        ...

    @overload
    def __rshift__(self, other: type[T]) -> T:
        ...

    @overload
    def __rshift__(self, other: Callable[[TVOrigin], T]) -> T:
        ...

    @overload
    def __rshift__(self, other: Any) -> Self:
        ...

    def __rshift__(
        self, other: type[T] | Callable[[TVOrigin], T] | Any
    ) -> T | Self | ValidateResult[T]:
        return self.step(other)  # type: ignore

    def __bool__(self):
        return self.success

    def __repr__(self):
        if self.flag == ResultFlag.VALID:
            return f"ValidateResult(value={self._value!r})"
        if self.flag == ResultFlag.ERROR:
            return f"ValidateResult(error={self._error!r})"
        return f"ValidateResult(default={self._value!r})"


class BasePattern(Generic[TOrigin]):
    """对参数类型值的包装"""

    regex_pattern: TPattern  # type: ignore
    pattern: str
    mode: MatchMode
    converter: Callable[[BasePattern[TOrigin], Any], TOrigin | None]
    validators: list[Callable[[TOrigin], bool]]

    anti: bool
    origin: type[TOrigin]
    pattern_accepts: tuple[BasePattern, ...]
    type_accepts: tuple[type, ...]
    alias: str | None
    previous: BasePattern | None

    __slots__ = (
        "regex_pattern",
        "pattern",
        "mode",
        "converter",
        "anti",
        "origin",
        "pattern_accepts",
        "type_accepts",
        "alias",
        "previous",
        "validators",
        "_hash",
        "_repr",
        "_accept"
    )

    @overload
    def __init__(
        self,
        *,
        model: Literal[MatchMode.KEEP],
        origin: type[TOrigin] = Any,
        alias: str | None = None,
        previous: BasePattern | None = None,
        accepts: list[type | BasePattern] | None = None,
        validators: list[Callable[[TOrigin], bool]] | None = None,
        anti: bool = False,
    ):
        ...

    @overload
    def __init__(
        self,
        pattern: str,
        model: Literal[MatchMode.REGEX_MATCH],
        origin: type[TOrigin] = str,
        converter: Callable[[BasePattern[TOrigin], str], TOrigin | None] | None = None,
        alias: str | None = None,
        previous: BasePattern | None = None,
        accepts: list[type | BasePattern] | None = None,
        validators: list[Callable[[TOrigin], bool]] | None = None,
        anti: bool = False,
    ):
        ...

    @overload
    def __init__(
        self,
        pattern: str,
        model: Literal[MatchMode.REGEX_CONVERT],
        origin: type[TOrigin],
        converter: Callable[[BasePattern[TOrigin], re.Match[str]], TOrigin | None] | None = None,
        alias: str | None = None,
        previous: BasePattern | None = None,
        accepts: list[type | BasePattern] | None = None,
        validators: list[Callable[[TOrigin], bool]] | None = None,
        anti: bool = False,
    ):
        ...

    @overload
    def __init__(
        self,
        *,
        model: Literal[MatchMode.TYPE_CONVERT],
        origin: type[TOrigin],
        converter: Callable[[BasePattern[TOrigin], Any], TOrigin | None] | None = None,
        alias: str | None = None,
        previous: BasePattern | None = None,
        accepts: list[type | BasePattern] | None = None,
        validators: list[Callable[[TOrigin], bool]] | None = None,
        anti: bool = False,
    ):
        ...

    def __init__(
        self,
        pattern: str = ".+",
        model:  MatchMode = MatchMode.REGEX_MATCH,
        origin: type[TOrigin] = str,
        converter: Callable[[BasePattern[TOrigin], Any], TOrigin | None] | None = None,
        alias: str | None = None,
        previous: BasePattern | None = None,
        accepts: list[type | BasePattern] | None = None,
        validators: list[Callable[[TOrigin], bool]] | None = None,
        anti: bool = False,
    ):
        """
        初始化参数匹配表达式
        """
        if pattern.startswith("^") or pattern.endswith("$"):
            raise ValueError(
                lang.require("nepattern", "pattern_head_or_tail_error").format(
                    target=pattern
                )
            )
        self.pattern = pattern
        self.regex_pattern = re.compile(f"^{pattern}$")
        self.mode = MatchMode(model)
        self.origin = origin
        self.alias = alias
        self.previous = previous
        accepts = accepts or []
        self.pattern_accepts = tuple(
            filter(lambda x: isinstance(x, BasePattern), accepts)  # type: ignore
        )
        self.type_accepts = tuple(
            filter(lambda x: not isinstance(x, BasePattern), accepts)  # type: ignore
        )
        self.converter = converter or (
            lambda _, x: (get_origin(origin) or origin)(x)
            if model == MatchMode.TYPE_CONVERT
            else eval(x[0])
        )
        self.validators = validators or []
        self.anti = anti
        self._repr = self.__calc_repr__()
        self._hash = hash(self._repr)
        if not self.pattern_accepts and not self.type_accepts:
            self._accept = lambda _: True
        elif not self.pattern_accepts:
            self._accept = lambda x: generic_isinstance(x, self.type_accepts)
        elif not self.type_accepts:
            self._accept = lambda x: any(map(lambda y: y.exec(x).flag == 'valid', self.pattern_accepts))
        else:
            self._accept = lambda x: (
                generic_isinstance(x, self.type_accepts) or
                any(map(lambda y: y.exec(x).flag == 'valid', self.pattern_accepts))
            )

    def __calc_repr__(self):
        if self.mode == MatchMode.KEEP:
            if self.alias:
                return self.alias
            return (
                "Any"
                if not self.type_accepts and not self.pattern_accepts
                else "|".join(
                    [x.__name__ for x in self.type_accepts]
                    + [x.__repr__() for x in self.pattern_accepts]
                )
            )

        if not self.alias:
            name = getattr(self.origin, "__name__", str(self.origin))
            if self.mode == MatchMode.REGEX_MATCH:
                text = self.pattern
            elif self.mode == MatchMode.REGEX_CONVERT or (
                not self.type_accepts and not self.pattern_accepts
            ):
                text = name
            else:
                text = (
                    "|".join(
                        [x.__name__ for x in self.type_accepts]
                        + [x.__repr__() for x in self.pattern_accepts]
                    )
                    + f" -> {name}"
                )
        else:
            text = self.alias
        return (
            f"{f'{self.previous.__repr__()} -> ' if self.previous and id(self.previous) != id(self) else ''}"
            f"{'!' if self.anti else ''}{text}"
        )

    def __repr__(self):
        return self._repr

    def __str__(self):
        return self._repr

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        return isinstance(other, BasePattern) and self._repr == other._repr

    @staticmethod
    def of(unit: type[TOrigin]) -> BasePattern[TOrigin]:
        """提供 Type[DataUnit] 类型的构造方法"""
        return BasePattern(
            model=MatchMode.KEEP, origin=unit, alias=unit.__name__, accepts=[unit]
        )

    @staticmethod
    def on(obj: TOrigin) -> BasePattern[TOrigin]:
        """提供 DataUnit 类型的构造方法"""
        from .base import DirectPattern

        return DirectPattern(obj)

    @staticmethod
    def to(content: Any) -> BasePattern:
        """便捷的使用 type_parser 的方法"""
        from .main import type_parser

        res = type_parser(content, "allow")
        return res if isinstance(res, BasePattern) else type_parser(Any)

    def reverse(self) -> Self:
        """改变 pattern 的 anti 值"""
        self.anti = not self.anti
        self._repr = self.__calc_repr__()
        self._hash = hash(self._repr)
        return self

    def prefixed(self):
        """让表达式能在某些场景下实现前缀匹配; 返回自身的拷贝"""
        cp_self = deepcopy(self)
        if self.mode in (MatchMode.REGEX_MATCH, MatchMode.REGEX_CONVERT):
            cp_self.regex_pattern = re.compile(f"^{self.pattern}")
        return cp_self

    def suffixed(self):
        """让表达式能在某些场景下实现后缀匹配; 返回自身的拷贝"""
        cp_self = deepcopy(self)
        if self.mode in (MatchMode.REGEX_MATCH, MatchMode.REGEX_CONVERT):
            cp_self.regex_pattern = re.compile(f"{self.pattern}$")
        return cp_self

    def match(self, input_: Any) -> TOrigin:
        """
        对传入的参数进行匹配, 如果匹配成功, 则返回转换后的值, 否则返回None
        """
        if (
            self.mode > 1
            and self.origin is not str and self.origin is not Any
            and generic_isinstance(input_, self.origin)
        ):
            return input_  # type: ignore
        if not self._accept(input_):
            if not self.previous or not self._accept(input_ := self.previous.match(input_)):  # pragma: no cover
                raise MatchFailed(
                    lang.require("nepattern", "type_error").format(
                        target=input_.__class__
                    )
                )
        if self.mode == 0:
            return input_  # type: ignore
        if self.mode == 2:
            res = self.converter(self, input_)
            if res is None and self.origin is Any:  # pragma: no cover
                raise MatchFailed(
                    lang.require("nepattern", "content_error").format(target=input_)
                )
            if not generic_isinstance(res, self.origin):
                if not self.previous or not generic_isinstance(
                    res := self.converter(self, self.previous.match(input_)),
                    self.origin,
                ):
                    raise MatchFailed(
                        lang.require("nepattern", "content_error").format(target=input_)
                    )
            if TYPE_CHECKING:
                assert res is not None
            return res
        if input_.__class__ is not str:
            if not self.previous or not isinstance(input_ := self.previous.match(input_), str):
                raise MatchFailed(
                    lang.require("nepattern", "type_error").format(target=type(input_))
                )
        if mat := (self.regex_pattern.match(input_) or self.regex_pattern.search(input_)):
            if self.mode == 1:
                return mat[0]  # type: ignore
            if (res := self.converter(self, mat)) is not None:
                return res
        raise MatchFailed(
            lang.require("nepattern", "content_error").format(target=input_)
        )

    @overload
    def validate(self, input_: Any) -> ValidateResult[TOrigin]:
        ...

    @overload
    def validate(
        self, input_: Any, default: TDefault
    ) -> ValidateResult[TOrigin | TDefault]:
        ...

    def validate(  # type: ignore
        self, input_: Any, default: TDefault | None = None
    ) -> ValidateResult[TOrigin | TDefault]:
        """
        对传入的值进行正向验证，返回可能的匹配与转化结果。

        若传入默认值，验证失败会返回默认值
        """
        try:
            res = self.match(input_)
            if self.validators and not all(i(res) for i in self.validators):
                raise MatchFailed(
                    lang.require("nepattern", "content_error").format(target=input_)
                )
            return ValidateResult(value=res, flag=ResultFlag.VALID)
        except Exception as e:
            if default is None:
                return ValidateResult(error=e, flag=ResultFlag.ERROR)
            return ValidateResult(
                value=None if default is Empty else default, flag=ResultFlag.DEFAULT  # type: ignore
            )

    @overload
    def invalidate(self, input_: Any) -> ValidateResult[Any]:
        ...

    @overload
    def invalidate(
        self, input_: Any, default: TDefault
    ) -> ValidateResult[Any | TDefault]:
        ...

    def invalidate(
        self, input_: Any, default: TDefault | None = None
    ) -> ValidateResult[Any | TDefault]:
        """
        对传入的值进行反向验证，返回可能的匹配与转化结果。

        若传入默认值，验证失败会返回默认值
        """
        try:
            res = self.match(input_)
        except MatchFailed:
            return ValidateResult(value=input_, flag=ResultFlag.VALID)
        else:
            for i in self.validators:
                if not i(res):
                    return ValidateResult(value=input_, flag=ResultFlag.VALID)
            if default is None:
                return ValidateResult(
                    error=MatchFailed(
                        lang.require("nepattern", "content_error").format(target=input_)
                    ),
                    flag=ResultFlag.ERROR,
                )
            return ValidateResult(
                value=None if default is Empty else default, flag=ResultFlag.DEFAULT
            )

    @overload
    def exec(self, input_: Any) -> ValidateResult[TOrigin]:
        ...

    @overload
    def exec(
        self, input_: Any, default: TDefault
    ) -> ValidateResult[TOrigin | TDefault]:
        ...

    def exec(self, input_: Any, default: TDefault | None = None) -> ValidateResult[TOrigin | TDefault | None]:  # type: ignore
        """
        依据 anti 值 自动选择验证方式
        """
        if self.anti:
            return self.invalidate(input_, default)
        else:
            return self.validate(input_, default)

    def __rrshift__(self, other):
        return self.exec(other)

    def __rmatmul__(self, other) -> Self:  # pragma: no cover
        if isinstance(other, str):
            self.alias = other
        return self

    def __matmul__(self, other) -> Self:  # pragma: no cover
        if isinstance(other, str):
            self.alias = other
        return self


def set_unit(
    target: type[TOrigin], predicate: Callable[..., bool]
) -> Annotated[TOrigin, ...]:
    """通过predicate区分同一个类的不同情况"""
    return Annotated[target, predicate]  # type: ignore


__all__ = ["MatchMode", "BasePattern", "set_unit", "ValidateResult", "TOrigin", "ResultFlag"]
