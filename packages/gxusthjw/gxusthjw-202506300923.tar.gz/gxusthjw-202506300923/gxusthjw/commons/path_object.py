#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        path_object.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“表征`路径对象`”的类。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/04     finish
# ----------------------------------------------------------------
# 导包 ============================================================
from functools import cached_property
from typing import Union
from pathlib import Path

# 声明 ============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining a class that represents `path object`.
"""

__all__ = [
    'PathObject',
]


# 定义 ===============================================================
class PathObject(object):
    """
    类`PathObject`表征“路径对象”。
    """

    def __init__(self, path: Union[str, Path]):
        """
        类`PathObject`的初始化方法。

        :param path: 路径。
        :type path: Union[str, Path]
        """
        # 将输入转换为 pathlib.Path 对象。
        if isinstance(path, (Path, str)):
            self.__path = Path(path)
        else:
            raise TypeError("Parameter path must be a string or pathlib.Path object.")

    @cached_property
    def validate(self):
        """
        验证路径是否有效。

        :return: 如果路径有效返回 True，否则返回 False。
        :rtype: bool
        """
        return bool(self.__path.anchor or self.__path.parts)

    @property
    def path(self):
        """
        获取 pathlib.Path 对象。

        :return: pathlib.Path 对象。
        :rtype: Path
        """
        return self.__path

    @cached_property
    def absolute_path(self):
        """
        获取绝对路径。

        :return: pathlib.Path 对象。
        :rtype: Path
        """
        return self.__path.resolve()

    @cached_property
    def path_str(self):
        """
        获取 完整路径的字符串。

        :return: 完整路径的字符串。
        :rtype: str
        """
        return str(self.__path.resolve())

    @cached_property
    def parent(self):
        """
        获取父路径。

        :return: 父路径。
        :rtype: PathObject
        """
        return PathObject(str(self.__path.parent.resolve()))

    @cached_property
    def is_file(self):
        """
        判断路径是否指向文件。

        :return: 如果路径指向文件，返回True，否则返回False。
        :rtype: bool
        """
        return self.__path.is_file()

    @cached_property
    def is_folder(self):
        """
        判断路径是否指向文件夹。

        :return: 如果路径指向文件夹，返回True，否则返回False。
        :rtype: bool
        """
        return self.__path.is_dir()

    @cached_property
    def exists(self):
        """
        判断路径是否存在。

        :return: 如果路径存在，返回True，否则返回False。
        :rtype: bool
        """
        return self.__path.exists()

    @cached_property
    def name(self):
        """
        获取 最末路径组分的字符串。

        :return: 最末路径组分的字符串。
        :rtype: str
        """
        return self.__path.name

    def __str__(self):
        """
        返回路径的字符串表示。

        :return: 路径的字符串表示。
        :rtype: str
        """
        return str(self.__path)
# =================================================================
