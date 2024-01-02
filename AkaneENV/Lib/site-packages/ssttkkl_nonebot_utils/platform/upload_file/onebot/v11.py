from __future__ import annotations
from typing import TYPE_CHECKING

from ....requires import silently_requires

if TYPE_CHECKING:
    from os import PathLike
    from typing import Union, AsyncIterable, Iterator

    from nonebot import Bot
    from nonebot.internal.adapter import Event


async def upload_file(bot: Bot, event: Event, filename: str,
                      data: Union[None, bytes, str,
                      AsyncIterable[Union[str, bytes]],
                      Iterator[Union[str, bytes]]] = None,
                      path: Union[None, str, PathLike[str]] = None):
    silently_requires("nonebot_plugin_gocqhttp_cross_machine_upload_file")

    from nonebot_plugin_gocqhttp_cross_machine_upload_file import upload_file as do_update_file
    return await do_update_file(bot, event, filename, data, path)


__all__ = ("upload_file",)
