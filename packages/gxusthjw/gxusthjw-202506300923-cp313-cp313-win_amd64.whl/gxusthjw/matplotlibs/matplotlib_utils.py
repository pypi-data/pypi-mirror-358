#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        matplotlib_utils.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义与`matplotlib`相关的工具方法。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/27     finish
# ------------------------------------------------------------------
# 导包 ============================================================

# 声明 ============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining some helper functions associated with `matplotlib`
"""

__all__ = [
    'import_mpl',
    'create_mpl_ax',
    'create_mpl_fig',
]


# 定义 ============================================================
def import_mpl():
    """
    导入`matplotlib`模块，并将其命名为plt。

        该模块不应被模块外调用。

        参考自：statsmodels.graphics.utils._import_mpl()

    :return: plt。
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        raise ImportError("Matplotlib is not found.")
    return plt


def create_mpl_ax(ax=None):
    """
    当需要单个绘图轴时，可用此函数创建。

        参考自：statsmodels.graphics.utils.create_mpl_ax

    :param ax: 绘图轴。
    :return: fig,ax
    """
    if ax is None:
        plt = import_mpl()
        fig = plt.figure()
        ax = fig.add_subplot(111)
    else:
        fig = ax.figure
    return fig, ax


def create_mpl_fig(fig=None, figsize=None):
    """
    当需要一个绘图窗时，可用此函数创建。

        参考自：statsmodels.graphics.utils.create_mpl_fig

    :param fig: 绘图窗。
    :param figsize: 绘图窗大小。
    :return: fig
    """
    if fig is None:
        plt = import_mpl()
        fig = plt.figure(figsize=figsize)
    return fig
