#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        quasi_sech.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“拟双曲正割函数”。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/10     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import numpy as np
import numpy.typing as npt

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defines 'quasi-hyperbolic Secant Function'.
"""

__all__ = [
    'sech',
    'sech_np',
    'quasi_sech',
    'quasi_sech_np',
]


# 定义 ==============================================================
def sech(x: npt.NDArray[np.float64],
         den_default:float = 0.0) -> npt.NDArray[np.float64]:
    """
    计算指定自变量x的双曲正割函数值，
    定义为 sech(x) = 2 / (exp(x) + exp(-x))。

    :param x: 自变量，必须是 float64 类型的 numpy.ndarray。
    :param den_default: 当exp(x) + exp(-x)接近于0时，采用此值代替。
    :return: 函数值，返回类型为 numpy.ndarray，元素类型为 float64。
    """
    with np.errstate(all='ignore'):
        denominator = np.exp(x) + np.exp(-x)

    # 显式处理分母过小的情况
    small_denominator = np.isclose(denominator, den_default)
    if np.any(small_denominator):
        # 可选：抛出异常或设为默认值，此处设为 den_default
        res = np.zeros_like(denominator)
        valid_mask = ~small_denominator
        res[valid_mask] = 2.0 / denominator[valid_mask]
    else:
        res = 2.0 / denominator

    return res


def sech_np(x: npt.NDArray[np.float64], *args, **kwargs) -> npt.NDArray[np.float64]:
    """
    计算指定自变量x的"双曲正割函数"值。

    此方法基于numpy.cosh函数实现。

    :param x: 自变量，必须是 float64 类型的 numpy.ndarray。
    :param args: 可选参数，将被直接传入 numpy.cosh 函数。
    :param kwargs: 可选关键字参数，将被直接传入 numpy.cosh 函数。
    :return: 函数值，类型与输入一致。
    """
    with np.errstate(all='ignore'):
        result = 1.0 / np.cosh(x, *args, **kwargs)
    return result


def quasi_sech(x: npt.NDArray[np.float64],
               peak_width: float, peak_steepness: float):
    """
    计算指定自变量x的“拟双曲正割函数”值。

    :param x: 自变量，必须是 float64 类型的 numpy.ndarray。
    :param peak_width: 拟双曲正割函数的参数peak_width，称为“峰宽”。
    :param peak_steepness: 拟双曲正割函数的参数peak_steepness，
                          称为“峰陡峭度指数”。
    :return: “拟双曲正割函数”值。
    """
    return sech(np.power(x * peak_width, peak_steepness))


def quasi_sech_np(x: npt.NDArray[np.float64],
                  peak_width: float, peak_steepness: float):
    """
    计算指定自变量x的“拟双曲正割函数”值。

    此方法基于sech_np函数实现。

    :param x: 自变量，必须是 float64 类型的 numpy.ndarray。
    :param peak_width: 拟双曲正割函数的参数peak_width，称为“峰宽”。
    :param peak_steepness: 拟双曲正割函数的参数peak_steepness，
                          称为“峰陡峭度指数”。
    :return: “拟双曲正割函数”值。
    """
    return sech_np(np.power(x * peak_width, peak_steepness))
