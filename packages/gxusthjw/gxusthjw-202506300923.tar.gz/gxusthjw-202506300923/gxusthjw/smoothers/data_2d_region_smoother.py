#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        data_2d_region_smoother.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“表征`二维数据区域平滑器`的类”。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2024/10/27     finish
# ------------------------------------------------------------------
# 导包 ==============================================================
from typing import Optional
from abc import ABC, abstractmethod

import numpy.typing as npt
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from ..commons import NumberSequence, Data2dRegion
from ..matplotlibs import create_mpl_ax
from ..statistics import FittingStatistics

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining a class that represents `the smoother for 
the region of two-dimensional data`.
"""

__all__ = [
    "Data2dRegionSmoother",
]


# 定义 ==============================================================


class Data2dRegionSmoother(Data2dRegion, ABC):
    """
    类`Data2dRegionSmoother`表征“二维数据区域平滑器”。

    类`Data2dRegionSmoother`类是一个基类，
    所有`二维数据区域平滑器`均应继承自此类。
    """

    def __init__(
            self,
            data_y: NumberSequence,
            data_x: Optional[NumberSequence] = None,
            region_start: int = 0,
            region_length: Optional[int] = None,
    ):
        """
        类`Data2dRegionSmoother`的初始化方法。

        :param data_y: 因变量（数据y）。
        :param data_x: 自变量（数据x,可选）。
        :param region_start: “数据区域”的起始索引位置，默认值为0。
        :param region_length: “数据区域”的长度，默认值为`data_len - region_start`。
        """
        super(Data2dRegionSmoother, self).__init__(
            data_y, data_x, region_start, region_length
        )

    # -------------------------------------------------------------
    @abstractmethod
    def do_smooth(self) -> npt.NDArray:
        """
        执行平滑操作。

        :return: 平滑后的数据。
        """
        pass

    @property
    def residuals(self) -> npt.NDArray:
        """
        计算平滑后的残差。

        :return: 平滑后的残差。
        """
        return self.region_data_y - self.do_smooth()

    # -------------------------------------------------------------
    def plot_comparison(self, ax=None, **kwargs) -> plt.Axes:
        """
        绘制平滑前后的对比图。

            可选关键字参数：

                1. s: 平滑前数据散点的大小，缺省值：5。

                2. marker: 平滑前数据散点的形状，缺省值：'o'。

                3. is_show: 指示是否显示图形，缺省值：False。

                4. color: 滑前数据曲线的颜色，缺省值：‘r'。

                5. linewidth: 滑前数据曲线的线宽，缺省值：3。

        :param ax: 轴对象。
        :param kwargs: 绘图所需关键字参数。
        :return: 绘图后的轴对象。
        """
        fig, ax = create_mpl_ax(ax)
        region_data_y_smoothed = self.do_smooth()
        # ---------------------------------------------------
        s = kwargs.pop("s", 5)
        marker = kwargs.pop("marker", "o")
        is_show = kwargs.pop("is_show", False)
        color = kwargs.pop("color", "r")
        linewidth = kwargs.pop("linewidth", 3)
        # ----------------------------------------------------
        ax.cla()
        ax.scatter(self.region_data_x, self.region_data_y, s=s, marker=marker)
        ax.plot(
            self.region_data_x, region_data_y_smoothed, color=color, linewidth=linewidth
        )
        ax.set_xlabel(f"Data Region X [{self.region_start},{self.region_data_stop}]")
        ax.set_ylabel("Data Region Y")
        fig_legend_other_text = "Comparison x:[{:.0f},{:.0f}]".format(
            self.region_data_x[0], self.region_data_x[-1]
        )
        handles, labels = ax.get_legend_handles_labels()
        handles.append(mpatches.Patch(color="none", label=fig_legend_other_text))
        plt.rc("legend", fontsize=10)
        ax.legend(loc="best", handles=handles)
        # ----------------------------------------------------
        if is_show:
            plt.show()
        return ax

    def plot_residuals(self, ax=None, **kwargs) -> plt.Axes:
        """
        绘制平滑后的残差图。

            可选关键字参数：

                1. is_show: 指示是否显示图形。

        :param ax: 轴对象。
        :param kwargs: 绘图所需关键字参数。
        :return: 绘图后的轴对象。
        """
        fig, ax = create_mpl_ax(ax)
        residuals = self.residuals
        # ----------------------------------------------------
        is_show = kwargs.pop("is_show", False)
        # ----------------------------------------------------
        ax.cla()
        ax.plot(self.region_data_x, residuals)
        ax.set_xlabel(f"Data Region X [{self.region_start},{self.region_data_stop}]")
        ax.set_ylabel("Data Region Y")
        fig_legend_other_text = "Residual x:[{:.0f},{:.0f}]".format(
            self.region_data_x[0], self.region_data_x[-1]
        )
        handles, labels = ax.get_legend_handles_labels()
        handles.append(mpatches.Patch(color="none", label=fig_legend_other_text))
        plt.rc("legend", fontsize=10)
        ax.legend(loc="best", handles=handles)
        # ----------------------------------------------------
        if is_show:
            plt.show()
        return ax

    def update_plot(self, *args, **kwargs):
        """
        更新绘图。

            可选关键字参数：

                1. s: 平滑前数据散点的大小，缺省值：5。

                2. marker:平滑前数据散点的形状，缺省值：'o'。

                3. color: 滑前数据曲线的颜色，缺省值：‘r'。

                4. linewidth: 滑前数据曲线的线宽，缺省值：3。

            注意：此方法类外部不可调用。

        :param args: 可选参数。
        :param kwargs: 可选关键字参数。
        """
        ax1, ax2 = args
        # ----------------------------------------------------
        s = kwargs.get("s", 5)
        marker = kwargs.get("marker", "o")
        color = kwargs.pop("color", "r")
        linewidth = kwargs.pop("linewidth", 3)
        # ----------------------------------------------------
        self.plot_comparison(
            ax=ax1, s=s, marker=marker, color=color, linewidth=linewidth, is_show=False
        )
        self.plot_residuals(ax=ax2, is_show=False)

    def plot(self, **kwargs):
        """
        绘图。

            可选关键字参数：

                1. title: 图形的标题，缺省值：'Smooth'。

                2. figsize: 图形的尺寸，缺省值：宽度（width）为：12，高度（height）为8。

                3. is_show: 指示是否显示图形，缺省值：False。

                4. s: 平滑前数据散点的大小，缺省值：5。

                5. marker:平滑前数据散点的形状，缺省值：'o'。

                6. color: 滑前数据曲线的颜色，缺省值：‘r'。

                7. linewidth: 滑前数据曲线的线宽，缺省值：3。

        :param kwargs: 绘图所需关键字参数。
        :return: 图形窗口，图形轴，图形轴
        :rtype: plt.Figure, plt.Axes, plt.Axes
        """
        title = kwargs.pop("title", "Smooth")
        figsize = kwargs.pop("figsize", (15, 8))
        s = kwargs.pop("s", 5)
        marker = kwargs.pop("marker", "o")
        is_show = kwargs.pop("is_show", False)
        color = kwargs.pop("color", "r")
        linewidth = kwargs.pop("linewidth", 3)
        # ----------------------------------------------------
        # 绘图时显示中文。
        plt.rcParams["font.family"] = "SimHei"
        plt.rcParams["axes.unicode_minus"] = False
        fig, (ax1, ax2) = plt.subplots(
            1,
            2,
            figsize=figsize,
            gridspec_kw={
                "width_ratios": [1, 1],
                "wspace": 0.2,
                "left": 0.05,
                "right": 0.95,
            },
        )
        fig.suptitle(title)
        self.update_plot(ax1, ax2, color=color, linewidth=linewidth, s=s, marker=marker)
        # ----------------------------------------------------
        if is_show:
            plt.show()
        return fig, ax1, ax2

    # -----------------------------------------------------------------------
    @abstractmethod
    def smooth(self, **kwargs):
        """
        执行带参数的平滑。

        :param kwargs: 可选关键字参数。
        :return: 平滑后的数据。
        """
        pass

    @abstractmethod
    def interactive_smooth(self, **kwargs):
        """
        交互式执行平滑。

        :param kwargs: 可选关键字参数。
        :return: 平滑结果，...。
        """
        pass

    # -------------------------------------------------------------
    # noinspection PyUnusedLocal
    def residuals_analysis(self, **kwargs):
        """
        执行平滑后的残差分析。

        :param kwargs: 可选关键字参数。
        :return: 拟合统计结果，...。
        """
        return FittingStatistics(
            self.region_data_y, self.residuals, x=self.region_data_x
        )

# ===================================================================
