#!/usr/bin/env python3
# --*-- coding: utf-8 --*--
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        finite_normal_distribution.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义表征“有限区间正态分布”的类。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2024/07/11     create
#       Jiwei Huang        0.0.1         2025/06/27     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import math
import numpy as np

from scipy.stats import rv_continuous

# 定义 ============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defines the classes for representing finite normal distributions.
"""

__all__ = [
    'finite_norm_pdf',
    'finite_norm_cdf_od',
    'finite_norm_cdf',
    'FiniteNormalDistribution',
    'finite_norm'
]


# ==================================================================

def finite_norm_pdf(x: float, mu: float, k: float, d: float) -> float:
    """
    计算有限区间正态分布概率密度函数(Probability Density Function, PDF)的值。

    任何非法参数（即不满足要求的参数），均返回：0。

    :param x: 随机变量（自变量）。
    :param mu: 有限区间正态分布的期望（均值）。
    :param k: 有限区间正态分布的阶，必须大于等于0。
    :param d: 随机变量取值区间之半，必须大于0。
    """
    lower = mu - d
    upper = mu + d
    if x <= lower or x >= upper:
        return 0.0
    else:
        if k < 0 or d <= 0:
            return 0.0
        else:
            coef = (math.pow(2.0, -0.5 * math.pow(math.sin(k * math.pi), 2.0)) *
                    math.pow(math.pi, -0.5 * math.pow(math.cos(k * math.pi), 2.0)) *
                    math.gamma(1.5 + k)) / (math.gamma(1.0 + k))
            return coef * (math.pow(1.0 - math.pow((x - mu) / d, 2.0), k)) / d


def finite_norm_cdf_od(x: float, mu: float, k: float, d: float) -> float:
    """
    计算有限区间正态分布累积分布函数(Cumulative Distribution Function)的阶差。

    :param x: 随机变量（自变量）。
    :param mu: 有限区间正态分布的期望（均值）。
    :param k: 有限区间正态分布的阶
    :param d: 随机变量取值区间之半。
    """
    if k == 0:
        return - (mu - x) / (2 * d)
    elif k == 1:
        return -(mu - x) * (d + mu - x) * (d - mu + x) / (4 * math.pow(d, 3))
    elif k == 2:
        return -3 * (mu - x) * ((d + mu - x) ** 2) * ((d - mu + x) ** 2) / (16 * math.pow(d, 5))
    elif k == 3:
        return -5 * (mu - x) * ((d + mu - x) ** 3) * ((d - mu + x) ** 3) / (32 * math.pow(d, 7))
    elif k == 4:
        return -35 * (mu - x) * ((d + mu - x) ** 4) * ((d - mu + x) ** 4) / (256 * math.pow(d, 9))
    elif k == 5:
        return -63 * (mu - x) * ((d + mu - x) ** 5) * ((d - mu + x) ** 5) / (512 * math.pow(d, 11))
    else:
        coef = (math.pow(2, 0.25 * (-5 + math.cos(2 * k * math.pi))) *
                math.pow(d, -1 - 2 * k) * math.pow(math.pi, -0.5 * (math.cos((k * math.pi) ** 2))) *
                (math.gamma(0.5 + k))) / (math.gamma(1.0 + k))
        return - coef * (mu - x) * math.pow(d + mu - x, k) * math.pow(d - mu + x, k)


# noinspection PyUnnecessaryBackslash
def finite_norm_cdf(x: float, mu: float, k: float, d: float) -> float:
    """
    计算有限区间正态分布累积分布函数(Cumulative Distribution Function)的值。

    :param x: 随机变量（自变量）。
    :param mu: 有限区间正态分布的期望（均值）。
    :param k: 有限区间正态分布的阶
    :param d: 随机变量取值区间之半。
    """
    lower = mu - d
    upper = mu + d
    if x <= lower:
        return 0
    if x >= upper:
        return 1
    if k < 0 or d <= 0:
        return 0.0
    if k == 0:
        return (d - mu + x) / (2 * d)
    elif k == 1:
        return ((2 * d + mu - x) * ((d - mu + x) ** 2)) / (4 * (d ** 3))
    elif k == 2:
        return ((8 * (d ** 2) + 9 * d * (mu - x) + 3 * ((mu - x) ** 2)) * ((d - mu + x) ** 3)) / (16 * (d ** 5))
    elif k == 3:
        return ((16 * (d ** 3) + 29 * (d ** 2) * (mu - x) + 20 * d * ((mu - x) ** 2) + 5 * ((mu - x) ** 3)) * (
                (d - mu + x) ** 4)) / (32 * (d ** 7))
    elif k == 4:
        return ((128 * (d ** 4) + 325 * (d ** 3) * (mu - x) + 345 * (d ** 2) * ((mu - x) ** 2) +
                 175 * d * ((mu - x) ** 3) + 35 * ((mu - x) ** 4)) * ((d - mu + x) ** 5)) / (256 * (d ** 9))
    elif k == 5:
        return ((256 * (d ** 5) + 843 * (d ** 4) * (mu - x) + 1218 * (d ** 3) * ((mu - x) ** 2) +
                 938 * (d ** 2) * ((mu - x) ** 3) + 378 * d * ((mu - x) ** 4) +
                 63 * ((mu - x) ** 5)) * ((d - mu + x) ** 6)) / (512 * (d ** 11))
    else:
        od = finite_norm_cdf_od(x, mu, k, d)
        return finite_norm_cdf(x, mu, k - 1, d) + od


# noinspection PyMethodOverriding,PyMethodMayBeStatic
class FiniteNormalDistribution(rv_continuous):
    """
    类`FiniteNormalDistribution`表征“有限区间正态分布”。
    """

    def _argcheck(self, mu: float, sigma: float, factor: float):
        """
        检查分布的参数是否符合要求。

        要求：factor > 0

        :param mu: 有限区间正态分布的期望（均值）。
        :param sigma: 有限区间正态分布的偏差（均方差）。
        :param factor: 区间的尺度因子，区间宽度之半：d = factor * sigma。
        """
        return factor >= math.sqrt(3) and sigma > 0

    def _pdf(self, x, mu: float, sigma: float, factor: float):
        """
        重写`rv_continuous`的_pdf方法。

        :param x: 随机变量（自变量）。
        :param mu: 有限区间正态分布的期望（均值）。
        :param sigma: 有限区间正态分布的偏差（均方差）。
        :param factor: 区间的尺度因子，区间宽度之半：d = factor * sigma。
        """
        k = int((factor ** 2 - 3) / 2)
        d = math.sqrt((2 * k + 3) * (sigma ** 2))
        if isinstance(x, float):
            return finite_norm_pdf(x, mu, k, d)
        else:
            return np.array([finite_norm_pdf(xi, mu, k, d) for xi in np.array(x)])

    def _cdf(self, x, mu: float, sigma: float, factor: float):
        """
        重写`rv_continuous`的_cdf方法，
        计算有限区间正态分布累积分布函数(Cumulative Distribution Function)的值。

        :param x: 随机变量（自变量）。
        :param mu: 有限区间正态分布的期望（均值）。
        :param sigma: 有限区间正态分布的偏差（均方差）。
        :param factor: 区间的尺度因子，区间宽度之半：d = factor * sigma。
        """
        k = int((factor ** 2 - 3) / 2)
        d = math.sqrt((2 * k + 3) * (sigma ** 2))
        return finite_norm_cdf(x, mu, k, d)


finite_norm = FiniteNormalDistribution(name="finite_norm", shapes="mu,sigma,factor")
