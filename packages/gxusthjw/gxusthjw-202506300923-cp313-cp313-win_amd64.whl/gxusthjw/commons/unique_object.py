#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        unique_object.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义与“`独一无二`对象”相关的类和函数。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/02     finish
# ------------------------------------------------------------------
# 导包 =============================================================
import string
from contextlib import contextmanager
from datetime import datetime
import uuid
import secrets

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining the classes and functions associated with `unique object`.
"""

__all__ = [
    "random_string",
    "unique_string",
    "date_string",
    "UniqueIdentifierObject",
]


# 定义 ===============================================================


def random_string(length: int = 10) -> str:
    """
    随机生成一个指定长度的字符串。

    :param length: 要生成字符串的长度。必须为正整数，否则将抛出 ValueError。
    :return: 生成的字符串。
    """
    # 定义字符集，包括小写字母、大写字母、数字和下划线
    characters = string.ascii_letters + string.digits + "_"

    # 检查 length 是否为正整数。
    if not isinstance(length, int):
        raise TypeError("Length must be an integer.")
    # 检查 length 是否为正整数。
    if length <= 0:
        raise ValueError("Length must be a positive integer.")

    # 使用 secrets.choice 从字符集中随机选择 length 个字符
    return "".join(secrets.choice(characters) for _ in range(length))


def unique_string() -> str:
    """
    生成一个具有一定唯一性的字符串。

    此字符串基于 UUIDv1 标准，包含了时间戳和节点信息。

    uuid1()生成的是一个基于时间戳和节点标识符（通常是计算机的 MAC 地址）的 UUID。

    UUID (Universally Unique Identifier) 是一个 128 位的数字，用来创建几乎唯一的标识符。

    UUID v1 的结构如下：

        1. 时间戳（Timestamp）：占据 UUID 的大部分空间，记录了从 UTC 1582 年 10 月 15 日午夜开始到 UUID 创建时的 100 纳秒间隔的数量。

        2. 节点标识符（Node identifier）：通常是创建 UUID 的机器的硬件地址（MAC 地址），占用了 UUID 的一部分。

    :return: 具有唯一性的字符串。
    """
    # 生成一个基于时间的 UUID，并将 UUID 转换为字符串形式
    return str(uuid.uuid1())


def date_string(format_str: str = "%Y%m%d%H%M%S") -> str:
    """
    生成一个指定格式的当前日期字符串。

        常见的日期格式代码包括：

            %Y：四位数的年份。

            %m：月份，两位数表示。

            %d：日期，两位数表示。

            %b：月份的缩写名称。

            %B：月份的全名。

            %y：年份的最后两位数字。

            %H：小时。

            %M：分钟。

            %S：秒。

    :param format_str: 日期格式字符串，默认为"%Y%m%d%H%M%S"。
    :return: 指定格式的当前日期字符串。
    """
    return datetime.now().strftime(format_str)


class UniqueIdentifierObject(object):
    """
    类`UniqueIdentifierObject`表征“独一无二标识符对象”。
    """

    # 用于确保标识符的唯一性。
    __identifier_set = set()

    def __init__(self):
        """
        类`UniqueIdentifierObject`的初始化方法。
        """
        with self._ensure_unique_identifier() as _identifier:
            self.__identifier = _identifier

    # noinspection PyMethodMayBeStatic
    @contextmanager
    def _ensure_unique_identifier(self):
        """
        上下文管理器，确保生成的标识符是唯一的。
        """
        while True:
            _identifier = unique_string()
            if _identifier not in UniqueIdentifierObject.__identifier_set:
                UniqueIdentifierObject.__identifier_set.add(_identifier)
                break
        yield _identifier

    @property
    def identifier(self) -> str:
        """
        获取对象的标识符。

        :return: 对象的标识符。
        """
        return self.__identifier

# ==================================================================
