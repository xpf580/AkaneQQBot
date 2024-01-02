import os
import sys

__all__ = ("LRU",)


NO_EXTENSIONS = bool(os.environ.get("TARINA_NO_EXTENSIONS"))  # type: bool
if sys.implementation.name != "cpython":
    NO_EXTENSIONS = True


if not NO_EXTENSIONS:  # pragma: no branch
    try:
        from ._lru_c import LRU as LRU  # type: ignore[misc]
    except Exception:  # pragma: no cover
        from ._lru_py import LRU as LRU  # type: ignore[misc]
else:
    from ._lru_py import LRU as LRU  # type: ignore[misc]
