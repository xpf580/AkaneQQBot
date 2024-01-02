from nonebot import require
from nonebot.plugin import PluginMetadata, inherit_supported_adapters

require("nonebot_plugin_orm")
require("nonebot_plugin_session")

from . import migrations
from .model import SessionModel, get_session_by_persist_id, get_session_persist_id

__plugin_meta__ = PluginMetadata(
    name="session 插件 orm 扩展",
    description="为 session 提供数据库模型及存取方法",
    usage="请参考文档",
    type="library",
    homepage="https://github.com/noneplugin/nonebot-plugin-session-orm",
    supported_adapters=inherit_supported_adapters("nonebot_plugin_session"),
    extra={"orm_version_location": migrations},
)
