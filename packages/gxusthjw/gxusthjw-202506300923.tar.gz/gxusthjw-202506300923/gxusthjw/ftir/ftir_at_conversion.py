#!/usr/bin/env python3
# --*-- coding: utf-8 --*--
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        ftir_at_conversion.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“FTIR吸光度（absorbance）与
#                   其透过率（transmittance）相互转换”的方法。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/15     finish
# ------------------------------------------------------------------
# 导包 ==============================================================
import numpy as np
import numpy.typing as npt

# 定义 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defines the methods for interconversion between FTIR absorbance and
 transmittance.
"""

__all__ = [
    'transmittance_to_absorbance',
    'absorbance_to_transmittance',
    'transmittance_to_absorbance2',
    'absorbance_to_transmittance2'
]


# ==================================================================


def transmittance_to_absorbance(transmittance: npt.ArrayLike) -> \
        npt.NDArray[np.float64]:
    """
    将透过率转换为吸光度。

    理论公式： A = log10(100/T) = log10(100) - log10(T) = 2.0 - log10(T)

    此结果的图形与OMNIC输出结果的图形完全重合，但数值有差异，
    这种差异可能与OMNIC软件对x坐标进行了插值有关。

    :param transmittance: 透过率，单位：%
    :return: 吸光度，没单位，可写为：a.u.。
    :rtype: npt.NDArray[np.float64]
    """
    transmittance_ndarray = np.asarray(transmittance)
    with np.errstate(all='ignore'):
        return 2.0 - np.log10(transmittance_ndarray)


def transmittance_to_absorbance2(transmittance: npt.ArrayLike) -> \
        npt.NDArray[np.float64]:
    """
    将透过率转换为吸光度。

    理论公式： A = log10(100/T)

    此函数与transmittance_to_absorbance的计算结果一致。

    :param transmittance: 透过率，单位：%
    :return: 吸光度，没单位，可写为：a.u.。
    :rtype: npt.NDArray[np.float64]
    """
    transmittance_ndarray = np.asarray(transmittance)
    with np.errstate(all='ignore'):
        return np.log10(100 / transmittance_ndarray)


def absorbance_to_transmittance(absorbance: npt.ArrayLike) -> \
        npt.NDArray[np.float64]:
    """
    将吸光度转换为透过率。

    理论公式：10^(2-A)

    先将transmittance变换absorbance，再将absorbance变换为transmittance，
    变换前后图形完全重合。

    :param absorbance: 吸光度，没单位，可写为：a.u.。
    :return: 透过率，单位：%
    :rtype: npt.NDArray[np.float64]
    """
    return 10 ** (2.0 - np.asarray(absorbance))


def absorbance_to_transmittance2(absorbance: npt.ArrayLike) -> \
        npt.NDArray[np.float64]:
    """
    将吸光度转换为透过率。

    理论公式：100 / (10^A)

    此函数与absorbance_to_transmittance的计算结果一致。

    :param absorbance: 吸光度，没单位，可写为：a.u.。
    :return: 透过率，单位：%
    :rtype: npt.NDArray[np.float64]
    """
    return 100 / (10 ** np.asarray(absorbance))
# ===================================================================
