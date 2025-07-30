# File Name:        deriv_gl_cy.pyi
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      基于格伦瓦尔德·莱特尼科夫（Grunwald-Letnikov,GL）
#                   定义，计算指定数据的指定阶（可为任意阶）导数
#                   —— Cython加速版。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/13     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import numpy as np

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Compute the specified-order (can be any order) derivative of 
the given data based on the Grunwald-Letnikov (GL) definition 
— Cython-accelerated version.
"""

__all__ = [
    'deriv_gl_cy',
    'deriv_gl_cy_0'，
]


# 定义 ==============================================================
def deriv_gl_cy(data_y: np.ndarray, deriv_order: float) -> np.ndarray:
    """
    基于格伦瓦尔德·莱特尼科夫（Grunwald-Letnikov,GL）定义，
    计算指定数据（data_y）的指定阶（deriv_order）导数。

    使用Cython实现，该实现的运行结果在某些deriv_order值（deriv_order=100时）
    与Python版本不一致，但性能显著提升。

    此算法由广西科技大学“姚志湘”老师开发的Matlab代码翻译而来，
    对应matlab代码为：glfd.m

    :param data_y: 原数据。
    :param deriv_order: 导数的阶。
    :return: 导数数据。
    """
    ...


def deriv_gl_cy_0(data_y: np.ndarray, deriv_order: float) -> np.ndarray:
    """
    基于格伦瓦尔德·莱特尼科夫（Grunwald-Letnikov,GL）定义，
    计算指定数据（data_y）的指定阶（deriv_order）导数。

    使用Cython实现，该实现的运行结果与Python版本一致，
    但性能并没有显著提升。
    
    此算法由广西科技大学“姚志湘”老师开发的Matlab代码翻译而来，
    对应matlab代码为：glfd.m

    :param data_y: 原数据。
    :param deriv_order: 导数的阶。
    :return: 导数数据。
    """
    ...
