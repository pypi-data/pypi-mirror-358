#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        specimen.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“表征`样本`”的类。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/28     finish
# ----------------------------------------------------------------
# 导包 ============================================================
from .data_analyzer import DataAnalyzer

# 声明 ============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining a class that represents `specimen`.
"""

__all__ = [
    'Specimen',
]


# 定义 =============================================================
class Specimen(DataAnalyzer):
    """
    抽象类`Specimen`表征“样本”。

        此类实质上是一个基类，所有承载样本数据的类均应继承自此类。

        所有承载样本数据的对象均拥有2个基本属性：

            1. 样本名（specimen_name）：str，此样本名在概念上应具有唯一性。

            1. 样品名（sample_name）：str，样品名用于表征某一类样品。
    """

    def __init__(self, *args, **kwargs):
        """
        类`Specimen`的构造方法。

            用到的关键字参数如下：

                1. specimen_name：str，样本名，缺省值为：‘specimen’。

                2. specimen_no：int，样本编号，缺省值为：0。系统并不记录此值。

                3. sample_name：str，样品名，用于表征某一类样品。
                   如果未给出，则缺省采用：`specimen_name_specimen_no"`

            其他未用到的关键字参数，同样将被全部转化为对象的属性。

        :param args: 可选参数。
        :param kwargs: 可选关键字参数。
        """
        # 样品名。
        if 'specimen_name' in kwargs:
            __specimen_name: str = kwargs.pop('specimen_name')
            if (__specimen_name is not None and
                    isinstance(__specimen_name, str) and
                    __specimen_name.strip()):
                self.__specimen_name: str = __specimen_name.strip()
            else:
                self.__specimen_name: str = 'specimen'
        else:
            self.__specimen_name: str = 'specimen'

        if 'specimen_no' in kwargs:
            __specimen_no: int = kwargs.pop('specimen_no')
            if (__specimen_no is not None and
                    isinstance(__specimen_no, int) and
                    __specimen_no >= 0):
                pass
            else:
                __specimen_no: int = 0
        else:
            __specimen_no: int = 0

        __default_sample_name: str = f"{self.__specimen_name}_{__specimen_no}"

        if 'sample_name' in kwargs:
            __sample_name: str = kwargs.pop('sample_name')
            if (__sample_name is not None and
                    isinstance(__sample_name, str) and
                    __sample_name.strip()):
                self.__sample_name: str = __sample_name.strip()
            else:
                self.__sample_name: str = __default_sample_name
        else:
            self.__sample_name: str = __default_sample_name

        super(Specimen, self).__init__(*args, **kwargs)
        self.data_logger.log(self.specimen_name, "SpecimenName")
        self.data_logger.log(self.sample_name, "SampleName")

    @property
    def specimen_name(self) -> str:
        """
        获取样本名。

        :return: 样本名。
        """
        return self.__specimen_name

    @specimen_name.setter
    def specimen_name(self, new_value: str):
        """
        设置样本名。

        :param new_value: 样本名。
        """
        if (not isinstance(new_value, str)) or (not new_value.strip()):
            raise ValueError("new_value must be a non-empty str.")
        self.__specimen_name = new_value
        self.data_logger.log(self.specimen_name, "SpecimenName")

    @property
    def sample_name(self) -> str:
        """
        获取样品名称。

        :return: 样品名称。
        """
        return self.__sample_name

    @sample_name.setter
    def sample_name(self, new_value: str):
        """
        设置样品名称。

        :param new_value: 样品名称。
        """
        if (not isinstance(new_value, str)) or (not new_value.strip()):
            raise ValueError("new_value must be a non-empty str.")
        self.__sample_name = new_value
        self.data_logger.log(self.sample_name, "SampleName")

# ===================================================================
