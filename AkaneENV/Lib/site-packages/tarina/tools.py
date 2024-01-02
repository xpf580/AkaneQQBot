from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Generator,
    Iterable,
    Literal,
    TypeVar,
    overload,
)

from typing_extensions import ParamSpec, Concatenate

from .guard import is_async

T = TypeVar("T")


def group_dict(iterable: Iterable, key_callable: Callable[[Any], Any]):
    temp = {}
    for i in iterable:
        k = key_callable(i)
        temp.setdefault(k, []).append(i)
    return temp


async def run_always_await(
    target: Callable[..., Any] | Callable[..., Awaitable[Any]], *args, **kwargs
) -> Any:
    obj = target(*args, **kwargs)
    if is_async(target) or is_async(obj):
        obj = await obj
    return obj


def gen_subclass(cls: type[T]) -> Generator[type[T], None, None]:
    """生成某个类的所有子类 (包括其自身)
    Args:
        cls (Type[T]): 类
    Yields:
        Type[T]: 子类
    """
    yield cls
    for sub_cls in cls.__subclasses__():
        if TYPE_CHECKING:
            assert issubclass(sub_cls, cls)
        yield from gen_subclass(sub_cls)


R = TypeVar("R")
P = ParamSpec("P")


@overload
def init_spec(fn: Callable[P, T]) -> Callable[[Callable[[T], R]], Callable[P, R]]:
    ...


@overload
def init_spec(
    fn: Callable[P, T], is_method: Literal[True]
) -> Callable[[Callable[[Any, T], R]], Callable[Concatenate[Any, P], R]]:
    ...


def init_spec(  # type: ignore
    fn: Callable[P, T], is_method: bool = False
) -> Callable[[Callable[[T], R] | Callable[[Any, T], R]], Callable[P, R] | Callable[Concatenate[Any, P], R]]:
    def wrapper(func: Callable[[T], R] | Callable[[Any, T], R]) -> Callable[P, R] | Callable[Concatenate[Any, P], R]:
        def inner(*args: P.args, **kwargs: P.kwargs):
            if is_method:
                return func(args[0], fn(*args[1:], **kwargs))  # type: ignore
            return func(fn(*args, **kwargs))  # type: ignore

        return inner

    return wrapper
