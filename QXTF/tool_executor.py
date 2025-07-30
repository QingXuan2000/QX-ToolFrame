#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/3/27 19:23
# @Author  : QingXuanJun
# @File    : tool_executor.py

import subprocess
from typing import Optional

from QXTF.config_handler import ConfigUtils
from QXTF.menu_engine import logo, get_text
from QXTF.system_utils import get_sys_arch, enter_back

# 加载配置
tools_config = ConfigUtils("./config/config.json").get_json()
settings = tools_config.get("settings", {})


def get_start_command(data: dict, index: int, arch: str) -> str:
    """获取指定索引和架构的工具启动命令

    Args:
        data: 工具配置数据
        index: 工具索引
        arch: 系统架构

    Returns:
        str: 启动命令

    Raises:
        IndexError: 当命令未找到时
    """
    for tool_name, tool_info in data.get("tools", {}).items():
        if tool_info.get("index") == index:
            return tool_info["start_command"].get(arch)
    raise IndexError("Command not found for the specified index or architecture.")


def arch_picker() -> Optional[str]:
    if settings.get("arch_picker"):
        logo()
        print(get_text(settings.get("arch_picker_ui")))
        try:
            user_arch = int(input('>>> '))
            if user_arch == 1:
                return "ARM64"
            elif user_arch == 2:
                return "ARM32"
            elif user_arch == 3:
                return "X86"
            elif user_arch == 4:
                return "X86_64"
            else:
                # 无效数字输入时抛出异常
                raise ValueError(f"\033[31m无效的架构选择!\033[0m")
        except ValueError as e:
            # 捕获输入非数字的情况
            raise ValueError(f"\033[31m输入错误: {str(e)}\033[0m") from e
    return None

def sub_menu(menu_config: str, user_option: int) -> None:
    """子菜单处理 - 使用标准库subprocess执行命令"""
    tools = ConfigUtils(menu_config).json_data
    try:
        if settings.get("arch_picker"):
            command = get_start_command(tools, user_option, arch_picker())
        else:
            command = get_start_command(tools, user_option, get_sys_arch())

        if command is None:
            print("\033[31m软件不支持该架构!\033[0m")
        elif command is not None:
            # 使用标准库subprocess执行命令
            result = subprocess.run(command, shell=True)

            if result.returncode != 0:
                print(f"\033[31m命令执行失败，返回码：{result.returncode}\033[0m")
    except Exception as e:
        print(f"\033[31m执行命令时出错：{str(e)}\033[0m")
    enter_back()
