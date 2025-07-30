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

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
"""

__all__ = [
    'filter_fourier'
]
# 定义 ==============================================================
import numpy as np

def filter_fourier(t, method, options):
    """
    根据指定方法和选项生成傅里叶滤波函数。

    参数:
        t (np.ndarray): 傅里叶变换的 x 轴（频率轴）。
        method (str): 滤波方法，例如 "FSD"。
        options (SimpleNamespace or dict): 包含滤波参数的配置对象。

    返回:
        filter_function (np.ndarray): 滤波器函数数组。
    """
    if method == "FSD":
        k = options.FSD_narrowing
        fwhhL = options.FSD_FWHHL
        fwhhG = options.FSD_FWHHG
        # 计算有效 FWHH 和高斯因子
        g = fwhhG / (fwhhG + fwhhL)
        fwhhT = ((1 + 0.25 * g ** 2 + 6.48 * g ** 4 - 1.05 * g ** 6) /
                 (1 - 0.54 * g ** 2 + 6.22 * g ** 4)) * np.sqrt(fwhhG ** 2 + fwhhL ** 2)
        res = fwhhT / k
        filter_type = options.Filter
    else:
        l_cut = options.CutPoint
        filter_type = options.Filter

    if filter_type == "Bessel":
        if method == "FSD":
            l_cut = 0.9520778 / res
        cut = np.abs(t) <= l_cut
        filter_function = (1 - (t / l_cut) ** 2) ** 2 * cut

    elif filter_type == "Blackman-Lorenz 3-term":
        if method == "FSD":
            l_cut = 1.1795 / res
        cut = np.abs(t) <= l_cut
        filter_function = (0.4089701 + 0.5 * np.cos(np.pi * t / l_cut) +
                           0.0910299 * np.cos(2 * np.pi * t / l_cut)) * cut

    elif filter_type == "Triangle-Sq":
        if method == "FSD":
            l_cut = 1.1795 / res
        cut = np.abs(t) <= l_cut
        filter_function = (1 - np.abs(t) / l_cut) ** 2 * cut

    elif filter_type == "Sinc-Sq":
        if method == "FSD":
            l_cut = 1.086818 / res
        cut = np.abs(t) <= l_cut
        with np.errstate(divide='ignore', invalid='ignore'):
            sinc = np.sin(np.pi * t / l_cut) / (np.pi * t / l_cut)
        sinc[np.isinf(sinc)] = 1  # 替换无穷大值为 1
        filter_function = sinc ** 2 * cut

    elif filter_type == "Triangle":
        if method == "FSD":
            l_cut = 0.885893 / res
        cut = np.abs(t) <= l_cut
        filter_function = (1 - np.abs(t) / l_cut) * cut

    elif filter_type == "Truncated Gaussian":
        if method == "FSD":
            l_cut = 1.0151 / res
        cut = np.abs(t) <= l_cut
        filter_function = np.exp(-np.pi ** 2 / np.log(2) * (t / (2 * l_cut)) ** 2) * cut

    elif filter_type == "Gaussian":
        if method == "FSD":
            l_cut = 1 / res
        filter_function = np.exp(-np.pi ** 2 / np.log(2) * (t / (2 * l_cut)) ** 2)

    elif filter_type == "Lorentzian":
        if method == "FSD":
            l_cut = 1 / res
        filter_function = np.exp(-np.pi * np.abs(t) / l_cut)

    elif filter_type == "Boxcar":
        if method == "FSD":
            l_cut = 0.6034 / res
        filter_function = np.abs(t) <= l_cut

    elif filter_type == "Norton-Beer Medium":
        if method == "FSD":
            l_cut = 0.8447 / res
        cut = np.abs(t) <= l_cut
        filter_function = (0.152442 - 0.136176 * (1 - (t / l_cut) ** 2) +
                           0.983734 * (1 - (t / l_cut) ** 2) ** 2) * cut

    elif filter_type == "Norton-Beer Strong":
        if method == "FSD":
            l_cut = 0.9439 / res
        cut = np.abs(t) <= l_cut
        filter_function = (0.045335 + 0.554883 * (1 - (t / l_cut) ** 2) +
                           0.399782 * (1 - (t / l_cut) ** 2) ** 3) * cut

    elif filter_type == "Hamming":
        if method == "FSD":
            l_cut = 0.9076 / res
        cut = np.abs(t) <= l_cut
        filter_function = (0.54 + 0.46 * np.cos(np.pi * t / l_cut)) * cut

    elif filter_type == "Hanning":
        if method == "FSD":
            l_cut = 1 / res
        cut = np.abs(t) <= l_cut
        filter_function = (0.5 + 0.5 * np.cos(np.pi * t / l_cut)) * cut

    elif filter_type == "Blackman":
        if method == "FSD":
            l_cut = 1.1127 / res
        cut = np.abs(t) <= l_cut
        filter_function = (0.42659071 + 0.49656062 * np.cos(np.pi * t / l_cut) +
                           0.07684867 * np.cos(2 * np.pi * t / l_cut)) * cut

    elif filter_type == "Blackman-Harris 3-term":
        if method == "FSD":
            l_cut = 1.1370 / res
        cut = np.abs(t) <= l_cut
        filter_function = (0.42659071 + 0.49656062 * np.cos(np.pi * t / l_cut) +
                           0.07684867 * np.cos(2 * np.pi * t / l_cut)) * cut

    else:
        raise ValueError(f"Unsupported filter type: {filter_type}")

    return filter_function
