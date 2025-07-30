#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        data_2d_region_view_sm_linear_fitter.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“表征`带可调视图区的二维数据区域线性拟合器`的类”。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2024/10/22     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import os
from typing import override, Optional

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.widgets import Slider, RadioButtons, Button, TextBox

from ..commons import NumberSequence, unique_string
from ..matplotlibs import create_mpl_ax
from ..smoothers import Data2dRegionViewSmoother
from ..statistics import FittingStatistics

from .sm_linear_fittings import linear_fitting_sm

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining a class that represents `the fitter with adjustable view for 
the region of two-dimensional data`.
"""

__all__ = [
    "Data2dRegionViewSmLinearFitter",
]


# 定义 ==============================================================
class Data2dRegionViewSmLinearFitter(Data2dRegionViewSmoother):
    """
    类`Data2dRegionViewSmLinearFitter`表征“带可调视图区的
      二维数据区域线性拟合器”。
    """

    def __init__(
        self,
        data_y: NumberSequence,
        data_x: Optional[NumberSequence] = None,
        region_start: Optional[int] = 0,
        region_length: Optional[int] = None,
        view_start: Optional[int] = 0,
        view_length: Optional[int] = None,
        method: Optional[str] = "ols",
    ):
        """
        类`Data2dRegionViewSmLinearFitter`的初始化方法。

        :param data_y: 因变量（数据y）。
        :param data_x: 自变量（数据x,可选）。
        :param region_start: “线性拟合区域”的起始位置。
        :param region_length: “线性拟合区域”的长度。
        :param view_start: “线性拟合视图区域”的起始位置。
        :param view_length: “线性拟合视图区域”的长度。
        :param method: 拟合方法。
        """
        super(Data2dRegionViewSmLinearFitter, self).__init__(
            data_y,
            data_x,
            region_start=region_start,
            region_length=region_length,
            view_start=view_start,
            view_length=view_length,
        )
        # ------------------------------------------------------------------
        self.__methods = ("ols", "rlm")
        self.__method = method.strip().lower()
        if self.__method not in self.__methods:
            raise ValueError(f"method must be one of {self.__methods}")
        # ------------------------------------------------------------------

    @property
    def method(self):
        """
        返回拟合方法。

        :return: 拟合方法。
        """
        return self.__method

    @method.setter
    def method(self, method: str):
        """
        设置拟合方法。

            注意：最好只在此类或此类的子类中调用。

        :param method: 拟合方法。
        """
        if method not in self.__methods:
            raise ValueError(f"method must be one of {self.__methods}")
        if method != self.method:
            self.__method = method
            self.__is_parameter_changed = True

    @property
    def methods(self):
        """
        获取所有支持的拟合方法。

        :return: 所有支持的拟合方法。
        """
        return self.__methods

    # -------------------------------------------------------------
    def plot_smooth_view(self, ax=None, **kwargs):
        """
        绘制平滑前后的视图。

            消耗掉的可选关键字参数：

                1. s: 平滑前数据散点的大小，缺省值：5。

                2. marker:平滑前数据散点的形状，缺省值：'o'。

                3. is_show: 指示是否显示图形。

        :param ax: 轴对象。
        :param kwargs: 绘图所需关键字参数。
        :return:绘图后的轴对象。
        """
        fig, ax = create_mpl_ax(ax)
        var_y_smoothed = self.do_smooth()
        # ---------------------------------------------------
        s = kwargs.pop("s", 5)
        marker = kwargs.pop("marker", "o")
        is_show = kwargs.pop("is_show", False)
        # ----------------------------------------------------
        ax.cla()
        ax.scatter(self.view_data_x, self.view_data_y, s=s, marker=marker)
        ax.plot(self.region_data_x, var_y_smoothed, color="r", linewidth=3)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
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
    def update_plot(self, ax1, ax2, ax3, s=5, marker="o"):
        """
        更新绘图。

            注意：此方法类外部不可调用。

        :param ax1: 对比图的轴。
        :param ax2: 残差轴的图。
        :param ax3: 视图。
        :param marker: 平滑前数据散点的形状，缺省值：'o'。
        :param s: 平滑前数据散点的大小，缺省值：5。
        """
        self.do_smooth()
        self.plot_comparison(ax=ax1, s=s, marker=marker, is_show=False)
        self.plot_residuals(ax=ax2, is_show=False)
        self.plot_smooth_view(ax=ax3, s=s, marker=marker, is_show=False)

    @override
    def plot(self, **kwargs):
        """
        绘图。

            消耗掉的可选关键字参数：

                1. title: 图形的标题，缺省值：'Smooth'。

                2. figsize: 图形的尺寸，缺省值：宽度（width）为：12，高度（height）为8。

                3. is_show: 指示是否显示图形，缺省值：False。

                4. s: 平滑前数据散点的大小，缺省值：5。

                5. marker:平滑前数据散点的形状，缺省值：'o'。

        :param kwargs: 绘图所需关键字参数。
        """
        title = kwargs.pop("title", "Smooth")
        figsize = kwargs.pop("figsize", (15, 8))
        s = kwargs.pop("s", 5)
        marker = kwargs.pop("marker", "o")
        is_show = kwargs.pop("is_show", False)
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
        self.update_plot(ax1=ax1, ax2=ax2, ax3=ax3, s=s, marker=marker)
        # ----------------------------------------------------
        if is_show:
            plt.show()
        return fig, ax1, ax2, ax3

    # -------------------------------------------------------------
    @override
    def do_smooth(self):
        """
        执行拟合。

            调用此函数将会添加“fitting_result”和‘region_data_y_fitted’属性。

                1. fitting_result：表示拟合结果。

                2. region_data_y_fitted：表示拟合后的数据。

        :return: 拟合后的数据。
        """
        if self.is_parameter_changed or not hasattr(self, "fitting_result"):
            fitting_result = linear_fitting_sm(
                self.region_data_y, self.region_data_x, self.method
            )
            region_data_y_fitted = fitting_result.fittedvalues
            setattr(self, "fitting_result", fitting_result)
            setattr(self, "region_data_y_fitted", region_data_y_fitted)
            self.is_parameter_changed = False
        else:
            region_data_y_fitted = getattr(self, "region_data_y_fitted")
        return region_data_y_fitted

    @override
    def smooth(self, **kwargs):
        """
        执行带参数的拟合。

        :param kwargs: 可选关键字参数。
        :return: 拟合后的数据。
        """
        self.region_start = kwargs.pop("region_start", self.region_start)
        self.region_length = kwargs.pop("region_length", self.region_length)
        self.method = kwargs.pop("method", self.method)
        return self.do_smooth()

    @override
    def interactive_smooth(self, **kwargs):
        """
        交互式执行拟合。

        :param kwargs: 可选关键字参数。
        :return: 拟合后的数据。
        """
        # ------------------------------------------------------
        self.region_start = kwargs.pop("region_start", self.region_start)
        self.region_length = kwargs.pop("region_length", self.region_length)
        self.view_start = kwargs.pop("view_start", self.view_start)
        self.view_length = kwargs.pop("view_length", self.view_length)
        self.method = kwargs.pop("method", self.method)
        # ------------------------------------------------------
        default_region_start = self.region_start
        default_region_length = self.region_length
        default_view_start = self.view_start
        default_view_length = self.view_length
        default_method = self.method
        # ------------------------------------------------------
        # 解析关键字参数 ------------------------------------------
        title = kwargs.pop("title", "Linear Fitting")
        figsize = kwargs.pop("figsize", (15, 8))
        s = kwargs.pop("s", 5)
        marker = kwargs.pop("marker", "o")
        save_path = kwargs.pop("save_path", os.path.expanduser("~"))
        save_file_name = kwargs.pop(
            "save_file_name", "LinearFittingSm_" + unique_string() + ".csv"
        )
        # 创建图形 ----------------------------------------------------
        fig, ax1, ax2, ax3 = self.plot(
            title=title, figsize=figsize, s=s, marker=marker, is_show=False
        )
        plt.subplots_adjust(bottom=0.3)  # 底部留出空间
        # 窗口部件  ------------------------------------------------
        # 窗口部件的布局 --------------------------------------------
        view_start_slider_ax = plt.axes((0.1, 0.02, 0.62, 0.03))
        view_length_slider_ax = plt.axes((0.1, 0.07, 0.62, 0.03))
        region_start_slider_ax = plt.axes((0.1, 0.12, 0.62, 0.03))
        region_length_slider_ax = plt.axes((0.1, 0.17, 0.62, 0.03))

        view_start_text_box_ax = plt.axes((0.77, 0.02, 0.05, 0.03))
        view_length_text_box_ax = plt.axes((0.77, 0.07, 0.05, 0.03))
        region_start_text_box_ax = plt.axes((0.77, 0.12, 0.05, 0.03))
        region_length_text_box_ax = plt.axes((0.77, 0.17, 0.05, 0.03))

        mode_radio_ax = plt.axes((0.83, 0.02, 0.06, 0.18))

        save_button_ax = plt.axes((0.9, 0.02, 0.055, 0.07))
        reset_button_ax = plt.axes((0.9, 0.13, 0.055, 0.07))
        # 创建窗口部件 ----------------------------------------------
        view_start_slider = Slider(
            ax=view_start_slider_ax,
            label="View Start",
            valmin=0,
            valmax=self.data_len - 3,
            valinit=default_view_start,
            valstep=1,
        )

        view_length_slider = Slider(
            ax=view_length_slider_ax,
            label="View Length",
            valmin=0,
            valmax=self.data_len,
            valinit=default_view_length,
            valstep=1,
        )

        region_start_slider = Slider(
            ax=region_start_slider_ax,
            label="Region Start",
            valmin=0,
            valmax=self.data_len - 3,
            valinit=default_region_start,
            valstep=1,
        )

        region_length_slider = Slider(
            ax=region_length_slider_ax,
            label="Region Length",
            valmin=0,
            valmax=self.data_len,
            valinit=default_region_length,
            valstep=1,
        )

        view_start_text_box = TextBox(
            view_start_text_box_ax, label="", initial=str(default_view_start)
        )
        view_length_text_box = TextBox(
            view_length_text_box_ax, label="", initial=str(default_view_length)
        )
        region_start_text_box = TextBox(
            region_start_text_box_ax, label="", initial=str(default_region_start)
        )
        region_length_text_box = TextBox(
            region_length_text_box_ax, label="", initial=str(default_region_length)
        )

        mode_radio = RadioButtons(
            mode_radio_ax, self.methods, active=self.methods.index(default_method)
        )
        # 增加标签的字体大小
        for label in mode_radio.labels:
            label.set_fontsize(12)  # 设置字体大小为 12

        save_button = Button(save_button_ax, "Save")
        reset_button = Button(reset_button_ax, "Reset")

        # 窗口部件的事件 ----------------------------------------------
        def on_view_start_changed(val):
            self.view_start = int(val)
            view_start_text_box.set_val(str(self.view_start))
            self.update_plot(ax1=ax1, ax2=ax2, ax3=ax3, s=s, marker=marker)

        view_start_slider.on_changed(on_view_start_changed)

        def on_view_length_changed(val):
            self.view_length = int(val)
            view_length_text_box.set_val(str(self.view_length))
            self.update_plot(ax1=ax1, ax2=ax2, ax3=ax3, s=s, marker=marker)

        view_length_slider.on_changed(on_view_length_changed)

        # noinspection PyShadowingNames,DuplicatedCode
        def on_region_start_changed(val):
            self.region_start = int(val)
            region_start_text_box.set_val(str(self.region_start))
            self.update_plot(ax1=ax1, ax2=ax2, ax3=ax3, s=s, marker=marker)

        region_start_slider.on_changed(on_region_start_changed)

        def on_region_length_changed(val):
            self.region_length = int(val)
            region_length_text_box.set_val(str(self.region_length))
            self.update_plot(ax1=ax1, ax2=ax2, ax3=ax3, s=s, marker=marker)

        region_length_slider.on_changed(on_region_length_changed)

        def view_start_text_box_change(text):
            self.view_start = int(text)
            view_start_slider.set_val(self.view_start)
            self.update_plot(ax1=ax1, ax2=ax2, ax3=ax3, s=s, marker=marker)

        view_start_text_box.on_submit(view_start_text_box_change)

        def view_length_text_box_change(text):
            self.view_length = int(text)
            view_length_slider.set_val(self.view_length)
            self.update_plot(ax1=ax1, ax2=ax2, ax3=ax3, s=s, marker=marker)

        view_length_text_box.on_submit(view_length_text_box_change)

        def start_text_box_change(text):
            self.region_start = int(text)
            region_start_slider.set_val(self.region_start)
            self.update_plot(ax1=ax1, ax2=ax2, ax3=ax3, s=s, marker=marker)

        region_start_text_box.on_submit(start_text_box_change)

        def length_text_box_change(text):
            self.region_length = int(text)
            region_length_slider.set_val(self.region_length)
            self.update_plot(ax1=ax1, ax2=ax2, ax3=ax3, s=s, marker=marker)

        region_length_text_box.on_submit(length_text_box_change)

        def mode_change_option(val):
            self.method = val
            self.update_plot(ax1=ax1, ax2=ax2, ax3=ax3, s=s, marker=marker)

        mode_radio.on_clicked(mode_change_option)

        # noinspection PyUnusedLocal
        def on_save_button_change(val):
            nonlocal save_path, save_file_name
            if not os.path.exists(save_path):
                os.makedirs(save_path, exist_ok=True)
            data_outfile = os.path.abspath(os.path.join(save_path, save_file_name))
            assert data_outfile is not None
            # noinspection PyUnresolvedReferences
            data = pd.DataFrame(
                {
                    "region_data_x": self.region_data_x,
                    "region_data_y": self.region_data_y,
                    "region_data_y_fitted": self.region_data_y_fitted,
                }
            )
            data.to_csv(data_outfile, index=False)

        save_button.on_clicked(on_save_button_change)

        # noinspection PyUnusedLocal
        def on_reset_button_change(val):
            # ----------------------------------------------------------
            self.view_start = default_view_start
            self.view_length = default_view_length
            self.region_start = default_region_start
            self.region_length = default_region_length
            self.method = default_method
            # ----------------------------------------------------------
            view_start_slider.set_val(self.view_start)
            view_length_slider.set_val(self.view_length)
            region_start_slider.set_val(self.region_start)
            region_length_slider.set_val(self.region_length)
            # ----------------------------------------------------------
            view_start_text_box.set_val(str(self.view_start))
            view_length_text_box.set_val(str(self.view_length))
            region_start_text_box.set_val(str(self.region_start))
            region_length_text_box.set_val(str(self.region_length))
            # ----------------------------------------------------------
            mode_radio.set_active(self.methods.index(default_method))
            # ----------------------------------------------------------
            self.update_plot(ax1=ax1, ax2=ax2, ax3=ax3, s=s, marker=marker)

        reset_button.on_clicked(on_reset_button_change)
        # ---------------------------------------------------------------
        plt.show()
        # noinspection PyUnresolvedReferences
        return self.region_data_y_fitted, self.region_data_y, self.region_data_x

    @override
    def residuals_analysis(self, **kwargs):
        """
        执行拟合后的残差分析。

        :param kwargs: 可选关键字参数。
        :return: 拟合统计结果。
        """
        return FittingStatistics(
            self.region_data_y, self.residuals, nvars_fitted=2, x=self.region_data_x
        )


# =======================================================================
