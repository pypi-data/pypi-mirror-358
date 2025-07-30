#!/usr/bin/env python3
# --*-- coding: utf-8 --*--
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        peak_shape.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“峰形函数”。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/17     revise
# ------------------------------------------------------------------
# 导包 =============================================================
import numpy as np
import numpy.typing as npt

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defines "peak-shape function".
"""

__all__ = [
    "gauss",
    "lorentz",
    "logistic",
    "gauss_lorentz",
]


# 定义 ==============================================================

def gauss(x: npt.NDArray[np.float64],
          center: float, fwhm: float) -> npt.NDArray[np.float64]:
    """
    计算高斯函数值。

    :param x: 函数的自变量。
    :param center: 高斯函数的中心位置。
    :param fwhm: 高斯函数的半高全宽。
    :return: 高斯函数值。
    """
    return np.exp(-((x - center) / (0.60056120439323 * fwhm)) ** 2)


def lorentz(x: npt.NDArray[np.float64],
            center: float,
            fwhm: float) -> npt.NDArray[np.float64]:
    """
    计算洛伦茨函数值。

    :param x: 函数的自变量。
    :param center: 洛伦茨函数的中心位置。
    :param fwhm: 洛伦茨函数的半高全宽。
    :return: 洛伦茨函数值。
    """
    return 1.0 / (1.0 + ((x - center) / (0.5 * fwhm)) ** 2.0)


def logistic(x: npt.NDArray[np.float64],
             center: float, fwhm: float) -> npt.NDArray[np.float64]:
    """
    计算逻辑函数的值。

    :param x:函数的自变量。
    :param center:逻辑函数的中心位置。
    :param fwhm:逻辑函数的半高全宽。
    :return:逻辑函数值。
    """
    n = np.exp(-((x - center) / (0.477 * fwhm)) ** 2)
    return (2 * n) / (1 + n)


def gauss_lorentz(x: npt.NDArray[np.float64],
                  center: float, fwhm: float, m: float) -> npt.NDArray[np.float64]:
    """
    计算高斯-洛伦茨复合函数的值。

    :param x:函数的自变量。
    :param center:高斯-洛伦茨复合函数的中心位置。
    :param fwhm:高斯-洛伦茨复合函数的半高全宽。
    :param m:高斯组分，单位：%。
    :return:高斯-洛伦茨复合函数值。
    """
    return ((m / 100) * gauss(x, center, fwhm) +
            (1 - (m / 100)) * lorentz(x, center, fwhm))
