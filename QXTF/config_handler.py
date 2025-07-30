#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/3/27 19:23
# @Author  : QingXuanJun
# @File    : config_handler.py

import json
import os

from typing import Dict


class ConfigUtils:
    """配置工具类，负责加载JSON配置文件"""

    def __init__(self, json_path: str) -> None:
        """初始化ConfigUtils实例

        Args:
            json_path (str): JSON配置文件路径
        """
        self.json_path: str = os.path.abspath(json_path)
        self.json_data: dict = self.get_json()

    def get_json(self) -> dict:
        """从JSON文件加载配置数据

        Returns:
            dict: 配置文件的JSON数据

        Raises:
            ValueError: 当JSON解析失败时
            FileNotFoundError: 当配置文件不存在时
        """
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON解析错误: {str(e)}") from e
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件未找到: {self.json_path}")