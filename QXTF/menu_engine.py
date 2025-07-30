#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2025/3/24 23:25
# @Author   : QingXuanJun
# @File     : menu_engine.py

import subprocess
from typing import Any, Union

import QXTF.config_handler
from QXTF.system_utils import identify_os

# 初始化ConfigUtils并直接获取JSON数据
tools_config = QXTF.config_handler.ConfigUtils("./config/config.json").get_json()
settings = tools_config.get("settings", {})


class MenuUtils:
    """菜单工具类，用于根据索引查找工具配置"""
    def __init__(self, idx_num: int, key: str, val: str, tools: dict) -> None:
        """初始化MenuUtils实例

        Args:
            idx_num: 索引编号
            key: 查找键
            val: 返回值键
            tools: 工具配置字典
        """
        self.idx_num = idx_num
        self.key = key
        self.val = val
        self.tools = tools  # 将 tools 作为类属性存储

    def find_val(self) -> Union[Any, None]:
        """根据索引查找对应的工具配置

        Returns:
            工具配置值或None
        """
        for tool in self.tools.values():
            if tool.get(self.key) == self.idx_num:
                return tool.get(self.val)
        return None


def get_sub_menu(sub_config: str) -> str:
    """获取子菜单"""
    sub_menu_config = QXTF.config_handler.ConfigUtils(sub_config)
    sub_menu_data = sub_menu_config.json_data.get("tools", {})
    sub_menu = []
    for tool in sub_menu_data.values():
        tools_name = tool.get("name", "None")
        sub_menu.append(tools_name)
    return "\n".join(sub_menu)


def menu(tools_dict: dict) -> str:
    """生成主菜单"""
    menu = []
    for tool in tools_dict.values():
        tools_name = tool.get("name", "None")
        menu.append(tools_name)
    return "\n".join(menu)

def clear() -> None:
    """清屏"""
    display_clear = settings.get("display_clear")
    if identify_os() == "Windows":
        subprocess.run("cls", shell=True)
    else:
        subprocess.run("clear", shell=True)


def get_text(text_path: str) -> str:
    """从文本文件中提取指定标记间的内容

    Args:
        text_path: 文本文件路径

    Returns:
        str: 提取的文本内容
    """
    text = []
    capture = False
    with open(text_path, "r", encoding="utf-8") as f:
        for line in f:
            if "#--Start" in line:
                capture = True
            elif "#--End" in line:
                capture = False
            elif capture:
                text.append(line)
        return "".join(text)


def logo() -> None:
    """显示Logo"""
    display_logo = settings.get("display_logo")
    clear()
    if display_logo:
        print(get_text(settings.get("logo_path")))
