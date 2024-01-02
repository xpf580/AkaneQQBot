from __future__ import annotations

import functools
import inspect
from typing import Any, Callable, Mapping


@functools.lru_cache(4096)
def get_signature(target: Callable):
    return inspect.signature(target).parameters.values()


try:
    from inspect import get_annotations  # type: ignore
except ImportError:

    def get_annotations(
        obj: Callable,
        *,
        _globals: Mapping[str, Any] | None = None,
        _locals: Mapping[str, Any] | None = None,
        eval_str: bool = False,
    ) -> dict[str, Any]:  # sourcery skip: avoid-builtin-shadow
        if not callable(obj):
            raise TypeError(f"{obj!r} is not a module, class, or callable.")

        ann = getattr(obj, "__annotations__", None)
        obj_globals = getattr(obj, "__globals__", None)
        obj_locals = None
        unwrap = obj
        if ann is None:
            return {}

        if not isinstance(ann, dict):
            raise ValueError(f"{unwrap!r}.__annotations__ is neither a dict nor None")
        if not ann:
            return {}

        if not eval_str:
            return dict(ann)

        if unwrap is not None:
            while True:
                if hasattr(unwrap, "__wrapped__"):
                    unwrap = unwrap.__wrapped__
                    continue
                if isinstance(unwrap, functools.partial):
                    unwrap = unwrap.func
                    continue
                break
            if hasattr(unwrap, "__globals__"):
                obj_globals = unwrap.__globals__

        if _globals is None:
            _globals = obj_globals
        if _locals is None:
            _locals = obj_locals

        return {
            key: eval(value, _globals, _locals)  # type: ignore
            if isinstance(value, str) else value
            for key, value in ann.items()
        }


@functools.lru_cache(4096)
def signatures(callable_target: Callable) -> list[tuple[str, Any, Any]]:
    callable_annotation = get_annotations(callable_target, eval_str=True)
    return [
        (
            param.name,
            (
                callable_annotation.get(param.name)
                if isinstance(param.annotation, str)
                else param.annotation
            )
            if param.annotation is not inspect.Signature.empty
            else None,
            param.default,
        )
        for param in get_signature(callable_target)
    ]
