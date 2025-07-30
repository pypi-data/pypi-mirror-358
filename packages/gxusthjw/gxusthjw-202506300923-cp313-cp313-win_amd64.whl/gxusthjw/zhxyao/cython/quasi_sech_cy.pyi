# File Name:        deriv_gl_cy.pyi
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“拟双曲正割函数”-Cython加速版。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/10     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import numpy as np

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defines 'quasi-hyperbolic Secant Function' 
— Cython-accelerated version.
"""

__all__ = [
    'sech_cy',
    'sech_cy_0',
    'quasi_sech_cy',
]


# 定义 ==============================================================
def sech_cy(x: np.ndarray, den_default: float = 0.0) -> np.ndarray:
    """
    计算双曲正割函数值：sech(x) = 2 / (exp(x) + exp(-x))。

    :param x: 自变量，一维 float64 类型数组。
    :param den_default: 分母接近零时使用的默认值。
    :return: 返回双曲正割函数值。
    """
    ...


def sech_cy_0(x: np.ndarray, den_default: float = 0.0) -> np.ndarray:
    """
    计算双曲正割函数值：sech(x) = 2 / (exp(x) + exp(-x))。

    :param x: 自变量，一维 float64 类型数组。
    :param den_default: 分母接近零时使用的默认值。
    :return: 返回双曲正割函数值。
    """
    ...


def quasi_sech_cy(x: np.ndarray, peak_width: float, peak_steepness: float) -> np.ndarray:
    """
    计算拟双曲正割函数值。

    :param x: 自变量，一维 float64 类型数组。
    :param peak_width: 峰宽参数。
    :param peak_steepness: 峰陡峭度指数。
    :return: 返回拟双曲正割函数值。
    """
    ...
