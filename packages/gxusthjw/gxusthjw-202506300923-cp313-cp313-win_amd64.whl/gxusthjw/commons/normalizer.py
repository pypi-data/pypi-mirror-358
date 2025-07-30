#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        normalizer.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义与“数据归一化”相关的函数和类。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/01     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import math
from typing import Tuple

import numpy as np
import numpy.typing as npt

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Define functions and classes related to `data normalization`.
"""

__all__ = [
    'normalize',
    'z_score',
    'decimal_scaling'
]


# 定义 ==============================================================


def normalize(data: npt.ArrayLike,
              new_range: Tuple[int, int] = (0, 1)) -> \
        npt.NDArray[np.number]:
    """
    将指定数据归一化至指定的范围内。

        当所有元素相等时，直接返回全为 lower 的数组。

        示例:
        >>> normalize([1, 2, 3], (0, 1))
        array([0. , 0.5, 1. ])

    :param data: 要归一化的数据。
    :param new_range: 指定的新范围。
    :return: 归一化的数据。
    """
    data = np.asarray(data)
    if not np.issubdtype(data.dtype, np.number):
        raise TypeError("Input data must be of numeric type.")
    lower, upper = new_range
    if upper <= lower:
        raise ValueError("Expected upper > lower, "
                         "but got {lower=%f,upper=%f}" % (lower, upper))
    data_max = np.max(data)
    data_min = np.min(data)
    height = data_max - data_min
    if height == 0:
        # 所有元素相等，直接返回全为 lower 的数组
        return np.full_like(data, fill_value=lower)
    k = (upper - lower) / height
    return lower + k * (data - data_min)

def z_score(data, axis=None, ddof=0):
    """
    Z-score 标准化：将数据转换为均值为0，标准差为1的分布。

    参数:
        data (array-like): 输入的一维或二维数组或列表，应为数值类型
        axis (int or None): 计算均值和标准差的轴方向，默认为None（全部元素一起计算）
        ddof (int): 标准差计算中的自由度调整，默认为0（总体标准差），设为1表示样本标准差

    返回:
        np.ndarray: 标准化后的数据，保持原始形状不变

    异常:
        若标准差为0，抛出 ValueError 并附带详细信息
    """
    data = np.array(data, dtype=float)
    mean = np.mean(data, axis=axis, keepdims=True)
    std = np.std(data, axis=axis, ddof=ddof, keepdims=True)

    if np.any(std < 1e-8):
        raise ValueError("Standard deviation is zero or near-zero, cannot perform Z-score normalization.")

    return (data - mean) / std


def decimal_scaling(data):
    """
    小数定标归一化：通过移动小数点位置进行标准化。

    参数:
        data (array-like): 输入的一维或二维数组或列表

    返回:
        np.ndarray: 归一化后的数据
    """
    data = np.array(data, dtype=float)

    # 处理全零情况，避免无效操作
    max_abs = np.max(np.abs(data))
    if max_abs < 1e-8:
        return data  # 全零或接近零时直接返回原数据

    j = np.ceil(np.log10(max_abs + 1e-8))  # 防止 log(0)
    return data / (10 ** j)