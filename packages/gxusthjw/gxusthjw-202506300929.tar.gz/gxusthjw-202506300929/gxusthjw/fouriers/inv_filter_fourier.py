#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        xxxxxx.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      xxxxxx。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/xx/xx     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import numpy as np
# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
"""

__all__ = [
    'inv_filter_fourier'
]
# 定义 ==============================================================


def inv_filter_fourier(t, options):
    """
    根据指定选项生成逆傅里叶滤波函数。

    参数:
        t (np.ndarray): 傅里叶变换的 x 轴（频率轴）。
        options (SimpleNamespace or dict): 包含滤波参数的配置对象。
            - FilterInverse: 滤波器类型，如 "Bessel", "Boxcar" 等
            - CutPointInverse: 截止点
            - CutPointInverseFactor: 截断因子（用于 cut < l_cut * factor）

    返回:
        filter_function (np.ndarray): 逆滤波器函数数组。
    """
    l_cut = options.CutPointInverse
    filter_type = options.FilterInverse
    factor = options.CutPointInverseFactor

    if filter_type == "Bessel":
        cut = np.abs(t) < l_cut * factor
        with np.errstate(divide='ignore', invalid='ignore'):
            filter_function = (1 - (t / l_cut) ** 2) ** 2
            filter_function = (1 / filter_function) * cut
        filter_function[np.isnan(filter_function)] = 0  # 替换 NaN 为 0

    elif filter_type == "Blackman-Lorenz 3-term":
        cut = np.abs(t) < l_cut * factor
        with np.errstate(divide='ignore', invalid='ignore'):
            filter_function = (0.4089701 + 0.5 * np.cos(np.pi * t / l_cut) +
                               0.0910299 * np.cos(2 * np.pi * t / l_cut))
            filter_function = (1 / filter_function) * cut
        filter_function[np.isnan(filter_function)] = 0

    elif filter_type == "Triangle-Sq":
        cut = np.abs(t) < l_cut * factor
        with np.errstate(divide='ignore', invalid='ignore'):
            filter_function = (1 - np.abs(t) / l_cut) ** 2
            filter_function = (1 / filter_function) * cut
        filter_function[np.isnan(filter_function)] = 0

    elif filter_type == "Sinc-Sq":
        cut = np.abs(t) < l_cut * factor
        with np.errstate(divide='ignore', invalid='ignore'):
            sinc = np.sin(np.pi * t / l_cut) / (np.pi * t / l_cut)
            filter_function = sinc ** 2
            filter_function = (1 / filter_function) * cut
        filter_function[0] = 1  # 特殊处理 t=0 处
        filter_function[np.isnan(filter_function)] = 0

    elif filter_type == "Triangle":
        cut = np.abs(t) < l_cut * factor
        with np.errstate(divide='ignore', invalid='ignore'):
            filter_function = (1 - np.abs(t) / l_cut)
            filter_function = (1 / filter_function) * cut
        filter_function[np.isnan(filter_function)] = 0

    elif filter_type == "Truncated Gaussian":
        cut = np.abs(t) < l_cut * factor
        with np.errstate(divide='ignore', invalid='ignore'):
            filter_function = np.exp(-np.pi ** 2 / np.log(2) * (t / (2 * l_cut)) ** 2)
            filter_function = (1 / filter_function) * cut
        filter_function[np.isnan(filter_function)] = 0

    elif filter_type == "Gaussian":
        with np.errstate(divide='ignore', invalid='ignore'):
            filter_function = np.exp(-np.pi ** 2 / np.log(2) * (t / (2 * l_cut)) ** 2)
            filter_function = 1 / filter_function
        filter_function[np.isnan(filter_function)] = 0

    elif filter_type == "Lorentzian":
        with np.errstate(divide='ignore', invalid='ignore'):
            filter_function = np.exp(-np.pi * np.abs(t) / l_cut)
            filter_function = 1 / filter_function
        filter_function[np.isnan(filter_function)] = 0

    elif filter_type == "Boxcar":
        filter_function = np.abs(t) <= l_cut

    elif filter_type == "Norton-Beer Medium":
        cut = np.abs(t) < l_cut * factor
        with np.errstate(divide='ignore', invalid='ignore'):
            term = (1 - (t / l_cut) ** 2)
            filter_function = 0.152442 - 0.136176 * term + 0.983734 * term ** 2
            filter_function = (1 / filter_function) * cut
        filter_function[np.isnan(filter_function)] = 0

    elif filter_type == "Norton-Beer Strong":
        cut = np.abs(t) < l_cut * factor
        with np.errstate(divide='ignore', invalid='ignore'):
            term = (1 - (t / l_cut) ** 2)
            filter_function = 0.045335 + 0.554883 * term + 0.399782 * term ** 3
            filter_function = (1 / filter_function) * cut
        filter_function[np.isnan(filter_function)] = 0

    elif filter_type == "Hamming":
        cut = np.abs(t) <= l_cut * factor
        with np.errstate(divide='ignore', invalid='ignore'):
            filter_function = 0.54 + 0.46 * np.cos(np.pi * t / l_cut)
            filter_function = (1 / filter_function) * cut
        filter_function[np.isnan(filter_function)] = 0

    elif filter_type == "Hanning":
        cut = np.abs(t) < l_cut * factor
        with np.errstate(divide='ignore', invalid='ignore'):
            filter_function = 0.5 + 0.5 * np.cos(np.pi * t / l_cut)
            filter_function = (1 / filter_function) * cut
        filter_function[np.isnan(filter_function)] = 0

    elif filter_type == "Blackman":
        cut = np.abs(t) < l_cut * factor
        with np.errstate(divide='ignore', invalid='ignore'):
            filter_function = (0.42659071 + 0.49656062 * np.cos(np.pi * t / l_cut) +
                               0.07684867 * np.cos(2 * np.pi * t / l_cut))
            filter_function = (1 / filter_function) * cut
        filter_function[np.isnan(filter_function)] = 0

    elif filter_type == "Blackman-Harris 3-term":
        cut = np.abs(t) < l_cut * factor
        with np.errstate(divide='ignore', invalid='ignore'):
            filter_function = (0.42659071 + 0.49656062 * np.cos(np.pi * t / l_cut) +
                               0.07684867 * np.cos(2 * np.pi * t / l_cut))
            filter_function = (1 / filter_function) * cut
        filter_function[np.isnan(filter_function)] = 0

    else:
        raise ValueError(f"Unsupported inverse filter type: {filter_type}")

    return filter_function
