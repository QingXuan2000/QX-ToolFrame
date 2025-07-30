#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/3/24 23:18
# @Author  : QingXuanJun
# @File    : main.py

from typing import Optional

from QXTF.config_handler import ConfigUtils
from QXTF.menu_engine import MenuUtils, logo, menu, get_sub_menu
from QXTF.system_utils import enter_back
from QXTF.tool_executor import sub_menu


class Application:
    """应用程序主类，负责菜单显示和用户交互"""
    def __init__(self) -> None:
        """初始化应用程序，加载工具配置"""
        self.tools_config: dict = ConfigUtils("./config/config.json").get_json().get("tools", {})
        self.menu_utils: Optional[MenuUtils] = None

    def main_menu(self) -> int:
        """显示主菜单并获取用户选择

        Returns:
            int: 用户选择的菜单项索引
        """
        while True:
            try:
                logo()
                print(menu(self.tools_config))
                return int(input("\n>>> "))
            except ValueError:
                print(f"\033[31m输入无效，请输入一个整数！\033[0m")
                enter_back()
            except Exception as e:
                print(f"\033[31m发生未知错误：{e}\033[0m")
                enter_back()

    def sub_menu_handler(self, user_option: int) -> bool:
        self.menu_utils = MenuUtils(user_option, "index", "config", self.tools_config)
        while True:
            try:
                logo()
                # 先获取并检查菜单配置
                menu_config = self.menu_utils.find_val()
                if menu_config is None:
                    print(f"\033[31m未找到对应的菜单配置\033[0m")
                    enter_back()
                    return False
                # 使用已验证的非None配置
                print(get_sub_menu(menu_config))
                sub_option = int(input("\n>>> "))
                
                sub_menu(menu_config, sub_option)
                return True
            except ValueError:
                print(f"\033[31m输入无效，请输入一个整数！\033[0m")
                enter_back()
            except FileNotFoundError:
                print(f"\033[31m配置文件未找到！\033[0m")
                enter_back()
            except TypeError:
                print(f"\033[31m未找到对应的索引！\033[0m")
                enter_back()
                return False
            except IndexError:
                print(f"\033[31m未找到对应的索引或架构！\033[0m")
                enter_back()
            except Exception as e:
                print(f"\033[31m发生未知错误：{str(e)}\033[0m")
                enter_back()

    def run(self) -> None:
        while True:
            main_option = self.main_menu()
            self.sub_menu_handler(main_option)


if __name__ == "__main__":
    app = Application()
    app.run()
