#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        typings.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“类型标注”相关的类和函数。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/27     finish
# ------------------------------------------------------------------
# 导包 =============================================================
from typing import (Union, Any, )
from collections.abc import (Iterable, Sequence)

import numpy as np
import numpy.typing as npt
import pandas as pd

# 声明 =============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining functions and classes for `type annotations`.
"""

__all__ = [
    'Number',
    'is_number',
    'NumberSequence',
    'is_number_sequence',
    'Numbers',
    'is_numbers',
    'Numeric',
    'is_numeric',
    'NumberNDArray',
    'is_number_ndarray',
    'is_number_1darray',
    'to_number_1darray',
    'is_scalar',
]

# 定义 ===============================================================
Number = Union[int, float, np.number]
"""
表示数值类型。

该类型所标注的变量可以是整数（int）、
浮点数（float）或np.number 类型。
"""


def is_number(value: Number) -> bool:
    """
    判断指定值是否为数值类型。

    :param value: 要判断的值，可以是整数（int）、
                  浮点数（float）或np.number 类型。
    :return: 如果指定的值是数值，返回 True；否则返回 False。
    """
    return isinstance(value, (int, float, np.number))


NumberSequence = Union[
    Sequence[Number],
    npt.NDArray[np.number],
    pd.Series
]
"""
表示数值型序列的类型。

该类型可以是以下几种之一：
    - 包含整数或浮点数的序列（Sequence[Number]）
    - 包含数值类型元素的 NumPy 数组（npt.NDArray[np.number]）
    - 包含数值类型元素的 Pandas 序列（pd.Series）
"""


def is_number_sequence(data: NumberSequence) -> bool:
    """
    检查给定的数据是否为 NumberSequence 类型。

    :param data: 要检查的数据，可以是以下几种之一：
                 - 包含整数或浮点数的序列（Sequence[Number]）
                 - 包含数值类型元素的 NumPy 数组（npt.NDArray[np.number]）
                 - 包含数值类型元素的 Pandas 序列（pd.Series[np.number]）
    :return: 如果数据是 NumberSequence 类型则返回 True，否则返回 False。
    """
    if isinstance(data, (np.ndarray, pd.Series)):
        return issubclass(data.dtype.type, np.number)
    if isinstance(data, Sequence):
        return all(is_number(item) for item in data)
    return False


Numbers = Union[
    Iterable[Number],
    NumberSequence
]
"""
表示数值集的类型。

该类型可以是以下几种之一：
    - 包含数值类型元素的可迭代对象（Iterable[Number]）
    - 包含数值类型元素的数值序列（NumberSequence）
"""


def is_numbers(data: Numbers) -> bool:
    """
    检查给定的数据是否为 Numbers 类型。

    :param data: 要检查的数据，可以是以下几种之一：
                    - 包含数值类型元素的可迭代对象（Iterable[Number]）
                    - 包含数值类型元素的数值序列（NumberSequence）
    :return: 如果数据是 Numbers 类型则返回 True，否则返回 False。
    """
    if isinstance(data, (Sequence, pd.Series, np.ndarray)):
        return is_number_sequence(data)
    if hasattr(data, '__iter__'):
        # 检查可迭代对象中的所有元素是否都是数字
        try:
            return all(is_number(item) for item in data)
        except TypeError:
            # 如果迭代过程中出现类型错误，则认为不符合条件
            return False
    return False


Numeric = Union[Number, Numbers]
"""
表示数值类型的类型变量。

该类型可以是以下几种之一：
    - 数值类型（Number）
    - 包含数值类型元素的数值集（Numbers）
"""


def is_numeric(data: Numeric) -> bool:
    """
    检查给定的数据是否为 Numeric 类型。

    :param data: 要检查的数据，该类型可以是以下几种之一：
                        - 数值类型（Number）
                        - 包含数值类型元素的数值集（Numbers）
    :return: 如果数据是 Numeric 类型则返回 True，否则返回 False。
    """
    if isinstance(data, Number):
        return is_number(data)
    if isinstance(data, (Sequence, pd.Series, np.ndarray)):
        # 检查 NumPy 数组是否只包含数值类型的元素
        return is_numbers(data)
    return False


NumberNDArray = npt.NDArray[np.number]
"""
表示包含数值类型元素的 NumPy 数组类型。

该类型别名用于简化类型标注，适用于以下场景：
    - 函数参数或返回值类型为包含数值类型元素的 NumPy 数组时。
"""


def is_number_ndarray(data: NumberNDArray) -> bool:
    """
    检查给定的数据是否为 NumberNDArray 类型。

    :param data: 要检查的数据，必须是包含数值类型元素的 NumPy 数组。
    :return: 如果数据是 NumberNDArray 类型则返回 True，否则返回 False。
    """
    return isinstance(data, np.ndarray) and issubclass(data.dtype.type, np.number)


def is_number_1darray(data: NumberNDArray) -> bool:
    """
    检查给定的数据是否为一维 NumberNDArray 类型。

    :param data: 要检查的数据，必须是一维的 NumPy 数组，并且包含数值类型元素。
    :return: 如果数据是一维的 NumberNDArray 类型则返回 True，否则返回 False。
    """
    return isinstance(data, np.ndarray) and \
        issubclass(data.dtype.type, np.number) and \
        data.ndim == 1


def to_number_1darray(data: NumberSequence) -> npt.NDArray[np.number]:
    """
    将输入的数据转换为数值类型的1维数组。

    如果转换成功，返回转换后的1维数值数组；
    如果转换失败，抛出ValueError异常。

    :param data: 待转换为1维数值数组的数据。
    :return: 数值类型的1维数组。
    :raise ValueError: 如果数据不能被转换为数值类型的1维数组。
    """
    # 将输入数据转换为NumPy数组
    d = np.asarray(data)
    # 检查转换后的数组是否为数值类型的1维数组
    if is_number_1darray(d):
        # 是数值类型的1维数组，直接返回
        return d
    else:
        # 不是数值类型的1维数组，抛出异常
        raise ValueError(
            "Input data cannot be converted to a numeric 1D array."
        )


def is_scalar(value: Any):
    """
    判断给定的值是否为标量。

    标量被定义为基本的不可迭代数据类型，包括整数、浮点数、布尔值和字符串，
    或者任何不属于迭代器类型（Iterable）的对象。

    None值被判断为标量，即：`is_scalar(None) -> True`

    :param value: 需要进行判断的值，可以是任何类型。
    :return: 如果给定的值是标量，则返回True；否则返回False。
    """
    if value is None:
        return True
    return isinstance(value, (int, float, bool, str)) or not isinstance(value, Iterable)
