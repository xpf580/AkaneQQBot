from nonebot import require

from ssttkkl_nonebot_utils.nonebot import except_log_only_if_trace


@except_log_only_if_trace(RuntimeError)
def silently_requires(plugin_name: str):
    require(plugin_name)
