from collections import UserDict
from typing import Any, Iterable, final
from tarina import Empty

from .core import BasePattern


@final
class Patterns(UserDict[Any, BasePattern]):
    name: str
    def __init__(self, name: str): ...
    def set(
        self,
        target: BasePattern,
        alias: str | None = None,
        cover: bool = True,
        no_alias=False
    ):
        """
        增加可使用的类型转换器

        Args:
            target: 设置的表达式
            alias: 目标类型的别名
            cover: 是否覆盖已有的转换器
            no_alias: 是否不使用目标类型自带的别名
        """
        ...
    def sets(self, patterns: Iterable[BasePattern], cover: bool = True, no_alias=False): ...
    def merge(self, patterns: dict[str, BasePattern], no_alias=False): ...
    def remove(self, origin_type: type, alias: str | None = None): ...

def create_local_patterns(
    name: str,
    data: dict[Any, BasePattern | type[Empty]] | None = None,
    set_current: bool = True,
) -> Patterns:
    """
    新建一个本地表达式组

    Args:
        name: 组名
        data: 可选的初始内容
        set_current: 是否设置为 current
    """
    ...

def switch_local_patterns(name: str) -> None: ...
def reset_local_patterns() -> None: ...
def local_patterns() -> Patterns: ...
def global_patterns() -> Patterns: ...
def all_patterns() -> Patterns:
    """获取 global 与 local 的合并表达式组"""
