#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/3/27 19:23
# @Author  : QingXuanJun
# @File    : system_utils.py

import platform

def enter_back() -> None:
    """等待用户输入Enter键返回上一级"""
    input("\033[32m输入Enter返回...\033[0m")

def get_sys_arch() -> str:
    """获取系统架构类型

    Returns:
        str: 架构类型（ARM64、ARM32、X86、X86_64或未知架构）
    """
    # 判断架构类型
    if platform.machine() in ["arm64", "aarch64"]:
        return "ARM64"
    elif platform.machine() in ["arm", "armv7l", "armv8l"]:
        return "ARM32"
    elif platform.machine() in ["i386", "i686"]:
        return "X86"
    elif platform.machine() in ["x86_64", "amd64", "AMD64"]:
        return "X86_64"
    else:
        return "Unknown Architecture(未知系统架构)"


def identify_os() -> str:
    """检测操作系统类型

    Returns:
        str: 操作系统类型（Windows、Linux、MacOS或Unknown OS）
    """
    os_name = platform.system()
    if os_name == 'Windows':
        return 'Windows'
    elif os_name == 'Linux':
        return 'Linux'
    elif os_name == 'Darwin':
        return 'MacOS'
    else:
        return 'Unknown OS'
