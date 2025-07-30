#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        data_analyzer.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“表征`数据分析器`”的类。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/28     finish
# ------------------------------------------------------------------
# 导包 ============================================================
from .data_logger import DataLogger

# 声明 ============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Define a class that represents `Data Analyzer`.
"""

__all__ = [
    'DataAnalyzer'
]


# 定义 ============================================================
class DataAnalyzer(object):
    """
    类`DataAnalyzer`表征“数据分析器”。

        类`DataAnalyzer`是所有表征`数据分析器`的基类。

        此类拥有如下属性：

            1. data_analyzer_name：数据分析器的名称。

            2. data_logger: 数据记录器。
    """

    def __init__(self, *args, **kwargs):
        """
        类`DataAnalyzer`的初始化方法。

            消耗掉的可选关键字参数：

                1. data_analyzer_name：数据分析器的名称，默认值：DataAnalyzer。

        :param args: 可选参数。
        :param kwargs: 可选关键字参数。
        """
        # 设置数据分析器的名字。
        self.__data_analyzer_name = kwargs.pop('data_analyzer_name', self.__class__.__name__)
        if self.__data_analyzer_name is None or (not isinstance(self.__data_analyzer_name, str)) or \
                (not self.__data_analyzer_name.strip()):
            self.__data_analyzer_name = self.__class__.__name__

        # 设置数据记录器的归属。
        data_logger_owner = self

        # 设置数据记录器的名字。
        data_logger_name = f"{self.__data_analyzer_name}_DataLogger"

        # 初始化数据记录器。
        self.__data_logger = DataLogger(datalogger_owner=data_logger_owner,
                                        datalogger_name=data_logger_name)
        self.__data_logger.log(self.__data_analyzer_name, 'DataAnalyzerName')
        self.__data_logger.logs(*args, **kwargs)

        # 可选参数将被转换为对象的属性。
        i = 0
        for arg in args:
            arg_name = f"arg_{i}"
            if not hasattr(self, arg_name):
                setattr(self, arg_name, arg)
            i = i + 1

        # 可选关键字参数将被转换为对象的属性。
        for key in kwargs.keys():
            if not hasattr(self, key):
                setattr(self, key, kwargs[key])

    @property
    def data_analyzer_name(self):
        """
        返回数据分析器的名称。

        :return: 数据分析器的名称。
        :rtype: str
        """
        return self.__data_analyzer_name

    @property
    def data_logger(self):
        """
        返回数据记录器。

        :return: 数据记录器。
        :rtype: DataLogger
        """
        return self.__data_logger
# ===============================================================
