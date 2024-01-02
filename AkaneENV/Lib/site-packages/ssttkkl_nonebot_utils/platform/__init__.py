import importlib

from .func_manager import FuncManagerFactory
from ..nonebot import except_log_only_if_trace

platform_func = FuncManagerFactory()

supported_platform = ("onebot.v11", "kaiheila", "qqguild")

for func_name in (
        "is_destination_available",
        "handling_reaction",
        "get_user_nickname",
        "is_group_admin",
        "extract_mention_user",
        "upload_file",
        "send_msgs"
):
    @except_log_only_if_trace(ImportError, f"failed to register {func_name} for all platform")
    def register():
        func_module = importlib.import_module("ssttkkl_nonebot_utils.platform." + func_name)
        for platform in supported_platform:
            @except_log_only_if_trace(ImportError, f"failed to register {func_name} for {platform}")
            def register_for_platform():
                nonlocal func_module
                func_module = importlib.import_module(f"ssttkkl_nonebot_utils.platform.{func_name}.{platform}")
                adapter_module = importlib.import_module(f"nonebot.adapters.{platform}")
                platform_func.register(adapter_module.Adapter.get_name(), func_name, getattr(func_module, func_name))

            register_for_platform()

        @except_log_only_if_trace(ImportError, f"failed to register {func_name} for fallback")
        def register_fallback():
            nonlocal func_module
            func_module = importlib.import_module(f"ssttkkl_nonebot_utils.platform.{func_name}.fallback")
            platform_func.register("fallback", func_name, getattr(func_module, func_name))

        register_fallback()


    register()
__all__ = ("platform_func",)
