#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        data_2d_region_savgol_filters.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“表征`二维数据区域Savgol滤波器`的类”。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2024/10/24     finish
# ------------------------------------------------------------------
# 导包 ==============================================================
import os
from typing import Optional, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons, Button, Slider, TextBox
from scipy.signal import savgol_filter

from ..commons import NumberSequence, unique_string
from ..smoothers import Data2dRegionSmoother

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining a class that represents `the savgol filter for 
the region of two-dimensional data`.
"""

__all__ = [
    "Data2dRegionSavgolFilter",
]


# 定义 ==============================================================
class Data2dRegionSavgolFilter(Data2dRegionSmoother):
    """
    类`Data2dRegionSavgolFilter`表征“二维数据区域Savgol滤波器”。
    """

    def __init__(
        self,
        data_y: NumberSequence,
        data_x: Optional[NumberSequence] = None,
        region_start: int = 0,
        region_length: Optional[int] = None,
        *,
        window_length: int = 11,
        polyorder: int = 2,
        deriv: int = 0,
        delta: float = 1.0,
        mode: str = "interp",
        cval: float = 0.0,
    ):
        """
        类`Data2dRegionSavgolFilter`的初始化方法。

        :param data_y: 因变量（数据y）。
        :param data_x: 自变量（数据x,可选）。
        :param region_start: “数据区域”的起始索引位置，默认值为0。
        :param region_length: “数据区域”的长度，默认值为`data_len - region_start`。
        :param window_length: int，`scipy.signal.savgol_filter`的参数window_length，缺省值：11。
               滤波窗口的长度，即在每个点上进行多项式拟合时所使用的邻近点的数量。这个值必须是一个正奇数整数。
        :param polyorder: int，`scipy.signal.savgol_filter`的参数polyorder，缺省值：2。
                用于拟合数据的多项式的阶数。这个值必须小于 window_length。
        :param deriv:int，`scipy.signal.savgol_filter`的参数deriv，缺省值：0。
                导数的阶数，默认为 0，表示只做平滑处理而不计算导数。
        :param delta: float，`scipy.signal.savgol_filter`的参数delta，缺省值：1.0。
                采样距离，默认为 1.0。只有当 deriv 不为 0 时才有意义。
        :param mode: str，`scipy.signal.savgol_filter`的参数mode，缺省值：'interp'。
                边界模式，可以是 'mirror', 'constant', 'nearest', 'wrap' 或 'interp'。
                默认是 'interp'，使用插值填充边界。
        :param cval: float，`scipy.signal.savgol_filter`的参数cva，缺省值：0.0。
                如果 mode 是 'constant'，则该值用来填充边界。默认是 0.0。
        """
        super(Data2dRegionSavgolFilter, self).__init__(
            data_y, data_x, region_start, region_length
        )
        self.__window_length = window_length
        self.__polyorder = polyorder
        self.__deriv = deriv
        self.__delta = delta
        self.__mode = mode
        self.__cval = cval
        # -----------------------------------------------------------

    @property
    def window_length(self) -> int:
        """
        返回窗口长度（`scipy.signal.savgol_filter`的参数window_length，int类型）。

        :return: 窗口长度。
        """
        return self.__window_length

    @window_length.setter
    def window_length(self, window_length: int):
        """
        设置窗口长度（`scipy.signal.savgol_filter`的参数window_length，int类型）。

            注意：最好只在此类或此类的子类中调用。

        :param window_length: 窗口长度。
        """
        if self.__window_length != window_length:
            self.__window_length = window_length
            self.is_parameter_changed = True

    @property
    def polyorder(self) -> int:
        """
        返回多项式阶数（`scipy.signal.savgol_filter`的参数polyorder，int类型）。

        :return: 多项式阶数。
        """
        return self.__polyorder

    @polyorder.setter
    def polyorder(self, polyorder: int):
        """
        设置多项式阶数（`scipy.signal.savgol_filter`的参数polyorder，int类型）。

            注意：最好只在此类或此类的子类中调用。

        :param polyorder:多项式阶数。
        """
        if self.__polyorder != polyorder:
            self.__polyorder = polyorder
            self.is_parameter_changed = True

    @property
    def deriv(self) -> int:
        """
        返回导数阶数（`scipy.signal.savgol_filter`的参数deriv，int类型）。

        :return:导数阶数。
        """
        return self.__deriv

    @deriv.setter
    def deriv(self, deriv: int):
        """
        设置导数阶数（`scipy.signal.savgol_filter`的参数deriv，int类型）。

            注意：最好只在此类或此类的子类中调用。

        :param deriv:导数阶数。
        """
        if self.__deriv != deriv:
            self.__deriv = deriv
            self.is_parameter_changed = True

    @property
    def delta(self) -> float:
        """
        返回差分步长（delta：`scipy.signal.savgol_filter`的参数delta，float类型）。

        :return: 差分步长。
        """
        return self.__delta

    @delta.setter
    def delta(self, delta: float):
        """
        设置差分步长（delta：`scipy.signal.savgol_filter`的参数delta，float类型）。

            注意：最好只在此类或此类的子类中调用。

        :param delta: 差分步长。
        """
        if self.__delta != delta:
            self.__delta = delta
            self.is_parameter_changed = True

    @property
    def mode(self) -> str:
        """
        返回边界扩展模式（`scipy.signal.savgol_filter`的参数mode，str类型）。

        :return: 边界扩展模式。
        """
        return self.__mode

    @mode.setter
    def mode(self, mode: str):
        """
        设置边界扩展模式（`scipy.signal.savgol_filter`的参数mode，str类型）。

            注意：最好只在此类或此类的子类中调用。

        :param mode: 边界扩展模式。
        """
        if self.__mode != mode:
            self.__mode = mode
            self.is_parameter_changed = True

    @property
    def modes(self) -> Tuple[str, str, str, str, str]:
        """
        返回所有允许的边界扩展模式。

        :return: 所有允许的边界扩展模式。
        """
        return "interp", "mirror", "constant", "wrap", "nearest"

    @property
    def cval(self) -> float:
        """
        返回边界扩展常数值（`scipy.signal.savgol_filter`的参数cva，float类型）。

            注意：

                1.最好只在此类或此类的子类中调用。

                2. 此值只有`self.mode=constant`时才有效。

        :return: 边界扩展常数值。
        """
        return self.__cval

    @cval.setter
    def cval(self, cval: float):
        """
        设置边界扩展常数值（`scipy.signal.savgol_filter`的参数cva，float类型）。

            注意：此值只有`self.mode=constant`时才有效。

        :param cval: 边界扩展常数值。
        """
        if self.__cval != cval:
            self.__cval = cval
            self.is_parameter_changed = True

    # -------------------------------------------------------------
    def do_smooth(self):
        """
        执行平滑操作。

        :return: 平滑后的数据。
        """
        if self.is_parameter_changed or not hasattr(self, "region_data_y_filtered"):
            region_data_y_filtered = savgol_filter(
                self.region_data_y,
                window_length=self.window_length,
                polyorder=self.polyorder,
                deriv=self.deriv,
                delta=self.delta,
                mode=self.mode,
                cval=self.cval,
            )
            setattr(self, "region_data_y_filtered", region_data_y_filtered)
            self.is_parameter_changed = False
        else:
            region_data_y_filtered = getattr(self, "region_data_y_filtered")
        return region_data_y_filtered

    def smooth(self, **kwargs):
        """
        执行带参数的平滑。

        :param kwargs: 可选关键字参数。
        :return: 平滑后的数据。
        """
        # 初始化参数 -----------------------------------------
        self.region_start: int = kwargs.pop("region_start", self.region_start)
        self.region_length: int = kwargs.pop("region_length", self.region_length)
        self.window_length: int = kwargs.pop("window_length", self.window_length)
        self.polyorder: int = kwargs.pop("polyorder", self.polyorder)
        self.deriv: int = kwargs.pop("deriv", self.deriv)
        self.delta: float = kwargs.pop("delta", self.delta)
        self.mode: str = kwargs.pop("mode", self.mode)
        self.cval: float = kwargs.pop("cval", self.cval)
        # 执行平滑处理 --------------------------------------
        return self.do_smooth()

    def simple_interactive_smooth(self, **kwargs):
        """
        简化的交互式平滑。

            可选关键字参数：

                1. region_start：要处理数据在原始数据上的起始索引，缺省值：`self.region_start`。

                2. region_length：要处理数据的长度，缺省值：`self.region_length`。

                3. window_length：`scipy.signal.savgol_filter`的参数window_length，缺省值：`self.window_length`。

                4. polyorder：`scipy.signal.savgol_filter`的参数polyorder，缺省值：`self.polyorder`。

                5. deriv：`scipy.signal.savgol_filter`的参数deriv，缺省值：`self.deriv`。

                6. delta：`scipy.signal.savgol_filter`的参数delta，缺省值：`self.delta`。

                7. mode：`scipy.signal.savgol_filter`的参数mode，缺省值：`self.mode`。

                8. cval：`scipy.signal.savgol_filter`的参数cva，缺省值：`self.cval`。

                # -----------------------------------------------------------------

                9. title: 图形的标题，缺省值：'Savgol Filter'。

                10. figsize: 图形的尺寸，缺省值：(12,8)，即宽度（width）为：12，高度（height）为8。

                11. s: 滤波前数据散点的大小，缺省值：5。

                12. marker:滤波前数据散点的形状，缺省值：'o'。

                # -----------------------------------------------------------------

                13. save_path: 保存文件的路径，缺省值：`os.path.expanduser("~")`。

                14. save_file_name：保存文件的文件名，缺省值：`"SavgolFilter_" + unique_string() + ".csv"`。

        :param kwargs: 所需的关键字参数。
        :return: 平滑后的数据。
        """
        # 参数准备 -----------------------------------------
        self.region_start: int = kwargs.pop("start", self.region_start)
        self.region_length: int = kwargs.pop("length", self.region_length)
        self.window_length: int = kwargs.pop("window_length", self.window_length)
        self.polyorder: int = kwargs.pop("polyorder", self.polyorder)
        self.deriv: int = kwargs.pop("deriv", self.deriv)
        self.delta: float = kwargs.pop("delta", self.delta)
        self.mode: str = kwargs.pop("mode", self.mode)
        self.cval: float = kwargs.pop("cval", self.cval)
        # ------------------------------------------------------------
        # 定义并保存参数的缺省值 -----------------------------------------
        default_region_start: int = self.region_start
        default_region_length: int = self.region_length
        default_window_length: int = self.window_length
        default_polyorder: int = self.polyorder
        default_deriv: int = self.deriv
        default_delta: float = self.delta
        default_mode: str = self.mode
        default_cval: float = self.cval
        # 解析关键字参数 ------------------------------------------
        title = kwargs.pop("title", "Savgol Filter")
        figsize = kwargs.pop("figsize", (12, 8))
        s = kwargs.pop("s", 5)
        marker = kwargs.pop("marker", "o")
        save_path = kwargs.pop("save_path", os.path.expanduser("~"))
        save_file_name = kwargs.pop(
            "save_file", "SavgolFilter_" + unique_string() + ".csv"
        )
        # 创建图形 ----------------------------------------------------
        fig, ax1, ax2 = self.plot(
            title=title, figsize=figsize, s=s, marker=marker, is_show=False
        )
        plt.subplots_adjust(bottom=0.3)  # 底部留出空间
        # 创建窗口部件  ------------------------------------------------
        # 窗口部件的布局  ----------------------------------------------
        mode_ax = plt.axes((0.795, 0.02, 0.1, 0.21))

        save_button_ax = plt.axes((0.9, 0.02, 0.055, 0.095))
        reset_button_ax = plt.axes((0.9, 0.135, 0.055, 0.095))

        start_slider_ax = plt.axes((0.15, 0.02, 0.53, 0.03))
        length_slider_ax = plt.axes((0.15, 0.06, 0.53, 0.03))
        window_length_slider_ax = plt.axes((0.15, 0.10, 0.53, 0.03))
        polyorder_slider_ax = plt.axes((0.15, 0.14, 0.53, 0.03))

        start_text_box_ax = plt.axes((0.74, 0.02, 0.05, 0.03))
        length_text_box_ax = plt.axes((0.74, 0.06, 0.05, 0.03))
        window_length_text_box_ax = plt.axes((0.74, 0.10, 0.05, 0.03))
        polyorder_text_box_ax = plt.axes((0.74, 0.14, 0.05, 0.03))

        deriv_text_box_ax = plt.axes((0.15, 0.19, 0.12, 0.03))
        delta_text_box_ax = plt.axes((0.35, 0.19, 0.12, 0.03))
        cval_text_box_ax = plt.axes((0.55, 0.19, 0.12, 0.03))

        # 创建单选按钮部件 -----------------------------------------------
        mode_radio = RadioButtons(
            mode_ax,
            self.modes,
            active=self.modes.index(default_mode),
            activecolor="red",
        )
        # 增加标签的字体大小
        for label in mode_radio.labels:
            label.set_fontsize(12)  # 设置字体大小为 12
        # 创建按钮部件 -------------------------------------------------
        save_button = Button(save_button_ax, "Save")
        reset_button = Button(reset_button_ax, "Reset")
        # 创建滑块部件 --------------------------------------------------

        start_slider = Slider(
            ax=start_slider_ax,
            label="Region Start",
            valmin=0,
            valmax=self.data_len - 3,
            valinit=default_region_start,
            valstep=1,
        )

        length_slider = Slider(
            ax=length_slider_ax,
            label="Region Length",
            valmin=0,
            valmax=self.data_len,
            valinit=default_region_length,
            valstep=1,
        )

        window_length_slider = Slider(
            ax=window_length_slider_ax,
            label="Window Length",
            valmin=3,
            valmax=self.data_len // 2,
            valinit=default_window_length,
            valstep=2,
        )

        polyorder_slider = Slider(
            ax=polyorder_slider_ax,
            label="Polyorder",
            valmin=1,
            valmax=9,
            valinit=default_polyorder,
            valstep=1,
        )

        start_text_box = TextBox(
            start_text_box_ax, label="", initial=str(default_region_start)
        )
        length_text_box = TextBox(
            length_text_box_ax, label="", initial=str(default_region_length)
        )
        window_length_text_box = TextBox(
            window_length_text_box_ax, label="", initial=str(default_window_length)
        )
        polyorder_text_box = TextBox(
            polyorder_text_box_ax, label="", initial=str(default_polyorder)
        )
        deriv_text_box = TextBox(
            deriv_text_box_ax, label="deriv: ", initial=str(default_deriv)
        )
        delta_text_box = TextBox(
            delta_text_box_ax, label="delta: ", initial=f"{default_delta:.3g}"
        )
        cval_text_box = TextBox(
            cval_text_box_ax, label="cval: ", initial=f"{default_cval:.3g}"
        )

        # 事件绑定 -----------------------------------------------------
        # noinspection PyShadowingNames,DuplicatedCode
        def mode_change_option(label):
            nonlocal ax1, ax2, s, marker
            self.mode = label
            self.update_plot(ax1, ax2, s=s, marker=marker)

        # 设置选项改变时调用的函数
        mode_radio.on_clicked(mode_change_option)

        # noinspection PyUnusedLocal,PyUnresolvedReferences
        def on_save_button_change(val):
            nonlocal save_path, save_file_name
            if not os.path.exists(save_path):
                os.makedirs(save_path, exist_ok=True)
            data_outfile = os.path.abspath(os.path.join(save_path, save_file_name))
            assert data_outfile is not None
            data = pd.DataFrame(
                {
                    "region_data_x": self.region_data_x,
                    "region_data_y": self.region_data_y,
                    "region_data_y_filtered": self.region_data_y_filtered,
                }
            )
            data.to_csv(data_outfile, index=False)

        save_button.on_clicked(on_save_button_change)

        # noinspection PyUnusedLocal
        def on_reset_button_change(val):
            nonlocal default_region_start
            nonlocal default_region_length
            nonlocal default_window_length
            nonlocal default_polyorder
            nonlocal default_deriv
            nonlocal default_delta
            nonlocal default_cval
            nonlocal default_mode
            nonlocal ax1, ax2, s, marker
            # ----------------------------------------------------------
            self.region_start = default_region_start
            self.region_length = default_region_length
            self.window_length = default_window_length
            self.polyorder = default_polyorder
            self.deriv = default_deriv
            self.delta = default_delta
            self.cval = default_cval
            self.mode = default_mode
            # ----------------------------------------------------------
            start_slider.set_val(self.region_start)
            length_slider.set_val(self.region_length)
            window_length_slider.set_val(self.window_length)
            polyorder_slider.set_val(self.polyorder)
            # ----------------------------------------------------------
            start_text_box.set_val(str(self.region_start))
            length_text_box.set_val(str(self.region_length))
            window_length_text_box.set_val(str(self.window_length))
            polyorder_text_box.set_val(str(self.polyorder))
            deriv_text_box.set_val(str(self.deriv))
            delta_text_box.set_val(f"{self.delta:.3g}")
            cval_text_box.set_val(f"{self.cval:.3g}")
            # ----------------------------------------------------------
            mode_radio.set_active(self.modes.index(self.mode))
            # ----------------------------------------------------------
            self.update_plot(ax1, ax2, s=s, marker=marker)

        reset_button.on_clicked(on_reset_button_change)

        def on_start_changed(val):
            nonlocal ax1, ax2, s, marker
            self.region_start = int(val)
            start_text_box.set_val(str(self.region_start))
            self.update_plot(ax1, ax2, s=s, marker=marker)

        start_slider.on_changed(on_start_changed)

        def on_length_changed(val):
            nonlocal ax1, ax2, s, marker
            self.region_length = int(val)
            length_text_box.set_val(str(self.region_length))
            self.update_plot(ax1, ax2, s=s, marker=marker)

        length_slider.on_changed(on_length_changed)

        def on_window_length_changed(val):
            nonlocal ax1, ax2, s, marker
            self.window_length = int(val)
            window_length_text_box.set_val(str(self.window_length))
            self.update_plot(ax1, ax2, s=s, marker=marker)

        window_length_slider.on_changed(on_window_length_changed)

        def on_polyorder_changed(val):
            nonlocal ax1, ax2, s, marker
            self.polyorder = int(val)
            polyorder_text_box.set_val(str(self.polyorder))
            self.update_plot(ax1, ax2, s=s, marker=marker)

        polyorder_slider.on_changed(on_polyorder_changed)

        # -------------------------------------------------------------
        def start_text_box_change(text):
            nonlocal ax1, ax2, s, marker
            self.region_start = int(text)
            start_slider.set_val(self.region_start)
            self.update_plot(ax1, ax2, s=s, marker=marker)

        start_text_box.on_submit(start_text_box_change)

        def length_text_box_change(text):
            nonlocal ax1, ax2, s, marker
            self.region_length = int(text)
            length_slider.set_val(self.region_length)
            self.update_plot(ax1, ax2, s=s, marker=marker)

        length_text_box.on_submit(length_text_box_change)

        def window_length_text_box_change(text):
            nonlocal ax1, ax2, s, marker
            self.window_length = int(text)
            window_length_slider.set_val(self.window_length)
            self.update_plot(ax1, ax2, s=s, marker=marker)

        window_length_text_box.on_submit(window_length_text_box_change)

        def polyorder_text_box_change(text):
            nonlocal ax1, ax2, s, marker
            self.polyorder = int(text)
            polyorder_slider.set_val(self.polyorder)
            self.update_plot(ax1, ax2, s=s, marker=marker)

        polyorder_text_box.on_submit(polyorder_text_box_change)

        def deriv_text_box_change(text):
            nonlocal ax1, ax2, s, marker
            self.deriv = int(text)
            self.update_plot(ax1, ax2, s=s, marker=marker)

        deriv_text_box.on_submit(deriv_text_box_change)

        def delta_text_box_change(text):
            nonlocal ax1, ax2, s, marker
            self.delta = float(text)
            self.update_plot(ax1, ax2, s=s, marker=marker)

        delta_text_box.on_submit(delta_text_box_change)

        def cval_text_box_change(text):
            nonlocal ax1, ax2, s, marker
            self.cval = float(text)
            self.update_plot(ax1, ax2, s=s, marker=marker)

        cval_text_box.on_submit(cval_text_box_change)
        # ---------------------------------------------------------------
        plt.show()
        # noinspection PyUnresolvedReferences
        return self.region_data_y_filtered

    def all_interactive_smooth(self, **kwargs):
        """
        全参数交互式平滑。

            可选关键字参数如下：

                1. region_start：要处理数据在原始数据上的起始索引，缺省值：`self.region_start`。

                2. region_length：要处理数据的长度，缺省值：`self.region_length`。

                3. window_length：`scipy.signal.savgol_filter`的参数window_length，缺省值：`self.window_length`。

                4. polyorder：`scipy.signal.savgol_filter`的参数polyorder，缺省值：`self.polyorder`。

                5. deriv：`scipy.signal.savgol_filter`的参数deriv，缺省值：`self.deriv`。

                6. delta：`scipy.signal.savgol_filter`的参数delta，缺省值：`self.delta`。

                7. mode：`scipy.signal.savgol_filter`的参数mode，缺省值：`self.mode`。

                8. cval：`scipy.signal.savgol_filter`的参数cva，缺省值：`self.cval`。

                # -----------------------------------------------------------------

                9. title: 图形的标题，缺省值：'Savgol Filter'。

                10. figsize: 图形的尺寸，缺省值：(12,8)，即宽度（width）为：12，高度（height）为8。

                11. s: 滤波前数据散点的大小，缺省值：5。

                12. marker:滤波前数据散点的形状，缺省值：'o'。

                # -----------------------------------------------------------------

                13. save_path: 保存文件的路径，缺省值：`os.path.expanduser("~")`。

                14. save_file_name：保存文件的文件名，缺省值：`"SavgolFilter_" + unique_string() + ".csv"`。

        :param kwargs: 所需的关键字参数。
        :return: 平滑后的数据。
        """
        # 参数准备 -----------------------------------------
        self.region_start: int = kwargs.pop("region_start", self.region_start)
        self.region_length: int = kwargs.pop("region_length", self.region_length)
        self.window_length: int = kwargs.pop("window_length", self.window_length)
        self.polyorder: int = kwargs.pop("polyorder", self.polyorder)
        self.deriv: int = kwargs.pop("deriv", self.deriv)
        self.delta: float = kwargs.pop("delta", self.delta)
        self.mode: str = kwargs.pop("mode", self.mode)
        self.cval: float = kwargs.pop("cval", self.cval)
        # ------------------------------------------------------------
        # 定义并保存参数的缺省值 -----------------------------------------
        default_region_start: int = self.region_start
        default_region_length: int = self.region_length
        default_window_length: int = self.window_length
        default_polyorder: int = self.polyorder
        default_deriv: int = self.deriv
        default_delta: float = self.delta
        default_mode: str = self.mode
        default_cval: float = self.cval
        # 解析关键字参数 ------------------------------------------
        title = kwargs.pop("title", "Savgol Filter")
        figsize = kwargs.pop("figsize", (12, 8))
        s = kwargs.pop("s", 5)
        marker = kwargs.pop("marker", "o")
        save_path = kwargs.pop("save_path", os.path.expanduser("~"))
        save_file_name = kwargs.pop(
            "save_file_name", "SavgolFilter_" + unique_string() + ".csv"
        )
        # 创建图形 ----------------------------------------------------
        fig, ax1, ax2 = self.plot(
            title=title, figsize=figsize, s=s, marker=marker, is_show=False
        )
        plt.subplots_adjust(bottom=0.3)  # 底部留出空间
        # 创建窗口部件  ------------------------------------------------
        # 窗口部件的布局  ----------------------------------------------
        mode_ax = plt.axes((0.795, 0.02, 0.1, 0.21))
        mode_radio = RadioButtons(
            mode_ax,
            self.modes,
            active=self.modes.index(default_mode),
            activecolor="red",
        )
        # 增加标签的字体大小
        for label in mode_radio.labels:
            label.set_fontsize(12)  # 设置字体大小为 12
        # -------------------------------------------------------------
        save_button_ax = plt.axes((0.9, 0.02, 0.055, 0.095))
        save_button = Button(save_button_ax, "Save")

        reset_button_ax = plt.axes((0.9, 0.135, 0.055, 0.095))
        reset_button = Button(reset_button_ax, "Reset")
        # ------------------------------------------------------------
        start_slider_ax = plt.axes((0.15, 0.02, 0.53, 0.03))
        length_slider_ax = plt.axes((0.15, 0.05, 0.53, 0.03))
        window_length_slider_ax = plt.axes((0.15, 0.08, 0.53, 0.03))
        polyorder_slider_ax = plt.axes((0.15, 0.11, 0.53, 0.03))
        deriv_slider_ax = plt.axes((0.15, 0.14, 0.53, 0.03))
        delta_slider_ax = plt.axes((0.15, 0.17, 0.53, 0.03))
        cval_slider_ax = plt.axes((0.15, 0.20, 0.53, 0.03))

        start_text_box_ax = plt.axes((0.74, 0.02, 0.05, 0.03))
        length_text_box_ax = plt.axes((0.74, 0.05, 0.05, 0.03))
        window_length_text_box_ax = plt.axes((0.74, 0.08, 0.05, 0.03))
        polyorder_text_box_ax = plt.axes((0.74, 0.11, 0.05, 0.03))
        deriv_text_box_ax = plt.axes((0.74, 0.14, 0.05, 0.03))
        delta_text_box_ax = plt.axes((0.74, 0.17, 0.05, 0.03))
        cval_text_box_ax = plt.axes((0.74, 0.20, 0.05, 0.03))

        start_text_box = TextBox(
            start_text_box_ax, label="", initial=str(default_region_start)
        )
        length_text_box = TextBox(
            length_text_box_ax, label="", initial=str(default_region_length)
        )
        window_length_text_box = TextBox(
            window_length_text_box_ax, label="", initial=str(default_window_length)
        )
        polyorder_text_box = TextBox(
            polyorder_text_box_ax, label="", initial=str(default_polyorder)
        )
        deriv_text_box = TextBox(
            deriv_text_box_ax, label="", initial=str(default_deriv)
        )
        delta_text_box = TextBox(
            delta_text_box_ax, label="", initial=f"{default_delta:.3g}"
        )
        cval_text_box = TextBox(
            cval_text_box_ax, label="", initial=f"{default_cval:.3g}"
        )

        start_slider = Slider(
            ax=start_slider_ax,
            label="Region Start",
            valmin=0,
            valmax=self.data_len - 3,
            valinit=default_region_start,
            valstep=1,
        )

        length_slider = Slider(
            ax=length_slider_ax,
            label="Region Length",
            valmin=0,
            valmax=self.data_len,
            valinit=default_region_length,
            valstep=1,
        )

        window_length_slider = Slider(
            ax=window_length_slider_ax,
            label="Window Length",
            valmin=3,
            valmax=self.data_len // 2,
            valinit=default_window_length,
            valstep=2,  # 窗口长度必须是奇数
        )

        polyorder_slider = Slider(
            ax=polyorder_slider_ax,
            label="Polyorder",
            valmin=1,
            valmax=9,
            valinit=default_polyorder,
            valstep=1,
        )

        deriv_slider = Slider(
            ax=deriv_slider_ax,
            label="Deriv",
            valmin=0,
            valmax=9,
            valinit=default_deriv,
            valstep=1,
        )

        delta_max = np.diff(self.region_data_x).max()
        if delta_max <= 1.0:
            delta_max = 1.0
        delta_slider = Slider(
            ax=delta_slider_ax,
            label="delta",
            valmin=0,
            valmax=delta_max,
            valinit=default_delta,
            valstep=delta_max / 100,
            valfmt="%.3g",
        )

        cval_slider = Slider(
            ax=cval_slider_ax,
            label="cval",
            valmin=0,
            valmax=max(self.region_data_y),
            valinit=default_cval,
            valstep=0.01,
            valfmt="%.3g",
        )

        # 事件绑定 -----------------------------------------------------
        # noinspection PyShadowingNames,DuplicatedCode
        def mode_change_option(label):
            nonlocal ax1, ax2, s, marker
            self.mode = label
            self.update_plot(ax1, ax2, s=s, marker=marker)

        # 设置选项改变时调用的函数
        mode_radio.on_clicked(mode_change_option)

        # noinspection PyUnusedLocal,PyUnresolvedReferences
        def on_save_button_change(val):
            nonlocal save_path, save_file_name
            if not os.path.exists(save_path):
                os.makedirs(save_path, exist_ok=True)
            data_outfile = os.path.abspath(os.path.join(save_path, save_file_name))
            assert data_outfile is not None
            data = pd.DataFrame(
                {
                    "region_data_x": self.region_data_x,
                    "region_data_y": self.region_data_y,
                    "region_data_y_filtered": self.region_data_y_filtered,
                }
            )
            data.to_csv(data_outfile, index=False)

        save_button.on_clicked(on_save_button_change)

        # noinspection PyUnusedLocal
        def on_reset_button_change(val):
            nonlocal default_region_start
            nonlocal default_region_length
            nonlocal default_window_length
            nonlocal default_polyorder
            nonlocal default_deriv
            nonlocal default_delta
            nonlocal default_cval
            nonlocal default_mode
            nonlocal ax1, ax2, s, marker
            # ----------------------------------------------------------
            self.region_start = default_region_start
            self.region_length = default_region_length
            self.window_length = default_window_length
            self.polyorder = default_polyorder
            self.deriv = default_deriv
            self.delta = default_delta
            self.cval = default_cval
            self.mode = default_mode
            # ----------------------------------------------------------
            start_slider.set_val(self.region_start)
            length_slider.set_val(self.region_length)
            window_length_slider.set_val(self.window_length)
            polyorder_slider.set_val(self.polyorder)
            deriv_slider.set_val(self.deriv)
            delta_slider.set_val(self.delta)
            cval_slider.set_val(self.cval)
            # ----------------------------------------------------------
            start_text_box.set_val(str(self.region_start))
            length_text_box.set_val(str(self.region_length))
            window_length_text_box.set_val(str(self.window_length))
            polyorder_text_box.set_val(str(self.polyorder))
            deriv_text_box.set_val(str(self.deriv))
            delta_text_box.set_val(f"{self.delta:.3g}")
            cval_text_box.set_val(f"{self.cval:.3g}")
            # ----------------------------------------------------------
            mode_radio.set_active(self.modes.index(self.mode))
            # ----------------------------------------------------------
            self.update_plot(ax1, ax2, s=s, marker=marker)

        reset_button.on_clicked(on_reset_button_change)

        def on_start_changed(val):
            nonlocal ax1, ax2, s, marker
            self.region_start = int(val)
            start_text_box.set_val(str(self.region_start))
            self.update_plot(ax1, ax2, s=s, marker=marker)

        start_slider.on_changed(on_start_changed)

        def on_length_changed(val):
            nonlocal ax1, ax2, s, marker
            self.region_length = int(val)
            length_text_box.set_val(str(self.region_length))
            self.update_plot(ax1, ax2, s=s, marker=marker)

        length_slider.on_changed(on_length_changed)

        def on_window_length_changed(val):
            nonlocal ax1, ax2, s, marker
            self.window_length = int(val)
            window_length_text_box.set_val(str(self.window_length))
            self.update_plot(ax1, ax2, s=s, marker=marker)

        window_length_slider.on_changed(on_window_length_changed)

        def on_polyorder_changed(val):
            nonlocal ax1, ax2, s, marker
            self.polyorder = int(val)
            polyorder_text_box.set_val(str(self.polyorder))
            self.update_plot(ax1, ax2, s=s, marker=marker)

        polyorder_slider.on_changed(on_polyorder_changed)

        def on_deriv_changed(val):
            nonlocal ax1, ax2, s, marker
            self.deriv = int(val)
            deriv_text_box.set_val(str(self.deriv))
            self.update_plot(ax1, ax2, s=s, marker=marker)

        deriv_slider.on_changed(on_deriv_changed)

        def on_delta_changed(val):
            nonlocal ax1, ax2, s, marker
            self.delta = float(val)
            delta_text_box.set_val(f"{f"{self.delta:.3g}"}")
            self.update_plot(ax1, ax2, s=s, marker=marker)

        delta_slider.on_changed(on_delta_changed)

        def on_cval_changed(val):
            nonlocal ax1, ax2, s, marker
            self.cval = float(val)
            cval_text_box.set_val(f"{self.cval:.3g}")
            self.update_plot(ax1, ax2, s=s, marker=marker)

        cval_slider.on_changed(on_cval_changed)

        # -------------------------------------------------------------
        def start_text_box_change(text):
            nonlocal ax1, ax2, s, marker
            self.region_start = int(text)
            start_slider.set_val(self.region_start)
            self.update_plot(ax1, ax2, s=s, marker=marker)

        start_text_box.on_submit(start_text_box_change)

        def length_text_box_change(text):
            nonlocal ax1, ax2, s, marker
            self.region_length = int(text)
            length_slider.set_val(self.region_length)
            self.update_plot(ax1, ax2, s=s, marker=marker)

        length_text_box.on_submit(length_text_box_change)

        def window_length_text_box_change(text):
            nonlocal ax1, ax2, s, marker
            self.window_length = int(text)
            window_length_slider.set_val(self.window_length)
            self.update_plot(ax1, ax2, s=s, marker=marker)

        window_length_text_box.on_submit(window_length_text_box_change)

        def polyorder_text_box_change(text):
            nonlocal ax1, ax2, s, marker
            self.polyorder = int(text)
            polyorder_slider.set_val(self.polyorder)
            self.update_plot(ax1, ax2, s=s, marker=marker)

        polyorder_text_box.on_submit(polyorder_text_box_change)

        def deriv_text_box_change(text):
            nonlocal ax1, ax2, s, marker
            self.deriv = int(text)
            deriv_slider.set_val(self.deriv)
            self.update_plot(ax1, ax2, s=s, marker=marker)

        deriv_text_box.on_submit(deriv_text_box_change)

        def delta_text_box_change(text):
            nonlocal ax1, ax2, s, marker
            self.delta = float(text)
            delta_slider.set_val(self.delta)
            self.update_plot(ax1, ax2, s=s, marker=marker)

        delta_text_box.on_submit(delta_text_box_change)

        def cval_text_box_change(text):
            nonlocal ax1, ax2, s, marker
            self.cval = float(text)
            cval_slider.set_val(self.cval)
            self.update_plot(ax1, ax2, s=s, marker=marker)

        cval_text_box.on_submit(cval_text_box_change)
        # ---------------------------------------------------------------
        plt.show()
        # noinspection PyUnresolvedReferences
        return self.region_data_y_filtered

    def interactive_smooth(self, **kwargs):
        """
        交互式执行平滑。

            可选关键字参数如下：

                1. region_start：要处理数据在原始数据上的起始索引，缺省值：`self.region_start`。

                2. region_length：要处理数据的长度，缺省值：`self.region_length`。

                3. window_length：`scipy.signal.savgol_filter`的参数window_length，缺省值：`self.window_length`。

                4. polyorder：`scipy.signal.savgol_filter`的参数polyorder，缺省值：`self.polyorder`。

                5. deriv：`scipy.signal.savgol_filter`的参数deriv，缺省值：`self.deriv`。

                6. delta：`scipy.signal.savgol_filter`的参数delta，缺省值：`self.delta`。

                7. mode：`scipy.signal.savgol_filter`的参数mode，缺省值：`self.mode`。

                8. cval：`scipy.signal.savgol_filter`的参数cva，缺省值：`self.cval`。

                # -----------------------------------------------------------------

                9. title: 图形的标题，缺省值：'Savgol Filter'。

                10. figsize: 图形的尺寸，缺省值：(12,8)，即宽度（width）为：12，高度（height）为8。

                11. s: 滤波前数据散点的大小，缺省值：5。

                12. marker:滤波前数据散点的形状，缺省值：'o'。

                # -----------------------------------------------------------------

                13. save_path: 保存文件的路径，缺省值：`os.path.expanduser("~")`。

                14. save_file_name：保存文件的文件名，缺省值：`"SavgolFilter_" + unique_string() + ".csv"`。

                # -----------------------------------------------------------------

                15. interactive_mode：交互模式，只能为“simple”或“all”，默认值为：“simple”。

        :param kwargs: 所需的关键字参数。
        :return: 平滑后的数据。
        """
        interactive_mode = kwargs.pop("interactive_mode", "simple")
        if interactive_mode == "simple":
            return self.simple_interactive_smooth(**kwargs)
        elif interactive_mode == "all":
            return self.all_interactive_smooth(**kwargs)
        else:
            raise ValueError("Expected interactive_mode is 'all' or 'simple'.")


# ==========================================================
