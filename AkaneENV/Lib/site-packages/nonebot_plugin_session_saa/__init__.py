from typing import Optional

from nonebot import require
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_saa")
require("nonebot_plugin_session")

__plugin_meta__ = PluginMetadata(
    name="session 插件 saa 扩展",
    description="提供从 session 获取 saa target 的方法",
    usage="请参考文档",
    type="library",
    homepage="https://github.com/noneplugin/nonebot-plugin-session-saa",
    supported_adapters=inherit_supported_adapters(
        "nonebot_plugin_saa", "nonebot_plugin_session"
    ),
)


from nonebot_plugin_saa import (
    PlatformTarget,
    TargetFeishuGroup,
    TargetFeishuPrivate,
    TargetKaiheilaChannel,
    TargetKaiheilaPrivate,
    TargetOB12Unknow,
    TargetQQGroup,
    TargetQQGuildChannel,
    TargetQQGuildDirect,
    TargetQQPrivate,
)
from nonebot_plugin_session import Session, SessionLevel
from nonebot_plugin_session.const import SupportedAdapter, SupportedPlatform


def get_saa_target(session: Session) -> Optional[PlatformTarget]:
    if session.platform == SupportedPlatform.qq:
        if session.level == SessionLevel.LEVEL1 and session.id1:
            return TargetQQPrivate(user_id=int(session.id1))
        elif session.level == SessionLevel.LEVEL2 and session.id2:
            return TargetQQGroup(group_id=int(session.id2))

    elif session.platform == SupportedPlatform.qqguild:
        if session.level == SessionLevel.LEVEL1:
            if session.id1 and session.id3:
                return TargetQQGuildDirect(
                    recipient_id=int(session.id1), source_guild_id=int(session.id3)
                )
        elif session.level == SessionLevel.LEVEL3:
            if session.id2:
                return TargetQQGuildChannel(channel_id=int(session.id2))

    elif session.platform == SupportedPlatform.kaiheila:
        if session.level == SessionLevel.LEVEL1 and session.id1:
            return TargetKaiheilaPrivate(user_id=session.id1)
        if session.level == SessionLevel.LEVEL3 and session.id2:
            return TargetKaiheilaChannel(channel_id=session.id2)

    elif session.platform == SupportedPlatform.feishu:
        if session.level == SessionLevel.LEVEL1 and session.id1:
            return TargetFeishuPrivate(open_id=session.id1)
        elif session.level == SessionLevel.LEVEL2 and session.id2:
            return TargetFeishuGroup(chat_id=session.id2)

    if session.bot_type == SupportedAdapter.onebot_v12:
        if session.level == SessionLevel.LEVEL1 and session.id1:
            return TargetOB12Unknow(
                platform=session.platform, detail_type="private", user_id=session.id1
            )
        elif session.level == SessionLevel.LEVEL2 and session.id2:
            return TargetOB12Unknow(
                platform=session.platform, detail_type="group", group_id=session.id2
            )
        elif session.level == SessionLevel.LEVEL3 and session.id2 and session.id3:
            return TargetOB12Unknow(
                platform=session.platform,
                detail_type="channel",
                channel_id=session.id2,
                guild_id=session.id3,
            )
