#!/usr/bin/env python3
# --*-- coding: utf-8 --*--
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        fourier_filter.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“傅里叶滤波函数”。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2023/10/15     revise
# ------------------------------------------------------------------
# 导包 =============================================================
import numpy as np
import numpy.typing as npt
from scipy.fft import fft, ifft


# ==================================================================
def shape_func(x: npt.NDArray[np.float64],
               pos: float, fwhm: float, n: float):
    """
    计算高斯滤波所用的峰形函数的值。

    （1）n==0时，此函数的结果与洛伦茨峰形函数的结果一致。

    （2）n==1时，此函数的结果与高斯形函数的结果一致。

    （2）n>1时，此函数的结果随着n值的增加，高斯曲线越矩形化。

    :param x: 函数的自变量。
    :param pos:函数曲线的中心位置。
    :param fwhm:函数的半高全宽。
    :param n: 峰形变换指数。
    :return:峰形函数的值。
    """
    if n == 0:
        return np.ones(len(x)) / (1 + ((x - pos) / (0.5 * fwhm)) ** 2)
    else:
        return np.exp(-((x - pos) / (0.6 * fwhm)) ** (2 * round(n)))


# noinspection PyUnboundLocalVariable
def fourier_filter(xvector: npt.NDArray[np.float64],
                   yvector: npt.NDArray[np.float64],
                   center_frequency: float,
                   filter_width: float,
                   filter_shape: float,
                   filter_mode: int):
    """
    傅里叶滤波器。

    对于此参数filter_mode，支持如下模式：

      1 = 'Band-pass'

      2 = 'Lowpass'

      3 = 'Highpass',

      4 = 'Band-reject (notch)',

      5 = 'Comb pass'

      6 = 'Comb notch'

    :param xvector: 自变量。
    :param yvector: 因变量（谱数据）
    :param center_frequency: 中心频率
    :param filter_width: 通带宽度（半高全宽）。
    :param filter_shape: 滤波函数的形状参数。
    :param filter_mode: 滤波模式。
    :return: 滤波后的谱数据。
    """
    fy = fft(yvector)
    lft1 = np.arange(0, (len(fy) // 2)) + 1
    lft2 = np.arange(len(fy) // 2, len(fy)) + 1
    match filter_mode:
        case 1:
            ffilter1 = shape_func(
                lft1, center_frequency + 1, filter_width,
                filter_shape)
            ffilter2 = shape_func(
                lft2, len(fy) - center_frequency + 1, filter_width,
                filter_shape)
            ffilter = np.concatenate((ffilter1, ffilter2))
        case 2:
            center_frequency = len(xvector) / 2
            ffilter1 = shape_func(
                lft1, center_frequency + 1, filter_width,
                filter_shape)
            ffilter2 = shape_func(
                lft2, len(fy) - center_frequency + 1, filter_width,
                filter_shape)
            ffilter = np.concatenate((ffilter1, ffilter2))
        case 3:
            center_frequency = 0
            ffilter1 = shape_func(
                lft1, center_frequency + 1, filter_width,
                filter_shape)
            ffilter2 = shape_func(
                lft2, len(fy) - center_frequency + 1, filter_width,
                filter_shape)
            ffilter = np.concatenate((ffilter1, ffilter2))
        case 4:
            ffilter1 = shape_func(
                lft1, center_frequency + 1, filter_width,
                filter_shape)
            ffilter2 = shape_func(
                lft2, len(fy) - center_frequency + 1, filter_width,
                filter_shape)
            ffilter = 1 - np.concatenate((ffilter1, ffilter2))
        case 5:
            n = 2
            ffilter1 = shape_func(
                lft1, center_frequency + 1, filter_width,
                filter_shape)
            ffilter2 = shape_func(
                lft2, len(fy) - center_frequency + 1, filter_width,
                filter_shape)
            while n < 50:
                ffilter1 = ffilter1 + shape_func(
                    lft1, n * (center_frequency + 1),
                    filter_width, filter_shape)
                ffilter2 = ffilter2 + shape_func(
                    lft2, len(fy) - n * (center_frequency + 1),
                    filter_width, filter_shape)
                n = n + 1
            ffilter = np.concatenate((ffilter1, ffilter2))
        case 6:
            n = 2
            ffilter1 = shape_func(
                lft1, center_frequency + 1, filter_width,
                filter_shape)
            ffilter2 = shape_func(
                lft2, len(fy) - center_frequency + 1, filter_width,
                filter_shape)
            while n < 50:
                ffilter1 = ffilter1 + shape_func(
                    lft1, n * (center_frequency + 1),
                    filter_width, filter_shape)
                ffilter2 = ffilter2 + shape_func(
                    lft2, len(fy) - n * (center_frequency + 1),
                    filter_width, filter_shape)
                n = n + 1
            ffilter = 1 - np.concatenate((ffilter1, ffilter2))
        case _:
            raise ValueError("Expected the filter_mode must be [1,6], "
                             "but got {}.".format(filter_mode))

    if len(fy) > len(ffilter):
        ffilter = np.concatenate((ffilter, ffilter[1]))

    ffy = fy * ffilter

    return np.real(ifft(ffy))
