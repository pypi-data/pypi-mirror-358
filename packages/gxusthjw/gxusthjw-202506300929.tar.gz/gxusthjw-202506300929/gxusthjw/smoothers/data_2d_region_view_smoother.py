#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        data_2d_region_view_smoother.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“表征`带可调视图区的二维数据区域平滑器`的类”。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2024/10/27     finish
# ------------------------------------------------------------------
# 导包 ==============================================================
from abc import ABC
from typing import Optional, override

import numpy.typing as npt
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches

from ..commons import NumberSequence
from ..matplotlibs import create_mpl_ax

from .data_2d_region_smoother import Data2dRegionSmoother

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining a class that represents `the smoother with adjustable view for 
the region of two-dimensional data`.
"""

__all__ = [
    "Data2dRegionViewSmoother",
]


# 定义 ==============================================================
class Data2dRegionViewSmoother(Data2dRegionSmoother, ABC):
    """
    类`Data2dRegionViewSmoother`表征`带可调视图区的二维数据区域平滑器`。

    类`Data2dRegionViewSmoother`类是一个基类，
    所有`带可调视图区的二维数据区域平滑器`均应继承自此类。
    """

    def __init__(
        self,
        data_y: NumberSequence,
        data_x: Optional[NumberSequence] = None,
        region_start: int = 0,
        region_length: Optional[int] = None,
        view_start: Optional[int] = 0,
        view_length: Optional[int] = None,
    ):
        """
        类`Data2dRegionViewSmoother`的初始化方法。

        :param data_y: 因变量（数据y）。
        :param data_x: 自变量（数据x,可选）。
        :param region_start: “数据区域”的起始位置。
        :param region_length: “数据区域”的长度。
        :param view_start: “数据视图区域”的起始位置。
        :param view_length: “数据视图区域”的长度。
        """
        super(Data2dRegionViewSmoother, self).__init__(
            data_y, data_x, region_start, region_length
        )
        # ------------------------------------------------------------------
        self.__view_start = view_start
        if view_length is not None:
            self.__view_length = view_length
        else:
            self.__view_length = self.data_len - self.__view_start
        # 检查数据。
        self.view_weak_check()
        # ------------------------------------------------------------------

    def view_weak_check(self):
        """
        检查数据。

            注意，此方法所实现的数据检查并不完整。
        """
        if (
            self.__view_start < 0
            or self.__view_start >= self.data_len
            or self.__view_length < 0
        ):
            raise ValueError("The view_start or view_length is invalid.")

    # -------------------------------------------------------------
    @property
    def view_start(self):
        """
        返回“视图区域”的起始位置。

        :return: “视图区域”的起始位置。
        """
        return self.__view_start

    @view_start.setter
    def view_start(self, view_start: int):
        """
        设置“视图区域”的起始位置。

            注意：最好只在此类或此类的子类中调用。

        :param view_start: “视图区域”的起始位置。
        """
        if self.view_start != view_start:
            self.__view_start = view_start
            self.is_parameter_changed = True

    @property
    def view_length(self):
        """
        返回“视图区域”的长度。

        :return: “视图区域”的长度。
        """
        return self.__view_length

    @view_length.setter
    def view_length(self, view_length: int):
        """
        设置“视图区域”的长度。

            注意：最好只在此类或此类的子类中调用。

        :param view_length: “视图区域”的长度。
        """
        if self.view_length != view_length:
            self.__view_length = view_length
            self.is_parameter_changed = True

    # --------------------------------------------------------------
    @property
    def view_stop(self):
        """
        返回“视图区域”的终止位置（不包含）。

        :return: “视图区域”的终止位置（不包含）。
        """
        return self.view_start + self.view_length

    @property
    def view_slice(self) -> slice:
        """
        返回“视图区域”的slice对象。

            slice对象的创建方式：

                1. slice(stop)

                2. slice(start, stop[, step])

        :return: “视图区域”的slice对象。
        """
        return slice(self.view_start, self.view_stop, 1)

    @view_slice.setter
    def view_slice(self, view_slice: slice):
        """
        设置“视图区域”的slice对象。

            注意：

                1. 创建slice对象时，如果不指定start，则start缺省为None，而非1。

                2. 创建slice对象时，如果不指定step，则step缺省为None，而非1。

                3. start,stop,step 都有可能是None

                4. 最好只在此类或此类的子类中调用。

        :param view_slice: “视图区域”的slice对象。
        """
        if view_slice.step in (None, 1):
            self.view_start = view_slice.start if view_slice.start is not None else 0
            stop = view_slice.stop if view_slice.stop is not None else self.view_stop
            self.view_length = stop - self.view_start
        else:
            raise ValueError(
                "Expected view_slice.step is None or view_slice.step == 1."
            )

    def set_view_slice(self, start: int, length: int):
        """
        设置“视图区域”的起始索引和长度。

            注意：最好只在此类或此类的子类中调用。

        :param start: “视图区域”的起始索引。
        :param length: “视图区域”的长度。
        """
        self.view_start = start
        self.view_length = length

    @property
    def view_data_y(self) -> npt.NDArray:
        """
        返回“视图区域”的数据y。

        :return: “视图区域”的数据y。
        """
        return self.data_y[self.view_slice]

    @property
    def view_data_x(self) -> npt.NDArray:
        """
        返回“视图区域”的数据x。

        :return: “视图区域”的数据x。
        """
        return self.data_x[self.view_slice]

    @property
    def view_data_len(self) -> int:
        """
        返回“视图区域”的数据长度。

            注意：

                1. self.view_data_len有可能不等于self.view_length。

                2. 理论上，self.view_data_len <= self.view_length。

        :return: “视图区域”的数据长度。
        """
        self.view_data_check()
        return self.view_data_y.shape[0]

    @property
    def view_data_stop(self):
        """
        返回“视图区域”的数据在原始数据上的实际终止索引。

        :return: “视图区域”的数据在原始数据上的实际终止索引。
        """
        return self.view_start + self.view_data_len

    def view_data_check(self):
        """
        检查“视图区域”的数据是否具有相同的长度。

            如果不具有相同的长度，则抛出ValueError异常。
        """
        if self.view_data_x.shape != self.view_data_y.shape:
            raise ValueError("Expected view_data_x.shape == view_data_y.shape.")

    @property
    def is_view_data_aligned(self):
        """
        判断“视图区域”的数据是否具有相同的长度。

        :return: 如果具有相同的长度，返回True，否则返回False。
        """
        return self.view_data_x.shape == self.view_data_y.shape

    # --------------------------------------------------------------
    def plot_view(self, ax=None, **kwargs) -> plt.Axes:
        """
        绘制平滑前后的视图。

            消耗掉的可选关键字参数：

                1. s: 平滑前数据散点的大小，缺省值：5。

                2. marker:平滑前数据散点的形状，缺省值：'o'。

                3. is_show: 指示是否显示图形。

                4. color: 滑前数据曲线的颜色，缺省值：‘r'。

                5. linewidth: 滑前数据曲线的线宽，缺省值：3。

        :param ax: 轴对象。
        :param kwargs: 绘图所需关键字参数。
        :return:绘图后的轴对象。
        """
        fig, ax = create_mpl_ax(ax)
        region_y_smoothed = self.do_smooth()
        # ---------------------------------------------------
        s = kwargs.pop("s", 5)
        marker = kwargs.pop("marker", "o")
        is_show = kwargs.pop("is_show", False)
        color = kwargs.pop("color", "r")
        linewidth = kwargs.pop("linewidth", 3)
        # ----------------------------------------------------
        ax.cla()
        ax.scatter(self.view_data_x, self.view_data_y, s=s, marker=marker)
        ax.plot(self.region_data_x, region_y_smoothed, color=color, linewidth=linewidth)
        ax.set_xlabel(f"Data Region X [{self.region_start},{self.region_data_stop}]")
        ax.set_ylabel("Data Region Y")
        fig_legend_other_text = "View x:[{:.0f},{:.0f}]".format(
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

    @override
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
        ax1, ax2, ax3 = args
        # ----------------------------------------------------
        s = kwargs.get("s", 5)
        marker = kwargs.get("marker", "o")
        color = kwargs.pop("color", "r")
        linewidth = kwargs.pop("linewidth", 3)
        # ----------------------------------------------------
        self.plot_comparison(
            ax=ax1, s=s, color=color, linewidth=linewidth, marker=marker, is_show=False
        )
        self.plot_residuals(ax=ax2, is_show=False)
        self.plot_view(
            ax=ax3, color=color, linewidth=linewidth, s=s, marker=marker, is_show=False
        )

    @override
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
        :return: 图形窗口，图形轴，图形轴，图形轴
        :rtype: plt.Figure, plt.Axes, plt.Axes, plt.Axes
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
        fig, (ax1, ax2, ax3) = plt.subplots(
            1,
            3,
            figsize=figsize,
            gridspec_kw={
                "width_ratios": [1, 1, 1],
                "wspace": 0.2,
                "left": 0.05,
                "right": 0.95,
            },
        )
        fig.suptitle(title)
        self.update_plot(
            ax1, ax2, ax3, color=color, linewidth=linewidth, s=s, marker=marker
        )
        # ----------------------------------------------------
        if is_show:
            plt.show()
        return fig, ax1, ax2, ax3


# ===============================================================
