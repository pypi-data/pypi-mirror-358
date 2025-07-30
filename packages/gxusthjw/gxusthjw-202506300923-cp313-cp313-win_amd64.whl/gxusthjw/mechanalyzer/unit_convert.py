#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        unit_convert.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义与“单位转换”相关的函数。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2024/10/13     finish
# ------------------------------------------------------------------
# 导包 ==============================================================
from typing import Union

import numpy as np

from ..commons import NumberSequence, Number

# 声明 ============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining the classes and functions associated with `unit convert`.
"""

__all__ = [
    'length_unit_to_mm',
    'force_unit_to_cn',
    'area_unit_to_mm2',
    'time_unit_to_s',
    'speed_unit_to_mms',
]


# 定义 ============================================================
def length_unit_to_mm(length: Union[NumberSequence, Number],
                      unit: str) -> Union[NumberSequence, Number]:
    """
    将指定单位的长度数据转换为以毫米（mm）为单位的长度数据。

        1.支持的单位包括：'m', 'dm', 'cm', 'mm'。

        2.上述单位符号全部都是大小写敏感的。

        3. length的类型可以为：int，float，np.ndarray，list，tuple

    :param length: 指定的长度数据。
    :param unit: 指定长度数据的单位（'m', 'dm', 'cm', 'mm'），大小写敏感。
    :return: 以毫米（mm）为单位的长度数据。
    """
    # 单位转换因子
    conversion_factors = {
        'm': 1000,
        'dm': 100,
        'cm': 10,
        'mm': 1
    }

    if unit not in conversion_factors:
        raise ValueError("Expect unit to be 'm' or 'dm' or 'cm' or 'mm'.")

    factor = conversion_factors[unit]

    if isinstance(length, (int, float, np.ndarray)):
        return length * factor
    else:
        return type(length)(item * factor for item in length)


def force_unit_to_cn(force: Union[NumberSequence, Number],
                     unit: str) -> Union[NumberSequence, Number]:
    """
    将指定单位的力数据转换为以厘牛（cN）为单位的力数据。

        1.支持的单位包括：‘N’,'cN'。

        2.上述单位符号全部都是大小写敏感的。

        3. force的类型可以为：int，float，np.ndarray，list，tuple

    :param force: 指定的力数据。
    :param unit: 指定力数据的单位（‘N’,'cN'），大小写敏感。
    :return:以厘牛（cN）为单位的力数据。
    """
    # 单位转换因子
    conversion_factors = {
        'N': 100,
        'cN': 1,
    }

    if unit not in conversion_factors:
        raise ValueError("Expect unit to be 'N' or 'cN'.")

    factor = conversion_factors[unit]

    if isinstance(force, (int, float, np.ndarray)):
        return force * factor
    else:
        return type(force)(item * factor for item in force)


def area_unit_to_mm2(area: Union[NumberSequence, Number],
                     unit: str) -> Union[NumberSequence, Number]:
    """
    将指定单位的面积数据转换为以平方毫米（mm^2）为单位的面积数据。

        1.支持的单位包括：‘m^2’,'dm^2','cm^2','mm^2'。

        2.上述单位符号全部都是大小写敏感的。

        3.area的类型可以为：int，float，np.ndarray，list，tuple

    :param area: 指定的面积数据。
    :param unit: 指定面积数据的单位（‘m^2’,'dm^2','cm^2','mm^2'），大小写敏感。
    :return:以平方毫米（mm^2）为单位的面积数据。
    """
    # 单位转换因子
    conversion_factors = {
        'm^2': 1e6,
        'dm^2': 1e4,
        'cm^2': 1e2,
        'mm^2': 1
    }
    if unit not in conversion_factors:
        raise ValueError("Expect unit to be 'm^2' or 'dm^2' or 'cm^2' or 'mm^2'.")

    factor = conversion_factors[unit]

    if isinstance(area, (int, float, np.ndarray)):
        return area * factor
    else:
        return type(area)(item * factor for item in area)


def time_unit_to_s(time: Union[NumberSequence, Number],
                   unit: str) -> Union[NumberSequence, Number]:
    """
    将指定单位的时间数据转换为以秒（s）为单位的时间数据。

        1.支持的单位包括：‘h’,'min','s'。

        2.上述单位符号全部都是大小写敏感的。

        3.time的类型可以为：int，float，np.ndarray，list，tuple

    :param time: 指定的时间数据。
    :param unit: 指定时间数据的单位（‘h’,'min','s'），大小写敏感。
    :return: 以秒（s）为单位的时间数据。
    """
    # 单位转换因子
    conversion_factors = {
        'h': 3600,
        'min': 60,
        's': 1,
    }
    if unit not in conversion_factors:
        raise ValueError("Expect unit to be 'h' or 'min' or 's'.")

    factor = conversion_factors[unit]

    if isinstance(time, (int, float, np.ndarray)):
        return time * factor
    else:
        return type(time)(item * factor for item in time)


# noinspection DuplicatedCode
def speed_unit_to_mms(speed: Union[NumberSequence, Number],
                      unit: str) -> Union[NumberSequence, Number]:
    """
    将指定单位的速度数据转换为以毫米每秒（mm/s）为单位的速度数据。

        1.支持的单位包括：‘m/h’,'dm/h','cm/h','mm/h',
                       ‘m/min’,'dm/min','cm/min','mm/min',
                       ‘m/s’,'dm/s','cm/s','mm/s'。

        2.上述单位符号全部都是大小写敏感的。

        3.speed的类型可以为：int，float，np.ndarray，list，tuple

    :param speed: 指定的速度数据。
    :param unit: 指定速度数据的单位，大小写敏感。
    :return: 以毫米每秒（mm/s）为单位的速度数据。
    """
    # 单位到转换因子的映射
    conversion_factors = {
        "m/h": 1000 / 3600,
        "dm/h": 100 / 3600,
        "cm/h": 10 / 3600,
        "mm/h": 1 / 3600,
        "m/min": 1000 / 60,
        "dm/min": 100 / 60,
        "cm/min": 10 / 60,
        "mm/min": 1 / 60,
        "m/s": 1000,
        "dm/s": 100,
        "cm/s": 10,
        "mm/s": 1,
    }
    if unit not in conversion_factors:
        raise ValueError(f"Expect one of {list(conversion_factors.keys())}")

    factor = conversion_factors.get(unit)

    if isinstance(speed, (int, float, np.ndarray)):
        return speed * factor
    else:
        return type(speed)(item * factor for item in speed)
# =================================================================
