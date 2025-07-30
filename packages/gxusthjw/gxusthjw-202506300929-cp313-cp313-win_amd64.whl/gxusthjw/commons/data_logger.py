#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        data_logger.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“表征`数据记录器`”的类。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/03     finish
# ------------------------------------------------------------------
# 导包 ==============================================================
from typing import (
    Any, Optional
)
from .data_table import DataTable

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Define a class that represents `data logger`.
"""

__all__ = ["DataLogger"]


# 定义 ==============================================================

class DataLogger(DataTable):
    """
    类`DataLogger`表征“数据记录器”。
    """

    def __init__(self, *args, **kwargs):
        """
        类`DataLogger`的初始化方法。

            备注：
                可选关键字参数：

                1. datalogger_owner，当datalogger_owner未指定或为None时，用`self`代替。

                2. datalogger_name，当datalogger_name未指定或为None时，
                   用`f"{self.__owner.__class__.__name__}_DataLogger"`代替。

        :param owner: 数据记录器的归属。
        :type owner: Any
        :param name: 数据记录器的名称。
        :type name: str
        """
        self.__datalogger_owner = kwargs.pop("datalogger_owner", self)
        self.__datalogger_owner = self.__datalogger_owner if self.__datalogger_owner\
                                                             is not None else self
        __default_name = f"{self.__datalogger_owner.__class__.__name__}_DataLogger"
        self.__datalogger_name = kwargs.pop("datalogger_name", __default_name)
        self.__datalogger_name = self.__datalogger_name if self.__datalogger_name \
                                                           is not None else __default_name
        # 初始化数据记录器中存储数据的对象------------------------------
        super(DataLogger, self).__init__(*args, **kwargs)
        self.update(self.__datalogger_owner, "DataLoggerOwner")
        self.update(self.__datalogger_name, "DataLoggerName")
        # 初始化完成 -----------------------------------------------

    @property
    def datalogger_owner(self) -> Any:
        """
        返回数据记录器的归属。

        :return: 数据记录器的归属。
        :rtype: Any
        """
        return self.__datalogger_owner

    @property
    def datalogger_name(self) -> str:
        """
        返回数据记录器的名称。

        :return: 数据记录器的名称。
        :rtype: str
        """
        return self.__datalogger_name

    def log(self, data, name: Optional[str] = None):
        """
        更新或添加数据项。

            注意：

                1. 如果数据记录器中，指定数据项名已经存在，
                   则数据记录器中此名所关联的数据将被指定的数据取代。

                2. 如果item_name为None，则用item_i取代，
                   其中i为数据记录器中数据项的数量。

        :param data: 要更新或添加的数据项数据。
        :param name: 要更新或添加的数据项名。
        """
        self.update(data, name)

    def logs(self, *args, **kwargs):
        """
        更新或添加数据。

            1. 对于可选参数args，其作用是指定数据项的数据，args中的每个元素为1条数据项的数据。

                args中每个元素的允许值包括：

                （1）标量值，类型必须为int,float,bool,str或object等。

                （2）类数组值：类型必须为list，tuple，numpy.ndarray,pandas.Series,
                            Iterable, Sequence等。

            2. 对于可选关键字参数kwargs，其作用是指定数据项的名称及其他关键字参数：

                （1）通过item_names关键字参数，如果其为字典（dict），
                    则键对应数据项的序号，而值对应数据项名。

                （2）通过item_names关键字参数，如果其为列表（list）或元组（tuple），
                    则序号对应数据项的序号，而值对应数据项名。

                （3）如果没有指定item_names关键字参数或者 item_names不符合（1）和（2）的规则，
                    则采用缺省的数据项名（item_i的形式）。

                （4）任何数据项名的遗漏，都会以item_i的形式代替。

            3. 对于除item_names外的其他可选关键字参数，将全部按照`键值对`存储。

        :param args: 可选参数，元组类型，用于初始化”数据项“的数据。
        :param kwargs: 可选的关键字参数，字典类型，
                       用于初始化”数据项“的名称及其他属性参数。
        """
        self.updates(*args, **kwargs)
# ====================================================================================
