from __future__ import annotations

from collections import UserDict
from contextvars import ContextVar, Token
from typing import final
from tarina import Empty

from .base import UnionPattern
from .util import AllParam


@final
class Patterns(UserDict):
    def __init__(self, name):
        self.name = name
        super().__init__({"": Empty, "*": AllParam})

    def set(self, target, alias=None, cover=True, no_alias=False):
        """
        增加可使用的类型转换器

        Args:
            target: 设置的表达式
            alias: 目标类型的别名
            cover: 是否覆盖已有的转换器
            no_alias: 是否不使用目标类型自带的别名
        """
        for k in {alias, None if no_alias else target.alias, target.origin}:
            if not k:
                continue
            if k not in self.data or cover:
                self.data[k] = target
            else:
                al_pat = self.data[k]
                self.data[k] = (
                    UnionPattern([*al_pat.base, target])
                    if isinstance(al_pat, UnionPattern)
                    else (UnionPattern([al_pat, target]))
                )

    def sets(self, patterns, cover=True, no_alias=False):
        for pat in patterns:
            self.set(pat, cover=cover, no_alias=no_alias)

    def merge(self, patterns, no_alias=False):
        for k in patterns:
            self.set(patterns[k], alias=k, no_alias=no_alias)

    def remove(self, origin_type, alias=None):
        if alias and (al_pat := self.data.get(alias)):
            if isinstance(al_pat, UnionPattern):
                self.data[alias] = UnionPattern(filter(lambda x: x.alias != alias, al_pat.base))  # type: ignore
                if not self.data[alias].base:  # type: ignore # pragma: no cover
                    del self.data[alias]
            else:
                del self.data[alias]
        elif al_pat := self.data.get(origin_type):
            if isinstance(al_pat, UnionPattern):
                self.data[origin_type] = UnionPattern(
                    filter(lambda x: x.origin != origin_type, al_pat.for_validate)
                )
                if not self.data[origin_type].base:  # type: ignore # pragma: no cover
                    del self.data[origin_type]
            else:
                del self.data[origin_type]


_ctx = {"$global": Patterns("$global")}
_ctx_token: Token

pattern_ctx: ContextVar[Patterns] = ContextVar("nepatterns")
_ctx_token = pattern_ctx.set(_ctx["$global"])


def create_local_patterns(name, data=None, set_current=True) -> Patterns:
    """
    新建一个本地表达式组

    Args:
        name: 组名
        data: 可选的初始内容
        set_current: 是否设置为 current
    """
    global _ctx_token
    if name.startswith("$"):
        raise ValueError(name)
    new = Patterns(name)
    new.update(data or {})
    _ctx[name] = new
    if set_current:
        pattern_ctx.reset(_ctx_token)
        _ctx_token = pattern_ctx.set(new)
    return new


def switch_local_patterns(name):
    global _ctx_token
    if name.startswith("$"):
        raise ValueError(name)
    target = _ctx[name]
    pattern_ctx.reset(_ctx_token)
    _ctx_token = pattern_ctx.set(target)


def reset_local_patterns():
    global _ctx_token

    target = _ctx["$global"]
    pattern_ctx.reset(_ctx_token)
    _ctx_token = pattern_ctx.set(target)


def local_patterns():
    local = pattern_ctx.get()
    return local if local.name != "$global" else Patterns("$temp")


def global_patterns():
    return _ctx["$global"]


def all_patterns():
    """获取 global 与 local 的合并表达式组"""
    new = Patterns("$temp")
    new.update(global_patterns().data)
    local = local_patterns()
    if not local.name.startswith("$"):
        new.update(local_patterns().data)
    return new


__all__ = [
    "Patterns",
    "local_patterns",
    "global_patterns",
    "all_patterns",
    "switch_local_patterns",
    "create_local_patterns",
    "reset_local_patterns",
]
