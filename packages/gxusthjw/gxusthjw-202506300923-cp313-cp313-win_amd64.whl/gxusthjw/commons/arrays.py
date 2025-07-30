#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        arrays.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      为`数组`提供辅助方法和类。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/02     finish
# ------------------------------------------------------------------
# 导包 ==============================================================
from typing import Union
from enum import Enum
import numpy as np
import numpy.typing as npt

from .typings import (
    Number,
    NumberNDArray,
    NumberSequence,
    is_number_1darray
)

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining helper functions and classes for `array` objects.
"""

__all__ = [
    "is_sorted_ascending_np",
    "is_sorted_descending_np",
    "is_sorted_np",
    "is_sorted",
    "is_sorted_ascending",
    "is_sorted_descending",
    "reverse",
    "is_equals_of",
    "Ordering",
    "sort",
    "find_closest_index",
    "find_crossing_index",
    "find_index_range",
]


# 定义 ==============================================================
def is_sorted_ascending_np(arr: NumberNDArray) -> bool:
    """
    判断数组是否为升序排列。

    :param arr: 数值数组。
    :return: 如果数组是升序排列，则返回True；否则返回False。
    """
    # 检查输入数组是否为一维数值数组。
    if not is_number_1darray(arr):
        raise TypeError("The input array (arr) must be a one-dimensional numeric array.")
    # 检查数组是否包含 NaN 值
    if np.any(np.isnan(arr)):
        raise ValueError("The input array (arr) contains NaN values, which are not allowed.")

    # 检查数组是否为空或只有一个元素，
    # 如果是，则直接返回True。
    if arr.size <= 1:
        return True
    # 逐元素比较，提前终止检查
    for i in range(1, len(arr)):
        if arr[i] < arr[i - 1]:
            return False
    return True


def is_sorted_descending_np(arr: NumberNDArray) -> bool:
    """
    判断数组是否为降序排列。

    :param arr: 数值数组。
    :return: 如果数组是降序排列，则返回True；否则返回False。
    """
    # 检查输入数组是否为一维数值数组。
    if not is_number_1darray(arr):
        raise TypeError("The input array (arr) must be a one-dimensional numeric array.")
    # 检查数组是否包含 NaN 值
    if np.any(np.isnan(arr)):
        raise ValueError("The input array (arr) contains NaN values, which are not allowed.")

    # 检查数组是否为空或只有一个元素，如果是，则直接返回True。
    if arr.size <= 1:
        return True
    # 逐元素比较，提前终止检查
    for i in range(1, len(arr)):
        if arr[i] > arr[i - 1]:
            return False
    return True


def is_sorted_np(arr: NumberNDArray):
    """
    判断数组是否为升序或降序排列。

    :param arr: 数值数组。
    :return: 如果数组是升序或降序排列，则返回 True；否则返回 False。
    """
    # 检查输入数组是否为一维数值数组。
    if not is_number_1darray(arr):
        raise TypeError("The input array (arr) must be a one-dimensional numeric array.")
    # 检查数组是否包含 NaN 值
    if np.any(np.isnan(arr)):
        raise ValueError("The input array (arr) contains NaN values, which are not allowed.")

    # 检查数组是否为空或只有一个元素，如果是，则直接返回True。
    if arr.size <= 1:
        return True

    ascending = True
    descending = True
    for i in range(1, len(arr)):
        if arr[i] < arr[i - 1]:
            ascending = False
        if arr[i] > arr[i - 1]:
            descending = False
        if not ascending and not descending:
            break
    return ascending or descending


def is_sorted(arr: NumberSequence) -> bool:
    """
    判断给定的数值组是否为有序排列（升序或降序）。

    :param arr: 给定的数值组，可以是以下几种之一：
                 - 包含整数或浮点数的列表（List[Union[int, float]]）
                 - 包含整数或浮点数的元组（Tuple[Union[int, float], ...]）
                 - 包含数值类型元素的 NumPy 数组（npt.NDArray[np.number]）
    :return: 如果给定的数值组是有序的，则返回 True；否则返回 False。
    """
    # 转换为 numpy 数组并检查类型
    try:
        value_arr = np.asarray(arr)
    except ValueError:
        raise ValueError("The input (arr) must be in a form that can be converted into a `NDArray`.")

    # 单次遍历判断是否有序
    return is_sorted_np(value_arr)


def is_sorted_ascending(arr: NumberSequence) -> bool:
    """
    判断给定的数值组是否为升序的。

    如果给定的数值组是是升序的，返回True，否则返回False。

    :param arr: 给定的数值组。
    :return:如果给定的数值组是是升序的，返回True，否则返回False。
    """
    # 转换为 numpy 数组并检查类型
    try:
        value_arr = np.asarray(arr)
    except ValueError:
        raise ValueError("The input (arr) must be in a form that can be converted into a `NDArray`.")
    return is_sorted_ascending_np(value_arr)


def is_sorted_descending(arr: NumberSequence) -> bool:
    """
    判断给定的数值组是否为降序的。

    如果给定的数值组是是降序的，返回True，否则返回False。

    :param arr: 给定的数值组。
    :return:如果给定的数值组是是降序的，返回True，否则返回False。
    """
    # 转换为 numpy 数组并检查类型
    try:
        value_arr = np.asarray(arr)
    except ValueError:
        raise ValueError("The input (arr) must be in a form that can be converted into a `NDArray`.")
    return is_sorted_descending_np(value_arr)


def reverse(arr: NumberSequence) -> npt.NDArray[np.number]:
    """
    将给定的数值组倒置。

    :param arr: 给定的数值组。
    :return: 倒置后的数值组。
    """
    # 转换为 numpy 数组并检查类型
    try:
        value_arr = np.asarray(arr)
    except ValueError:
        raise ValueError("The input (arr) must be in a form that can be converted into a `NDArray`.")
    return np.array(value_arr[::-1], copy=True)


def is_equals_of(
        arr1: NumberSequence, arr2: NumberSequence, rtol=0, atol=1e-9
) -> bool:
    """
    判断给定的两个数值组的相等性。

    第1个参数记为：a

    第2个参数记为：b

    则下式为True，此函数返回True：

        absolute(a - b) <= (atol + rtol * absolute(b))

    :param arr1: 数值组1。
    :param arr2: 数值组2。
    :param rtol: 相对容差，相对容差是指：两个数之差除以第2个数。
    :param atol: 绝对容差，绝对容差是指：两个数之差。
    :return:如果给定的两个数值组相等，则返回True，否则返回false。
    """
    # 转换为 numpy 数组并检查类型
    try:
        value_arr1 = np.asarray(arr1)
        value_arr2 = np.asarray(arr2)
    except ValueError:
        raise ValueError("The input (arr) must be in a form that can be converted into a `NDArray`.")

    return np.allclose(
        value_arr1, value_arr2, rtol=rtol, atol=atol, equal_nan=True
    )


class Ordering(Enum):
    """
    枚举`Ordering`表征有序性。
    """

    # 无序。
    UNORDERED = 0
    """
    ‘UNORDERED’表征`无序`。
    """

    # 升序。
    ASCENDING = 1
    """
    ‘ASCENDING’表征`升序`。
    """

    # 降序。
    DESCENDING = 2
    """
    ‘DESCENDING’表征`降序`。
    """

    # noinspection DuplicatedCode
    @staticmethod
    def of(value: Union[int, str]):
        """
        从值或成员名（忽略大小写）构建枚举实例。

        :param value: 指定的值或成员名（忽略大小写）。
        :return: Ordering对象。
        :rtype: Ordering
        """
        if isinstance(value, str):
            if value.upper() in Ordering.__members__:
                return Ordering.__members__[value]
            else:
                raise ValueError(f"Unknown value ({value}) for Ordering.")
        elif isinstance(value, int):
            for member in Ordering:
                if member.value == value:
                    return member
            raise ValueError(f"Unknown value ({value}) for Ordering.")
        else:
            raise ValueError(f"Unknown value ({value}) for Ordering.")


def sort(
        arr: NumberSequence, ordering: Ordering = Ordering.ASCENDING
) -> npt.NDArray[np.number]:
    """
    获取给定数值组的有序copy。

    :param arr: 给定的数值组。
    :param ordering: 指定升序或降序。
    :return: 有序的数值组。
    """
    arr_sorted = np.sort(arr)
    if ordering == Ordering.DESCENDING:
        return reverse(arr_sorted)
    return arr_sorted


# noinspection PyTypeChecker
def find_closest_index(ordered_arr: NumberSequence, value: Number):
    """
    在指定有序数组中找到最接近指定值的索引。

    此方法与find_crossing_index方法的目标是一致的，但两者的算法并不相同。

    降序与升序的结果不同。

    :param ordered_arr: 指定的有序数组。
    :param value: 指定的值。
    :return: 指定有序数组中找到最接近指定值的索引。
    """
    ordered_arr = np.asarray(ordered_arr)
    if is_sorted_ascending(ordered_arr):
        if not (ordered_arr[0] <= value <= ordered_arr[-1]):
            return None
        # 对于升序数组
        idx = np.searchsorted(ordered_arr, value)
        if idx < len(ordered_arr) and ordered_arr[idx] == value:
            return idx
        if idx == 0:
            return 0
        elif idx == len(ordered_arr):
            return len(ordered_arr) - 1
        else:
            before = ordered_arr[idx - 1]
            after = ordered_arr[idx]
            if after - value < value - before:
                return idx
            else:
                return idx - 1
    elif is_sorted_descending(ordered_arr):
        if not (ordered_arr[-1] <= value <= ordered_arr[0]):
            return None
        # 对于降序数组
        reversed_arr = ordered_arr[::-1]
        rev_idx = np.searchsorted(reversed_arr, value)
        if rev_idx < len(reversed_arr) and reversed_arr[rev_idx] == value:
            return len(ordered_arr) - 1 - rev_idx
        if rev_idx == 0:
            return len(ordered_arr) - 1
        elif rev_idx == len(reversed_arr):
            return 0
        else:
            before = reversed_arr[rev_idx - 1]
            after = reversed_arr[rev_idx]
            if after - value < value - before:
                return len(ordered_arr) - 1 - rev_idx
            else:
                return len(ordered_arr) - 1 - (rev_idx - 1)
    else:
        raise ValueError("Expected arr is ordered.")


def find_crossing_index(ordered_arr: NumberSequence, value: Number):
    """
    在指定有序数组中找到最接近指定值的索引。

    此方法与find_closest_index方法的目标是一致的，但两者的算法并不相同。

    无论是降序或升序，其结果均相同。

    :param ordered_arr: 指定的有序数组。
    :param value: 指定的值。
    :return: 指定有序数组中找到最接近指定值的索引。
    """
    if not is_sorted(ordered_arr):
        raise ValueError("Expected arr is ordered.")
    ordered_arr = np.asarray(ordered_arr)
    if (ordered_arr[0] <= value <= ordered_arr[-1]) or (
            ordered_arr[-1] <= value <= ordered_arr[0]
    ):
        # 找到符号变化的位置
        sign_changes = np.where(np.diff(np.sign(ordered_arr - value)) != 0)[0]
        # 计算交叉点的索引
        cross_indices = sign_changes + (value - ordered_arr[sign_changes]) / (
                ordered_arr[sign_changes + 1] - ordered_arr[sign_changes]
        )
        # 添加等于 strain_value 的位置
        equal_indices = np.where(ordered_arr == value)[0]
        # 合并索引并排序
        all_indices = np.sort(np.concatenate((cross_indices, equal_indices)))
        # 返回最接近的索引
        return int(np.round(all_indices[0])) if all_indices.size > 0 else None
    else:
        return None


def find_index_range(ordered_arr: NumberSequence, value1: Number, value2: Number):
    """
    获取两个指定值范围的索引范围。

    :param ordered_arr: 指定的有序数组。
    :param value1: 指定的值1。
    :param value2: 指定的值2。
    :return: 两个指定值范围的索引范围。
    """
    value1_index = find_crossing_index(ordered_arr, value1)
    value2_index = find_crossing_index(ordered_arr, value2)
    return (
        (value1_index, value2_index)
        if value2_index > value1_index
        else (value2_index, value1_index)
    )
