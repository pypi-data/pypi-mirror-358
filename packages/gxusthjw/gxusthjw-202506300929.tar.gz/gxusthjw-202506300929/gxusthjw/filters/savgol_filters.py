#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        savgol_filters.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      基于scipy.signal.savgol_filter，
#                   对指定数据执行滤波处理。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2024/10/20     finish
# ------------------------------------------------------------------
# 导包 ==============================================================
import os
from typing import Optional, Tuple

import numpy as np
import numpy.typing as npt
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.widgets import (RadioButtons, Slider,
                                TextBox, Button)
from scipy.signal import savgol_filter

from ..commons import NumberSequence, unique_string

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining the filter functions to apply filtering on the specified data
 using the method provided by the scipy.signal.savgol_filter module.
"""

__all__ = [
    'simple_interactive_savgol_filter',
    'all_interactive_savgol_filter',
    'interactive_savgol_filter',
    'static_savgol_filter',
]


# 定义 ==============================================================
def simple_interactive_savgol_filter(
        y: NumberSequence,
        x: Optional[NumberSequence] = None,
        **kwargs) -> Tuple[npt.NDArray, npt.NDArray, npt.NDArray]:
    """
    基于scipy.signal.savgol_filter对指定数据进行简化参数的交互式滤波。

        可选关键字参数：

            1. title: str，图标题，默认值：”Savgol Filter“。

            2. figsize: Tuple[int,int]，图尺寸。默认值：(12, 8)

            3. s: int，滤波前数据的散点大小，缺省值：5。

            4. marker: str，滤波前数据的散点形状，缺省值：'o'。

            5. save_path: str，保存文件路径，缺省值为：`os.path.expanduser('~')`。

            6. save_file: str，保存文件名，缺省值为：`"SavgolFilter_" + unique_string() + ".csv"`。

            # -----------------------------------------------

            7. start: int，要滤波数据在原始数据上的起始索引。

            8. length: int，要滤波数据的长度。

            # -----------------------------------------------

            9. window_length: int，`scipy.signal.savgol_filter`的参数window_length，缺省值：11。
               滤波窗口的长度，即在每个点上进行多项式拟合时所使用的邻近点的数量。这个值必须是一个正奇数整数。

            10. polyorder: int，`scipy.signal.savgol_filter`的参数polyorder，缺省值：2。
                用于拟合数据的多项式的阶数。这个值必须小于 window_length。

            11. deriv: int，`scipy.signal.savgol_filter`的参数deriv，缺省值：0。
                导数的阶数，默认为 0，表示只做平滑处理而不计算导数。

            12. delta: float，`scipy.signal.savgol_filter`的参数delta，缺省值：1.0。
                采样距离，默认为 1.0。只有当 deriv 不为 0 时才有意义。

            13. mode: str，`scipy.signal.savgol_filter`的参数mode，缺省值：'interp'。
                边界模式，可以是 'mirror', 'constant', 'nearest', 'wrap' 或 'interp'。
                默认是 'interp'，使用插值填充边界。

            14. cval: float，`scipy.signal.savgol_filter`的参数cva，缺省值：0.0。
                如果 mode 是 'constant'，则该值用来填充边界。默认是 0.0。

            # -----------------------------------------------

    :param y: 因变量（数据y）。
    :param x: 自变量（数据x,可选）。
    :param kwargs: 可选关键字参数。
    :return: 滤波后的区域数据y, 被滤波的区域数据y,被滤波的区域数据x。
    :rtype: Tuple[npt.NDArray, npt.NDArray, npt.NDArray]
    """
    # 初始化数据 --------------------------------------------------
    ys = np.asarray(y)
    ys_len = ys.shape[0]
    xs = np.arange(ys_len) if x is None else np.asarray(x)
    xs_len = xs.shape[0]
    data_len = xs_len if ys_len > xs_len else ys_len
    start = 0
    length = data_len - start
    # ------------------------------------------------------------
    # 可选关键字参数解析 --------------------------------------------
    title = kwargs.pop('title', "Savgol Filter")
    figsize = kwargs.pop('figsize', (12, 8))
    s = kwargs.pop('s', 5)
    marker = kwargs.pop('marker', 'o')
    save_path = kwargs.pop('save_path', os.path.expanduser('~'))
    save_file_name = kwargs.pop(
        'save_file',
        "SavgolFilter_" + unique_string() + ".csv")
    # 定义默认参数 --------------------------------------------------
    default_start: int = kwargs.pop('start', start)
    default_length: int = kwargs.pop('length', length)
    default_window_length: int = kwargs.pop('window_length', 11)
    default_polyorder: int = kwargs.pop('polyorder', 2)
    default_deriv: int = kwargs.pop('deriv', 0)
    default_delta: float = kwargs.pop('delta', 1.0)
    default_mode: str = kwargs.pop('mode', 'interp')
    default_cval: float = kwargs.pop('cval', 0.0)
    modes = ('interp', 'mirror', 'constant', 'wrap', 'nearest')
    # 定义可变参数 ------------------------------------------------
    start_selected: int = default_start
    length_selected: int = default_length
    window_length_selected: int = default_window_length
    polyorder_selected: int = default_polyorder
    deriv_selected: int = default_deriv
    delta_selected: float = default_delta
    mode_selected: str = default_mode
    cval_selected: float = default_cval
    # 初始化图形 ---------------------------------------------------
    # 绘图时显示中文。
    plt.rcParams['font.family'] = 'SimHei'
    plt.rcParams['axes.unicode_minus'] = False
    fig, (ax1, ax2) = plt.subplots(
        1, 2,
        figsize=figsize,
        gridspec_kw={'width_ratios': [1, 1],
                     'wspace': 0.2,
                     'left': 0.05,
                     'right': 0.95}
    )
    fig.suptitle(title)
    plt.subplots_adjust(bottom=0.3)  # 底部留出空间
    # ------------------------------------------------------------
    # 过程变量 ----------------------------------------------------
    y_var = ys[start_selected:start_selected + length_selected]
    x_var = xs[start_selected:start_selected + length_selected]
    y_filtered = ys[start_selected:start_selected + length_selected]
    y_error = y_var - y_filtered

    # 定义更新函数 --------------------------------------------------
    def _update():
        nonlocal ax1
        nonlocal ax2
        nonlocal start_selected
        nonlocal length_selected
        nonlocal window_length_selected
        nonlocal polyorder_selected
        nonlocal deriv_selected
        nonlocal delta_selected
        nonlocal mode_selected
        nonlocal cval_selected
        nonlocal x_var
        nonlocal y_var
        nonlocal y_filtered
        nonlocal y_error

        # 截取数据。
        y_var = ys[start_selected:start_selected + length_selected]
        x_var = xs[start_selected:start_selected + length_selected]
        # 计算数据。
        y_filtered = savgol_filter(y_var, window_length=window_length_selected,
                                   polyorder=polyorder_selected,
                                   deriv=deriv_selected, delta=delta_selected,
                                   mode=mode_selected, cval=cval_selected)
        y_error = y_var - y_filtered

        # 画图
        ax1.cla()
        ax1.scatter(x_var, y_var, s=s, marker=marker)
        ax1.plot(x_var, y_filtered)
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        fig_legend_other_text = ("Filter x:[{:.0f},{:.0f}]".format(x_var[0], x_var[-1]))
        handles, labels = ax1.get_legend_handles_labels()
        handles.append(mpatches.Patch(color='none', label=fig_legend_other_text))
        plt.rc('legend', fontsize=10)
        ax1.legend(loc='best', handles=handles)

        ax2.cla()
        ax2.plot(x_var, y_error)
        ax2.set_xlabel('X')
        ax2.set_ylabel('Y')
        fig_legend_other_text = ("Residual x:[{:.0f},{:.0f}]".format(x_var[0], x_var[-1]))
        handles, labels = ax2.get_legend_handles_labels()
        handles.append(mpatches.Patch(color='none', label=fig_legend_other_text))
        plt.rc('legend', fontsize=10)
        ax2.legend(loc='best', handles=handles)

    _update()
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
    mode_radio = RadioButtons(mode_ax, modes,
                              active=modes.index(default_mode),
                              activecolor='red')
    # 增加标签的字体大小
    for label in mode_radio.labels:
        label.set_fontsize(12)  # 设置字体大小为 12
    # 创建按钮部件 -------------------------------------------------
    save_button = Button(save_button_ax, 'Save')
    reset_button = Button(reset_button_ax, 'Reset')
    # 创建滑块部件 --------------------------------------------------

    start_slider = Slider(
        ax=start_slider_ax,
        label='Start',
        valmin=0,
        valmax=data_len - 3,
        valinit=default_start,
        valstep=1
    )

    length_slider = Slider(
        ax=length_slider_ax,
        label='Length',
        valmin=0,
        valmax=data_len,
        valinit=default_length,
        valstep=1
    )

    window_length_slider = Slider(
        ax=window_length_slider_ax,
        label='Window Length',
        valmin=3,
        valmax=data_len // 2,
        valinit=default_window_length,
        valstep=2  # 窗口长度必须是奇数
    )

    polyorder_slider = Slider(
        ax=polyorder_slider_ax,
        label='Polyorder',
        valmin=1,
        valmax=9,
        valinit=default_polyorder,
        valstep=1
    )
    start_text_box = TextBox(start_text_box_ax, label='', initial=str(default_start))
    length_text_box = TextBox(length_text_box_ax, label='', initial=str(default_length))
    window_length_text_box = TextBox(window_length_text_box_ax, label='', initial=str(default_window_length))
    polyorder_text_box = TextBox(polyorder_text_box_ax, label='', initial=str(default_polyorder))
    deriv_text_box = TextBox(deriv_text_box_ax, label='deriv: ', initial=str(default_deriv))
    delta_text_box = TextBox(delta_text_box_ax, label='delta: ', initial=f"{default_delta:.3g}")
    cval_text_box = TextBox(cval_text_box_ax, label='cval: ', initial=f"{default_cval:.3g}")

    # 事件绑定 -----------------------------------------------------
    # noinspection PyShadowingNames,DuplicatedCode
    def mode_change_option(label):
        nonlocal mode_selected
        mode_selected = label
        _update()

    # 设置选项改变时调用的函数
    mode_radio.on_clicked(mode_change_option)

    # noinspection PyUnusedLocal,PyUnresolvedReferences
    def on_save_button_change(val):
        data_outfile = os.path.join(save_path, save_file_name)
        data = pd.DataFrame({'var_x': x_var, 'var_y': y_var, 'var_y_filtered': y_filtered})
        data.to_csv(data_outfile, index=False)

    save_button.on_clicked(on_save_button_change)

    # noinspection PyUnusedLocal
    def on_reset_button_change(val):
        nonlocal start_selected
        nonlocal length_selected
        nonlocal window_length_selected
        nonlocal polyorder_selected
        nonlocal deriv_selected
        nonlocal delta_selected
        nonlocal mode_selected
        nonlocal cval_selected
        # ----------------------------------------------------------
        start_selected = default_start
        length_selected = default_length
        window_length_selected = default_window_length
        polyorder_selected = default_polyorder
        deriv_selected = default_deriv
        delta_selected = default_delta
        cval_selected = default_cval
        mode_selected = default_mode
        # ----------------------------------------------------------
        start_slider.set_val(start_selected)
        length_slider.set_val(length_selected)
        window_length_slider.set_val(window_length_selected)
        polyorder_slider.set_val(polyorder_selected)
        # ----------------------------------------------------------
        start_text_box.set_val(str(start_selected))
        length_text_box.set_val(str(length_selected))
        window_length_text_box.set_val(str(window_length_selected))
        polyorder_text_box.set_val(str(polyorder_selected))
        deriv_text_box.set_val(str(deriv_selected))
        delta_text_box.set_val(f"{delta_selected:.3g}")
        cval_text_box.set_val(f"{cval_selected:.3g}")
        # ----------------------------------------------------------
        mode_radio.set_active(modes.index(mode_selected))
        # ----------------------------------------------------------
        _update()

    reset_button.on_clicked(on_reset_button_change)

    def on_start_changed(val):
        nonlocal start_selected
        start_selected = int(val)
        start_text_box.set_val(str(start_selected))
        _update()

    start_slider.on_changed(on_start_changed)

    def on_length_changed(val):
        nonlocal length_selected
        length_selected = int(val)
        length_text_box.set_val(str(length_selected))
        _update()

    length_slider.on_changed(on_length_changed)

    def on_window_length_changed(val):
        nonlocal window_length_selected
        window_length_selected = int(val)
        window_length_text_box.set_val(str(window_length_selected))
        _update()

    window_length_slider.on_changed(on_window_length_changed)

    def on_polyorder_changed(val):
        nonlocal polyorder_selected
        polyorder_selected = int(val)
        polyorder_text_box.set_val(str(polyorder_selected))
        _update()

    polyorder_slider.on_changed(on_polyorder_changed)

    # -------------------------------------------------------------
    def start_text_box_change(text):
        nonlocal start_selected
        start_selected = int(text)
        start_slider.set_val(start_selected)
        _update()

    start_text_box.on_submit(start_text_box_change)

    def length_text_box_change(text):
        nonlocal length_selected
        length_selected = int(text)
        length_slider.set_val(length_selected)
        _update()

    length_text_box.on_submit(length_text_box_change)

    def window_length_text_box_change(text):
        nonlocal window_length_selected
        window_length_selected = int(text)
        window_length_slider.set_val(window_length_selected)
        _update()

    window_length_text_box.on_submit(window_length_text_box_change)

    def polyorder_text_box_change(text):
        nonlocal polyorder_selected
        polyorder_selected = int(text)
        polyorder_slider.set_val(polyorder_selected)
        _update()

    polyorder_text_box.on_submit(polyorder_text_box_change)

    def deriv_text_box_change(text):
        nonlocal deriv_selected
        deriv_selected = int(text)
        _update()

    deriv_text_box.on_submit(deriv_text_box_change)

    def delta_text_box_change(text):
        nonlocal delta_selected
        delta_selected = float(text)
        _update()

    delta_text_box.on_submit(delta_text_box_change)

    def cval_text_box_change(text):
        nonlocal cval_selected
        cval_selected = float(text)
        _update()

    cval_text_box.on_submit(cval_text_box_change)
    # -------------------------------------------------------------------
    plt.show()
    return y_filtered, y_var, x_var


# =========================================================================

def all_interactive_savgol_filter(
        y: NumberSequence,
        x: Optional[NumberSequence] = None,
        **kwargs) -> Tuple[npt.NDArray, npt.NDArray, npt.NDArray]:
    """
    基于scipy.signal.savgol_filter对指定数据进行全参的交互式滤波。

        可选关键字参数：

            1. title: str，图标题，默认值：”Savgol Filter“。

            2. figsize: Tuple[int,int]，图尺寸。默认值：(12, 8)

            3. s: int，滤波前数据的散点大小，缺省值：5。

            4. marker: str，滤波前数据的散点形状，缺省值：'o'。

            5. save_path: str，保存文件路径，缺省值为：`os.path.expanduser('~')`。

            6. save_file: str，保存文件名，缺省值为：`"SavgolFilter_" + unique_string() + ".csv"`。

            # -----------------------------------------------

            7. start: int，要滤波数据在原始数据上的起始索引。

            8. length: int，要滤波数据的长度。

            # -----------------------------------------------

            9. window_length: int，`scipy.signal.savgol_filter`的参数window_length，缺省值：11。
               滤波窗口的长度，即在每个点上进行多项式拟合时所使用的邻近点的数量。这个值必须是一个正奇数整数。

            10. polyorder: int，`scipy.signal.savgol_filter`的参数polyorder，缺省值：2。
                用于拟合数据的多项式的阶数。这个值必须小于 window_length。

            11. deriv: int，`scipy.signal.savgol_filter`的参数deriv，缺省值：0。
                导数的阶数，默认为 0，表示只做平滑处理而不计算导数。

            12. delta: float，`scipy.signal.savgol_filter`的参数delta，缺省值：1.0。
                采样距离，默认为 1.0。只有当 deriv 不为 0 时才有意义。

            13. mode: str，`scipy.signal.savgol_filter`的参数mode，缺省值：'interp'。
                边界模式，可以是 'mirror', 'constant', 'nearest', 'wrap' 或 'interp'。
                默认是 'interp'，使用插值填充边界。

            14. cval: float，`scipy.signal.savgol_filter`的参数cva，缺省值：0.0。
                如果 mode 是 'constant'，则该值用来填充边界。默认是 0.0。

            # -----------------------------------------------

    :param y: 因变量（数据y）。
    :param x: 自变量（数据x,可选）。
    :param kwargs: 可选关键字参数。
    :return: 滤波后的区域数据y, 被滤波的区域数据y,被滤波的区域数据x。
    :rtype:Tuple[npt.NDArray, npt.NDArray, npt.NDArray]
    """
    # 初始化数据 ------------------------------------------------------
    ys = np.asarray(y)
    ys_len = ys.shape[0]
    xs = np.arange(ys_len) if x is None else np.asarray(x)
    xs_len = xs.shape[0]
    data_len = xs_len if ys_len > xs_len else ys_len
    start = 0
    length = data_len - start
    # ------------------------------------------------------------
    # 消耗可选关键字参数 --------------------------------------------
    title = kwargs.pop('title', "Savgol Filter")
    figsize = kwargs.pop('figsize', (12, 8))
    s = kwargs.pop('s', 5)
    marker = kwargs.pop('marker', 'o')
    save_path = kwargs.pop('save_path', os.path.expanduser('~'))
    save_file_name = kwargs.pop(
        'save_file', "SavgolFilter_" + unique_string() + ".csv")
    # 定义默认参数 --------------------------------------------------
    default_start: int = kwargs.pop('start', start)
    default_length: int = kwargs.pop('length', length)
    default_window_length: int = kwargs.pop('window_length', 11)
    default_polyorder: int = kwargs.pop('polyorder', 2)
    default_deriv: int = kwargs.pop('deriv', 0)
    default_delta: float = kwargs.pop('delta', 1.0)
    default_mode: str = kwargs.pop('mode', 'interp')
    default_cval: float = kwargs.pop('cval', 0.0)

    modes = ('interp', 'mirror', 'constant', 'wrap', 'nearest')
    # 定义可变参数 ------------------------------------------------
    start_selected: int = default_start
    length_selected: int = default_length
    window_length_selected: int = default_window_length
    polyorder_selected: int = default_polyorder
    deriv_selected: int = default_deriv
    delta_selected: float = default_delta
    mode_selected: str = default_mode
    cval_selected: float = default_cval
    # 过程变量 ----------------------------------------------------
    y_var = ys[start_selected:start_selected + length_selected]
    x_var = xs[start_selected:start_selected + length_selected]
    y_filtered = ys[start_selected:start_selected + length_selected]
    y_error = y_var - y_filtered
    # 初始化图形 ---------------------------------------------------
    # 绘图时显示中文。
    plt.rcParams['font.family'] = 'SimHei'
    plt.rcParams['axes.unicode_minus'] = False
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=figsize,
        gridspec_kw={'width_ratios': [1, 1],
                     'wspace': 0.2,
                     'left': 0.05,
                     'right': 0.95})
    fig.suptitle(title)
    plt.subplots_adjust(bottom=0.3)  # 底部留出空间

    # ------------------------------------------------------------
    # 定义更新函数 --------------------------------------------------
    def _update():
        nonlocal ax1
        nonlocal ax2
        nonlocal start_selected
        nonlocal length_selected
        nonlocal window_length_selected
        nonlocal polyorder_selected
        nonlocal deriv_selected
        nonlocal delta_selected
        nonlocal mode_selected
        nonlocal cval_selected
        nonlocal x_var
        nonlocal y_var
        nonlocal y_filtered
        nonlocal y_error

        # 截取数据。
        y_var = ys[start_selected:start_selected + length_selected]
        x_var = xs[start_selected:start_selected + length_selected]
        # 计算数据。
        y_filtered = savgol_filter(y_var, window_length=window_length_selected,
                                   polyorder=polyorder_selected,
                                   deriv=deriv_selected, delta=delta_selected,
                                   mode=mode_selected, cval=cval_selected)
        y_error = y_var - y_filtered

        # 画图
        ax1.cla()
        ax1.scatter(x_var, y_var, s=s, marker=marker)
        ax1.plot(x_var, y_filtered)
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        fig_legend_other_text = ("Filter x:[{:.0f},{:.0f}]".format(x_var[0], x_var[-1]))
        handles, labels = ax1.get_legend_handles_labels()
        handles.append(mpatches.Patch(color='none', label=fig_legend_other_text))
        plt.rc('legend', fontsize=10)
        ax1.legend(loc='best', handles=handles)

        ax2.cla()
        ax2.plot(x_var, y_error)
        ax2.set_xlabel('X')
        ax2.set_ylabel('Y')
        fig_legend_other_text = ("Residual x:[{:.0f},{:.0f}]".format(x_var[0], x_var[-1]))
        handles, labels = ax2.get_legend_handles_labels()
        handles.append(mpatches.Patch(color='none', label=fig_legend_other_text))
        plt.rc('legend', fontsize=10)
        ax2.legend(loc='best', handles=handles)

    _update()
    # 创建部件 -----------------------------------------------------
    mode_ax = plt.axes((0.795, 0.02, 0.1, 0.21))
    mode_radio = RadioButtons(mode_ax, modes, active=modes.index(default_mode),
                              activecolor='red')
    # 增加标签的字体大小
    for label in mode_radio.labels:
        label.set_fontsize(12)  # 设置字体大小为 12
    # -------------------------------------------------------------
    save_button_ax = plt.axes((0.9, 0.02, 0.055, 0.095))
    save_button = Button(save_button_ax, 'Save')

    reset_button_ax = plt.axes((0.9, 0.135, 0.055, 0.095))
    reset_button = Button(reset_button_ax, 'Reset')
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

    start_text_box = TextBox(start_text_box_ax, label='', initial=str(default_start))
    length_text_box = TextBox(length_text_box_ax, label='', initial=str(default_length))
    window_length_text_box = TextBox(window_length_text_box_ax, label='', initial=str(default_window_length))
    polyorder_text_box = TextBox(polyorder_text_box_ax, label='', initial=str(default_polyorder))
    deriv_text_box = TextBox(deriv_text_box_ax, label='', initial=str(default_deriv))
    delta_text_box = TextBox(delta_text_box_ax, label='', initial=f"{default_delta:.3g}")
    cval_text_box = TextBox(cval_text_box_ax, label='', initial=f"{default_cval:.3g}")

    start_slider = Slider(
        ax=start_slider_ax,
        label='Start',
        valmin=0,
        valmax=data_len - 3,
        valinit=default_start,
        valstep=1
    )

    length_slider = Slider(
        ax=length_slider_ax,
        label='Length',
        valmin=0,
        valmax=data_len,
        valinit=default_length,
        valstep=1
    )

    window_length_slider = Slider(
        ax=window_length_slider_ax,
        label='Window Length',
        valmin=3,
        valmax=data_len // 2,
        valinit=default_window_length,
        valstep=2  # 窗口长度必须是奇数
    )

    polyorder_slider = Slider(
        ax=polyorder_slider_ax,
        label='Polyorder',
        valmin=1,
        valmax=9,
        valinit=default_polyorder,
        valstep=1
    )

    deriv_slider = Slider(
        ax=deriv_slider_ax,
        label='Deriv',
        valmin=0,
        valmax=9,
        valinit=default_deriv,
        valstep=1
    )

    delta_max = np.diff(xs).max()
    if delta_max <= 1.0:
        delta_max = 1.0
    delta_slider = Slider(
        ax=delta_slider_ax,
        label='delta',
        valmin=0,
        valmax=delta_max,
        valinit=default_delta,
        valstep=delta_max / 100,
        valfmt="%.3g"
    )

    cval_slider = Slider(
        ax=cval_slider_ax,
        label='cval',
        valmin=0,
        valmax=max(ys),
        valinit=default_cval,
        valstep=0.01,
        valfmt="%.3g"
    )

    # 事件绑定 -----------------------------------------------------
    # noinspection PyShadowingNames,DuplicatedCode
    def mode_change_option(label):
        nonlocal mode_selected
        mode_selected = label
        _update()

    # 设置选项改变时调用的函数
    mode_radio.on_clicked(mode_change_option)

    # noinspection PyUnusedLocal,PyUnresolvedReferences
    def on_save_button_change(val):
        data_outfile = os.path.join(save_path, save_file_name)
        data = pd.DataFrame({'var_x': x_var, 'var_y': y_var, 'var_y_filtered': y_filtered})
        data.to_csv(data_outfile, index=False)

    save_button.on_clicked(on_save_button_change)

    # noinspection PyUnusedLocal
    def on_reset_button_change(val):
        nonlocal start_selected
        nonlocal length_selected
        nonlocal window_length_selected
        nonlocal polyorder_selected
        nonlocal deriv_selected
        nonlocal delta_selected
        nonlocal mode_selected
        nonlocal cval_selected
        # ----------------------------------------------------------
        start_selected = default_start
        length_selected = default_length
        window_length_selected = default_window_length
        polyorder_selected = default_polyorder
        deriv_selected = default_deriv
        delta_selected = default_delta
        cval_selected = default_cval
        mode_selected = default_mode
        # ----------------------------------------------------------
        start_slider.set_val(start_selected)
        length_slider.set_val(length_selected)
        window_length_slider.set_val(window_length_selected)
        polyorder_slider.set_val(polyorder_selected)
        deriv_slider.set_val(deriv_selected)
        delta_slider.set_val(delta_selected)
        cval_slider.set_val(cval_selected)
        # ----------------------------------------------------------
        start_text_box.set_val(str(start_selected))
        length_text_box.set_val(str(length_selected))
        window_length_text_box.set_val(str(window_length_selected))
        polyorder_text_box.set_val(str(polyorder_selected))
        deriv_text_box.set_val(str(deriv_selected))
        delta_text_box.set_val(f"{delta_selected:.3g}")
        cval_text_box.set_val(f"{cval_selected:.3g}")
        # ----------------------------------------------------------
        mode_radio.set_active(modes.index(mode_selected))
        # ----------------------------------------------------------
        _update()

    reset_button.on_clicked(on_reset_button_change)

    def on_start_changed(val):
        nonlocal start_selected
        start_selected = int(val)
        start_text_box.set_val(str(start_selected))
        _update()

    start_slider.on_changed(on_start_changed)

    def on_length_changed(val):
        nonlocal length_selected
        length_selected = int(val)
        length_text_box.set_val(str(length_selected))
        _update()

    length_slider.on_changed(on_length_changed)

    def on_window_length_changed(val):
        nonlocal window_length_selected
        window_length_selected = int(val)
        window_length_text_box.set_val(str(window_length_selected))
        _update()

    window_length_slider.on_changed(on_window_length_changed)

    def on_polyorder_changed(val):
        nonlocal polyorder_selected
        polyorder_selected = int(val)
        polyorder_text_box.set_val(str(polyorder_selected))
        _update()

    polyorder_slider.on_changed(on_polyorder_changed)

    def on_deriv_changed(val):
        nonlocal deriv_selected
        deriv_selected = int(val)
        deriv_text_box.set_val(str(deriv_selected))
        _update()

    deriv_slider.on_changed(on_deriv_changed)

    def on_delta_changed(val):
        nonlocal delta_selected
        delta_selected = float(val)
        delta_text_box.set_val(f"{f"{delta_selected:1.3g}"}")
        _update()

    delta_slider.on_changed(on_delta_changed)

    def on_cval_changed(val):
        nonlocal cval_selected
        cval_selected = float(val)
        cval_text_box.set_val(f"{cval_selected:1.3g}")
        _update()

    cval_slider.on_changed(on_cval_changed)

    # -------------------------------------------------------------
    def start_text_box_change(text):
        nonlocal start_selected
        start_selected = int(text)
        start_slider.set_val(start_selected)
        _update()

    start_text_box.on_submit(start_text_box_change)

    def length_text_box_change(text):
        nonlocal length_selected
        length_selected = int(text)
        length_slider.set_val(length_selected)
        _update()

    length_text_box.on_submit(length_text_box_change)

    def window_length_text_box_change(text):
        nonlocal window_length_selected
        window_length_selected = int(text)
        window_length_slider.set_val(window_length_selected)
        _update()

    window_length_text_box.on_submit(window_length_text_box_change)

    def polyorder_text_box_change(text):
        nonlocal polyorder_selected
        polyorder_selected = int(text)
        polyorder_slider.set_val(polyorder_selected)
        _update()

    polyorder_text_box.on_submit(polyorder_text_box_change)

    def deriv_text_box_change(text):
        nonlocal deriv_selected
        deriv_selected = int(text)
        deriv_slider.set_val(deriv_selected)
        _update()

    deriv_text_box.on_submit(deriv_text_box_change)

    def delta_text_box_change(text):
        nonlocal delta_selected
        delta_selected = float(text)
        delta_slider.set_val(delta_selected)
        _update()

    delta_text_box.on_submit(delta_text_box_change)

    def cval_text_box_change(text):
        nonlocal cval_selected
        cval_selected = float(text)
        cval_slider.set_val(cval_selected)
        _update()

    cval_text_box.on_submit(cval_text_box_change)
    # -------------------------------------------------------------------
    plt.show()
    return y_filtered, y_var, x_var


# =========================================================================
def interactive_savgol_filter(y: NumberSequence,
                              x: Optional[NumberSequence] = None,
                              **kwargs):
    """
    基于scipy.signal.savgol_filter对指定数据进行交互式平滑。

        可选关键字参数：

            1. interactive_mode：交互模式，允许值为：['all','simple'],
                                 缺省值为:'simple'。
            # ----------------------------------------------------

            2. title: str，图标题，默认值：”Savgol Filter“。

            3. figsize: Tuple[int,int]，图尺寸。默认值：(12, 8)

            4. s: int，滤波前数据的散点大小，缺省值：5。

            5. marker: str，滤波前数据的散点形状，缺省值：'o'。

            6. save_path: str，保存文件路径，缺省值为：`os.path.expanduser('~')`。

            7. save_file: str，保存文件名，缺省值为：`"SavgolFilter_" + unique_string() + ".csv"`。

            # -----------------------------------------------

            8. start: int，要滤波数据在原始数据上的起始索引。

            9. length: int，要滤波数据的长度。

            # -----------------------------------------------

            10. window_length: int，`scipy.signal.savgol_filter`的参数window_length，缺省值：11。
               滤波窗口的长度，即在每个点上进行多项式拟合时所使用的邻近点的数量。这个值必须是一个正奇数整数。

            11. polyorder: int，`scipy.signal.savgol_filter`的参数polyorder，缺省值：2。
                用于拟合数据的多项式的阶数。这个值必须小于 window_length。

            12. deriv: int，`scipy.signal.savgol_filter`的参数deriv，缺省值：0。
                导数的阶数，默认为 0，表示只做平滑处理而不计算导数。

            13. delta: float，`scipy.signal.savgol_filter`的参数delta，缺省值：1.0。
                采样距离，默认为 1.0。只有当 deriv 不为 0 时才有意义。

            14. mode: str，`scipy.signal.savgol_filter`的参数mode，缺省值：'interp'。
                边界模式，可以是 'mirror', 'constant', 'nearest', 'wrap' 或 'interp'。
                默认是 'interp'，使用插值填充边界。

            15. cval: float，`scipy.signal.savgol_filter`的参数cva，缺省值：0.0。
                如果 mode 是 'constant'，则该值用来填充边界。默认是 0.0。

            # -----------------------------------------------

    :param y: 因变量（数据y）。
    :param x: 自变量（数据x,可选）。
    :return: 滤波后的区域数据y, 被滤波的区域数据y,被滤波的区域数据x。
    :rtype:Tuple[npt.NDArray, npt.NDArray, npt.NDArray]
    """
    interactive_mode = kwargs.pop('interactive_mode', 'simple')
    if interactive_mode == 'simple':
        return simple_interactive_savgol_filter(y, x, **kwargs)
    elif interactive_mode == 'all':
        return all_interactive_savgol_filter(y, x, **kwargs)
    else:
        raise ValueError("Expected interactive_mode is 'all' or 'simple'.")


# =========================================================================
def static_savgol_filter(y: NumberSequence,
                         x: Optional[NumberSequence] = None,
                         **kwargs):
    """
    基于scipy.signal.savgol_filter对指定数据进行滤波。

        可选关键字参数：

            1. start: int，要滤波数据在原始数据上的起始索引。

            2. length: int，要滤波数据的长度。

            #-----------------------------------------

            3. window_length: int，`scipy.signal.savgol_filter`的参数window_length，缺省值：11。
               滤波窗口的长度，即在每个点上进行多项式拟合时所使用的邻近点的数量。这个值必须是一个正奇数整数。

            4. polyorder: int，`scipy.signal.savgol_filter`的参数polyorder，缺省值：2。
                用于拟合数据的多项式的阶数。这个值必须小于 window_length。

            5. deriv: int，`scipy.signal.savgol_filter`的参数deriv，缺省值：0。
                导数的阶数，默认为 0，表示只做平滑处理而不计算导数。

            6. delta: float，`scipy.signal.savgol_filter`的参数delta，缺省值：1.0。
                采样距离，默认为 1.0。只有当 deriv 不为 0 时才有意义。

            7. mode: str，`scipy.signal.savgol_filter`的参数mode，缺省值：'interp'。
                边界模式，可以是 'mirror', 'constant', 'nearest', 'wrap' 或 'interp'。
                默认是 'interp'，使用插值填充边界。

            9. cval: float，`scipy.signal.savgol_filter`的参数cva，缺省值：0.0。
                如果 mode 是 'constant'，则该值用来填充边界。默认是 0.0。

            # -----------------------------------------------

            10. is_data_out: 指示是否输出处理结果。

            11. data_outfile_name: 输出数据文件的名称。

            12. data_outpath: 数据输出路径。

            13. is_print_summary: 是否打印summary。

            14. is_plot: 指示是否绘图。

            15. is_fig_out: 指示是否输出图形。

            16. fig_outfile_name: 图形输出文件名。

            17. fig_outpath: 图形输出路径。

            18. is_show_fig: 指示是否显示绘图。

            # -----------------------------------------------

            20. title: str，图标题，默认值：”Savgol Filter“。

            21. figsize: Tuple[int,int]，图尺寸。默认值：(12, 8)

            22. s: int，滤波前数据的散点大小，缺省值：5。

            23. marker: str，滤波前数据的散点形状，缺省值：'o'。

    :param y: 因变量（数据y）。
    :param x: 自变量（数据x,可选）。
    :return: 滤波后的区域数据y, 被滤波的区域数据y,被滤波的区域数据x。
    :rtype:Tuple[npt.NDArray, npt.NDArray, npt.NDArray]
    """
    # 初始化数据 ------------------------------------------------------
    ys = np.asarray(y)
    ys_len = ys.shape[0]
    xs = np.arange(ys_len) if x is None else np.asarray(x)
    xs_len = xs.shape[0]
    data_len = xs_len if ys_len > xs_len else ys_len
    start = 0
    length = data_len - start
    # ------------------------------------------------------------
    # 解析可选关键字参数 --------------------------------------------
    start: int = kwargs.pop('start', start)
    length: int = kwargs.pop('length', length)
    window_length: int = kwargs.pop('window_length', 11)
    polyorder: int = kwargs.pop('polyorder', 2)
    deriv: int = kwargs.pop('deriv', 0)
    delta: float = kwargs.pop('delta', 1.0)
    mode: str = kwargs.pop('mode', 'interp')
    cval: float = kwargs.pop('cval', 0.0)
    # -----------------------------------------------------------
    is_data_out = kwargs.pop("is_data_out", False)
    data_outfile_name = kwargs.pop('data_outfile_name', "SavgolFilter_" + unique_string())
    data_outpath = kwargs.pop('data_outpath', os.path.expanduser('~'))
    data_outfile = os.path.join(data_outpath, "{}.csv".format(data_outfile_name))
    # -----------------------------------------------------------
    is_print_summary = kwargs.pop('is_print_summary', False)
    # -----------------------------------------------------------
    is_plot = kwargs.pop('is_plot', False)
    is_fig_out = kwargs.pop('is_fig_out', False)
    fig_outfile_name = kwargs.pop('fig_outfile_name', "SavgolFilter_" + unique_string())
    fig_outpath = kwargs.pop('fig_outpath', os.path.expanduser('~'))
    fig_outfile = os.path.join(fig_outpath, "{}.png".format(fig_outfile_name))
    is_show_fig = kwargs.pop('is_show_fig', False)
    # -----------------------------------------------------------
    title = kwargs.pop('title', "Savgol Filter")
    figsize = kwargs.pop('figsize', (12, 8))
    s = kwargs.pop('s', 5)
    marker = kwargs.pop('marker', 'o')
    # 数据准备与滤波 ----------------------------------------------
    y_var = ys[start:start + length]
    x_var = xs[start:start + length]
    y_var_filtered = savgol_filter(y_var, window_length=window_length,
                                   polyorder=polyorder, deriv=deriv,
                                   delta=delta, mode=mode, cval=cval)
    y_error = y_var - y_var_filtered
    # 其他功能区 -----------------------------------------------------
    if is_print_summary:
        print(y_var_filtered)

    if is_data_out:
        if not os.path.exists(data_outpath):
            os.makedirs(data_outpath, exist_ok=True)
        assert data_outfile is not None
        data = pd.DataFrame({'var_x': x_var, 'var_y': y_var,
                             'var_y_filtered': y_var_filtered})
        data.to_csv(data_outfile, index=False)

    if is_show_fig or is_fig_out or is_plot:
        # 绘图时显示中文。
        plt.rcParams['font.family'] = 'SimHei'
        plt.rcParams['axes.unicode_minus'] = False
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize,
                                       gridspec_kw={'width_ratios': [1, 1],
                                                    'wspace': 0.2,
                                                    'left': 0.05,
                                                    'right': 0.95})
        fig.suptitle(title)

        # 画图
        ax1.cla()
        ax1.scatter(x_var, y_var, s=s, marker=marker)
        ax1.plot(x_var, y_var_filtered)
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        fig_legend_other_text = ("Filter x:[{:.0f},{:.0f}]".format(x_var[0], x_var[-1]))
        handles, labels = ax1.get_legend_handles_labels()
        handles.append(mpatches.Patch(color='none', label=fig_legend_other_text))
        plt.rc('legend', fontsize=10)
        ax1.legend(loc='best', handles=handles)

        ax2.cla()
        ax2.plot(x_var, y_error)
        ax2.set_xlabel('X')
        ax2.set_ylabel('Y')
        fig_legend_other_text = ("Residual x:[{:.0f},{:.0f}]".format(x_var[0], x_var[-1]))
        handles, labels = ax2.get_legend_handles_labels()
        handles.append(mpatches.Patch(color='none', label=fig_legend_other_text))
        plt.rc('legend', fontsize=10)
        ax2.legend(loc='best', handles=handles)

    if is_fig_out:
        if not os.path.exists(fig_outpath):
            os.makedirs(fig_outpath, exist_ok=True)
        assert fig_outfile is not None
        plt.savefig(fig_outfile)

    if is_show_fig:
        plt.show()
    # --------------------------------------------------------------
    return y_var_filtered, y_var, x_var
# =========================================================================
