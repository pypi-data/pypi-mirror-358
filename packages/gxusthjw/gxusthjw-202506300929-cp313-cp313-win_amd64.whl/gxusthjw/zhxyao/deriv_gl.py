#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        deriv_gl.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      基于格伦瓦尔德·莱特尼科夫（Grunwald-Letnikov,GL）
#                   定义的计算指定数据的指定阶（可为任意阶）导数。
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
Defines a function to compute the derivative of a specified order 
 for given data, based on the Grünwald-Letnikov (GL) definition.
"""

__all__ = [
    'deriv_gl',
    'deriv_gl_0',
    'deriv_gl_1'
]


# 定义 ==============================================================
def deriv_gl(data_y: npt.NDArray[np.float64], deriv_order: float) \
        -> npt.NDArray[np.float64]:
    """
    基于格伦瓦尔德·莱特尼科夫（Grunwald-Letnikov,GL）定义，
    计算指定数据（data_y）的指定阶（deriv_order）导数。

    此算法由广西科技大学“姚志湘”老师开发，
    对应matlab代码为：glfd.m

    :param data_y: 原数据。
    :param deriv_order: 导数的阶。
    :return: 导数数据。
    """
    n = data_y.shape[0]
    w = np.ones(n, dtype=np.float64)
    res = np.zeros(n, dtype=np.float64)
    for j in range(1, n):
        w[j] = w[j - 1] * (1 - (deriv_order + 1) / j)
    y_rev = data_y[::-1]
    for j2 in range(n):
        res[j2] = np.dot(w[:j2 + 1], y_rev[-(j2 + 1):])
    return res


# ------------------------------------------------------------------
def deriv_gl_0(data_y: npt.NDArray[np.float64], deriv_order: float) \
        -> npt.NDArray[np.float64]:
    """
    基于格伦瓦尔德·莱特尼科夫（Grunwald-Letnikov,GL）定义，
    计算指定数据（data_y）的指定阶（deriv_order）导数。

    此算法由广西科技大学“姚志湘”老师开发的Matlab代码经整理而来，
    对应matlab代码为：glfd.m

    :param data_y: 原数据。
    :param deriv_order: 导数的阶。
    :return: 导数数据。
    """
    n = data_y.shape[0]
    w = np.ones(n, dtype=np.float64)
    res = np.zeros(n, dtype=np.float64)
    for j in range(1, n):
        w[j] = w[j - 1] * (1 - (deriv_order + 1) / j)
    for j2 in range(n):
        res[j2] = np.dot(w[0:(j2 + 1)], data_y[0:(j2 + 1)][::-1])
    return res


# ------------------------------------------------------------------
def deriv_gl_1(data_y: npt.NDArray[np.float64], deriv_order: float) \
        -> npt.NDArray[np.float64]:
    """
    基于格伦瓦尔德·莱特尼科夫（Grunwald-Letnikov,GL）定义，
    计算指定数据（data_y）的指定阶（deriv_order）导数。

    此算法由广西科技大学“姚志湘”老师开发，
    对应matlab代码为：glfd.m

    :param data_y: 原数据。
    :param deriv_order: 导数的阶。
    :return: 导数数据。
    """
    n = data_y.shape[0]
    w = np.ones(n, dtype=np.float64)
    res = np.zeros(n, dtype=np.float64)
    for j in range(1, n):
        w[j] = w[j - 1] * (1 - (deriv_order + 1) / j)
    y_rev = data_y[::-1]
    for j2 in range(n):
        res[j2] = np.dot(w[:j2 + 1], y_rev[-(j2 + 1):])
    return res
# ------------------------------------------------------------------
