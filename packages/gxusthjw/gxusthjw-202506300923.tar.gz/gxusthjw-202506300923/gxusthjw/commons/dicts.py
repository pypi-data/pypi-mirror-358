#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        dicts.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      为`字典`提供辅助方法和类。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/02     finish
# ------------------------------------------------------------------
# 导包 ==============================================================

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining helper functions and classes for `dict` objects.
"""

__all__ = [
    'dict_to_str',
]
# 定义 ==============================================================
def dict_to_str(delimiter: str = "=",
                separator: str = "\n",
                drop_key: bool = False,
                **kwargs):
    """
    将 **kwargs 参数转换为字符串，支持自定义分隔符和换行符。

    注意事项：
        - 如果 kwargs 为空，则返回空字符串。
        - delimiter 和 separator 必须为字符串类型。
        - kwargs 的值会被自动转换为字符串以避免类型错误。

    :param delimiter: 键和值之间的分隔符，默认是等号（"="）。
    :param separator: 每个键值对之间的分隔符，默认是换行符（"\n"）。
    :param drop_key: 指示是否丢弃key值。
    :param kwargs: 需要转换为字符串的键值对。
    :return: 格式化后的字符串。
    """
    if drop_key:
        formatted_lines = [f"{delimiter}{value}" for _, value in
                           kwargs.items()]
    else:
        # 将 kwargs 字典中的键值对格式化为 "key{separator}value" 的形式
        formatted_lines = [f"{key}{delimiter}{value}" for key, value in
                           kwargs.items()]
    # 使用指定的换行符连接每一行
    result = separator.join(formatted_lines)
    return result

