from __future__ import annotations

from collections import OrderedDict
from typing import Any, Callable, Generic, Hashable, Iterable, TypeVar, overload

_KT = TypeVar("_KT", bound=Hashable)
_VT = TypeVar("_VT")
_T = TypeVar("_T")


class LRU(Generic[_KT, _VT]):
    __slots__ = ("__max", "__cache", "__size", "__callback")

    def __init__(
        self, size: int, callback: Callable[[_KT, _VT], Any] | None = None
    ) -> None:
        if size < 1:
            raise ValueError("Size should be a positive number")
        self.__max = size
        self.__cache = OrderedDict()
        self.__size = 0
        self.__callback = callback

    def clear(self) -> None:
        self.__cache.clear()

    @overload
    def get(self, key: _KT) -> _VT | None:
        ...

    @overload
    def get(self, key: _KT, instead: _VT | _T) -> _VT | _T:
        ...

    def get(self, key: _KT, instead: _VT | _T | None = None):
        if key in self.__cache:
            self.__cache.move_to_end(key, last=False)
            return self.__cache[key]
        return instead

    def get_size(self) -> int:
        return self.__max

    def has_key(self, key: _KT) -> bool:
        return key in self.__cache

    def keys(self) -> list[_KT]:
        return list(self.__cache.keys())

    def values(self) -> list[_VT]:
        return list(self.__cache.values())

    def items(self) -> list[tuple[_KT, _VT]]:
        return list(self.__cache.items())

    def peek_first_item(self) -> tuple[_KT, _VT] | None:
        return self.items()[0] if self.__cache else None

    def peek_last_item(self) -> tuple[_KT, _VT] | None:
        return self.items()[-1] if self.__cache else None

    @overload
    def pop(self, key: _KT) -> _VT | None:
        ...

    @overload
    def pop(self, key: _KT, default: _VT | _T) -> _VT | _T:
        ...

    def pop(self, key: _KT, default: _VT | _T | None = None):
        return self.__cache.pop(key, default)

    def popitem(self, least_recent: bool = True) -> tuple[_KT, _VT]:
        return self.__cache.popitem(last=least_recent)

    @overload
    def setdefault(self: LRU[_KT, _T | None], key: _KT) -> _T | None:
        ...

    @overload
    def setdefault(self, key: _KT, default: _VT) -> _VT:
        ...

    def setdefault(self, key: _KT, default: _VT | None = None):
        if key in self.__cache:
            return self.__cache[key]
        self.__setitem__(key, default)
        return default

    def set_callback(self, callback: Callable[[_KT, _VT], Any]) -> None:
        self.__callback = callback

    def set_size(self, size: int) -> None:
        self.__max = size
        if self.__max < self.__size:
            for _ in range(self.__size - self.__max):
                k, v = self.__cache.popitem(last=True)
                self.__size -= 1
                if self.__callback:
                    self.__callback(k, v)

    @overload
    def update(self, __m: Iterable[tuple[_KT, _VT]], **kwargs: _VT) -> None:
        ...

    @overload
    def update(self, **kwargs: _VT) -> None:
        ...

    def update(self, *args, **kwargs):
        self.__cache.update(*args, **kwargs)

    __contains__ = has_key

    def __delitem__(self, key: _KT) -> None:
        self.__cache.pop(key)

    def __getitem__(self, item: _KT) -> _VT:
        if item in self.__cache:
            self.__cache.move_to_end(item, last=False)
            return self.__cache[item]
        raise KeyError(item)

    def __len__(self) -> int:
        return len(self.__cache)

    def __repr__(self) -> str:
        return repr(self.__cache)

    def __setitem__(self, key: _KT, value: _VT) -> None:
        if key in self.__cache:
            self.__cache.move_to_end(key, last=False)
            self.__cache[key] = value
            return
        self.__cache[key] = value
        self.__cache.move_to_end(key, last=False)
        self.__size += 1
        if self.__max < self.__size:
            _k, _v = self.__cache.popitem(last=True)
            self.__size -= 1
            if self.__callback:
                self.__callback(_k, _v)
