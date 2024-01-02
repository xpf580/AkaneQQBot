from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar, Token
from typing import Generic, TypeVar

T = TypeVar("T")
D = TypeVar("D")


class ContextModel(Generic[T]):
    current_ctx: ContextVar[T]

    def __init__(self, name: str) -> None:
        self.current_ctx = ContextVar(name)

    def get(self, default: T | D | None = None) -> T | D:
        return self.current_ctx.get(default)

    def set(self, value: T):
        return self.current_ctx.set(value)

    def reset(self, token: Token):
        return self.current_ctx.reset(token)

    @contextmanager
    def use(self, value: T):
        token = self.set(value)
        yield
        self.reset(token)
