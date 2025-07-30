#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        data_2d_region_sm_linear_fitter.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“表征`二维数据区域线性拟合器`的类”。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2024/10/22     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import os
from typing import override, Optional

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.widgets import (RadioButtons, Slider, Button, TextBox)

from ..commons import (NumberSequence, unique_string)
from ..smoothers import Data2dRegionSmoother
from ..statistics import FittingStatistics
from .sm_linear_fittings import linear_fitting_sm

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining a class that represents `the fitter for 
the region of two-dimensional data`.
"""

__all__ = [
    'Data2dRegionSmLinearFitter',
]


# 定义 ==============================================================
class Data2dRegionSmLinearFitter(Data2dRegionSmoother):
    """
    类`Data2dRegionViewSmLinearFitter`表征“二维数据区域线性拟合器”。
    """

    def __init__(self, y: NumberSequence,
                 x: NumberSequence,
                 region_start: Optional[int] = 0,
                 region_length: Optional[int] = None,
                 method: Optional[str] = 'ols'):
        """
        类`Data2dRegionViewSmLinearFitter`的初始化方法。

            可选关键字参数：

                1. region_start：要拟合数据在原始数据上的起始索引。

                2. region_length：要拟合数据的长度。

                3. method：拟合方法，默认值：'ols'。

        :param y: 因变量。
        :param x: 自变量。
        :param method: 拟合方法，默认值：'ols'。
        """
        # 初始化参数 -----------------------------------------------
        self.__methods = ('ols', 'rlm')
        self.__method = method.strip().lower()
        if self.__method not in self.__methods:
            raise ValueError(f"method must be one of {self.__methods}")
        super(Data2dRegionSmLinearFitter, self).__init__(
            y, x, region_start=region_start, region_length=region_length)
        # 初始化完成 -----------------------------------------------

    @property
    def method(self) -> str:
        """
        返回拟合方法。

        :return: 拟合方法。
        """
        return self.__method

    @method.setter
    def method(self, method: str):
        """
        设置拟合方法。

        :param method: 拟合方法。
        """
        if self.method != method.strip().lower():
            self.__method = method.strip().lower()
            self.is_parameter_changed = True

    @property
    def methods(self):
        """
        获取所有支持的拟合方法。

        :return: 所有支持的拟合方法。
        """
        return self.__methods

    # -------------------------------------------------------------
    @override
    def do_smooth(self):
        """
        执行拟合。

            调用此函数将会添加“fitting_result”和‘region_data_y_fitted’属性。

                1. fitting_result：表示拟合结果。

                2. region_data_y_fitted：表示拟合后的数据。

        :return: 拟合后的数据（region_data_y_fitted）。
        """
        if self.is_parameter_changed or not hasattr(self, 'fitting_result'):
            fitting_result = linear_fitting_sm(self.region_data_y,
                                               self.region_data_x,
                                               method=self.method)
            region_data_y_fitted = fitting_result.fittedvalues
            setattr(self, 'fitting_result', fitting_result)
            setattr(self, 'region_data_y_fitted', region_data_y_fitted)
            self.is_parameter_changed = False
        else:
            region_data_y_fitted = getattr(self, 'region_data_y_fitted')
        return region_data_y_fitted

    @override
    def smooth(self, **kwargs):
        """
        执行拟合。

        :param kwargs: 可选关键字参数。
        :return: 拟合后的数据（region_data_y_fitted）。
        """
        self.region_start = kwargs.pop('region_start', self.region_start)
        self.region_length = kwargs.pop('region_length', self.region_length)
        self.method = kwargs.pop('method', self.method)
        return self.do_smooth()

    @override
    def interactive_smooth(self, **kwargs):
        """
        交互式执行拟合。

        :param kwargs: 可选关键字参数。
        :return: 拟合后的数据（region_data_y_fitted）。
        """
        self.region_start = kwargs.pop('region_start', self.region_start)
        self.region_length = kwargs.pop('region_length', self.region_length)
        self.method = kwargs.pop('method', self.method)
        # ---------------------------------------------
        default_start = self.region_start
        default_length = self.region_length
        default_method = self.method
        # ---------------------------------------------
        # 解析关键字参数 ------------------------------------------
        title = kwargs.pop('title', "Linear Fitting")
        figsize = kwargs.pop('figsize', (12, 8))
        s = kwargs.pop('s', 5)
        marker = kwargs.pop('marker', 'o')
        save_path = kwargs.pop('save_path', os.path.expanduser('~'))
        save_file_name = kwargs.pop('save_file_name',
                                    "LinearFittingSm_" + unique_string() + ".csv")
        # 创建图形 ----------------------------------------------------
        fig, ax1, ax2 = self.plot(title=title, figsize=figsize,
                                  s=s, marker=marker, is_show=False)
        plt.subplots_adjust(bottom=0.2)  # 底部留出空间
        # 窗口部件  ------------------------------------------------
        # 窗口部件的布局 --------------------------------------------
        mode_radio_ax = plt.axes((0.83, 0.02, 0.06, 0.09))
        start_slider_ax = plt.axes((0.1, 0.08, 0.62, 0.03))
        length_slider_ax = plt.axes((0.1, 0.02, 0.62, 0.03))
        save_button_ax = plt.axes((0.9, 0.02, 0.055, 0.03))
        reset_button_ax = plt.axes((0.9, 0.08, 0.055, 0.03))
        start_text_box_ax = plt.axes((0.77, 0.08, 0.05, 0.03))
        length_text_box_ax = plt.axes((0.77, 0.02, 0.05, 0.03))
        # 创建窗口部件 ----------------------------------------------
        mode_radio = RadioButtons(mode_radio_ax, self.methods,
                                  active=self.methods.index(default_method))
        # 增加标签的字体大小
        for label in mode_radio.labels:
            label.set_fontsize(12)  # 设置字体大小为 12

        start_slider = Slider(
            ax=start_slider_ax,
            label='Start',
            valmin=0,
            valmax=self.data_len - 3,
            valinit=default_start,
            valstep=1
        )

        length_slider = Slider(
            ax=length_slider_ax,
            label='Length',
            valmin=0,
            valmax=self.data_len,
            valinit=default_length,
            valstep=1
        )

        save_button = Button(save_button_ax, 'Save')
        reset_button = Button(reset_button_ax, 'Reset')
        start_text_box = TextBox(start_text_box_ax, label='', initial=str(default_start))
        length_text_box = TextBox(length_text_box_ax, label='', initial=str(default_length))

        def mode_change_option(val):
            self.method = val
            self.update_plot(ax1, ax2, s=s, marker=marker)

        # 设置选项改变时调用的函数
        mode_radio.on_clicked(mode_change_option)

        # 滑块数值变化事件处理函数
        # noinspection PyShadowingNames,DuplicatedCode
        def on_start_changed(val):
            self.region_start = int(val)
            start_text_box.set_val(str(self.region_start))
            self.update_plot(ax1, ax2, s=s, marker=marker)

        start_slider.on_changed(on_start_changed)

        def on_length_changed(val):
            self.region_length = int(val)
            length_text_box.set_val(str(self.region_length))
            self.update_plot(ax1, ax2, s=s, marker=marker)

        length_slider.on_changed(on_length_changed)

        # noinspection PyUnusedLocal
        def on_save_button_change(val):
            nonlocal save_path, save_file_name
            if not os.path.exists(save_path):
                os.makedirs(save_path, exist_ok=True)
            data_outfile = os.path.abspath(os.path.join(save_path, save_file_name))
            assert data_outfile is not None
            # noinspection PyUnresolvedReferences
            data = pd.DataFrame({'region_data_x': self.region_data_x,
                                 'region_data_y': self.region_data_y,
                                 'region_data_y_fitted': self.region_data_y_fitted})
            data.to_csv(data_outfile, index=False)

        save_button.on_clicked(on_save_button_change)

        # noinspection PyUnusedLocal
        def on_reset_button_change(val):
            nonlocal default_start, default_length, default_method
            # ----------------------------------------------------------
            self.region_start = default_start
            self.region_length = default_length
            self.method = default_method
            # ----------------------------------------------------------
            start_slider.set_val(self.region_start)
            length_slider.set_val(self.region_length)
            # ----------------------------------------------------------
            start_text_box.set_val(str(self.region_start))
            length_text_box.set_val(str(self.region_length))
            # ----------------------------------------------------------
            mode_radio.set_active(self.methods.index(default_method))
            # ----------------------------------------------------------
            self.update_plot(ax1, ax2, s=s, marker=marker)

        reset_button.on_clicked(on_reset_button_change)

        def start_text_box_change(text):
            self.region_start = int(text)
            start_slider.set_val(self.region_start)
            self.update_plot(ax1, ax2, s=s, marker=marker)

        start_text_box.on_submit(start_text_box_change)

        def length_text_box_change(text):
            self.region_length = int(text)
            length_slider.set_val(self.region_length)
            self.update_plot(ax1, ax2, s=s, marker=marker)

        length_text_box.on_submit(length_text_box_change)
        # ---------------------------------------------------------------
        plt.show()
        # noinspection PyUnresolvedReferences
        return self.region_data_y_fitted, self.region_data_y, self.region_data_x

    # -------------------------------------------------------------
    @override
    def residuals_analysis(self, **kwargs):
        """
        执行拟合残差分析。

        :param kwargs: 可选关键字参数。
        :return: 分析结果，...。
        """
        filter_residuals = self.residuals
        return FittingStatistics(self.region_data_y, filter_residuals,
                                 nvars_fitted=2,
                                 x=self.region_data_x)

# ==================================================================
