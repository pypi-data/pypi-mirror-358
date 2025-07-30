#!/usr/bin/env python3
# --*-- coding: utf-8 --*--
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        function_object.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“表征`函数对象`”的类。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/09     finish
# ------------------------------------------------------------------
# 导包 ==============================================================
from abc import ABCMeta, abstractmethod

# 定义 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Define the class for representing `function object`.
"""

__all__ = [
    'FunctionObject'
]


# ==================================================================

class FunctionObject(metaclass=ABCMeta):
    """
    类`FunctionObject`表征“函数对象”。

    继承此类的子类意味着其实例是“函数对象”。
    """

    @abstractmethod
    def __call__(self, *args, **kwargs):
        """
        此方法使对象调用语法可用。

        :param args: 可选参数。
        :param kwargs: 可选关键字参数。
        :return: 函数值。
        """
        pass

    @abstractmethod
    def reviews(self, *args, **kwargs):
        """
        审阅函数。

        :param args: 可选参数。
        :param kwargs: 可选关键字参数。
        """
        pass
