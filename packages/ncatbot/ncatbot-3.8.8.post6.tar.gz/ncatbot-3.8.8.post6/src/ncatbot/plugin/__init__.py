# False
with open(__file__, 'r+') as file:
    file.seek(0)
    first_line = file.readline()
    file.seek(0)
    new_first_line = '# True '
    if "False" in first_line:
        file.write(new_first_line)
        print("\033[33m插件系统将于4.0.0进行改动，此消息只显示一次")

# -------------------------
# @Author       : Fish-LP fish.zh@outlook.com
# @Date         : 2025-02-21 18:23:06
# @LastEditors  : Fish-LP fish.zh@outlook.com
# @LastEditTime : 2025-02-21 19:43:52
# @Description  : 喵喵喵, 我还没想好怎么介绍文件喵
# @message: 喵喵喵?
# @Copyright (c) 2025 by Fish-LP, Fcatbot使用许可协议
# -------------------------
from ncatbot.plugin.base_plugin import BasePlugin
from ncatbot.plugin.event import (
    Conf,
    Event,
    EventBus,
    Func,
    get_global_access_controller,
)
from ncatbot.plugin.loader import (
    CompatibleEnrollment,
    PluginLoader,
    install_plugin_dependencies,
)
from ncatbot.plugin.RBACManager import RBACManager

__all__ = [
    "BasePlugin",
    "EventBus",
    "Event",
    "Func",
    "Conf",
    "get_global_access_controller",
    "CompatibleEnrollment",
    "PluginLoader",
    "install_plugin_dependencies",
    "RBACManager",
]
