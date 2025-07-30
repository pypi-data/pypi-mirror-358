#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        sm_linear_fitters.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      基于`statsmodels`包提供的线性拟合方法，
#                   定义对指定数据执行线性拟合的函数。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2024/10/18     revise
#       Jiwei Huang        0.0.1         2024/10/22     finish
# ------------------------------------------------------------------
# 导包 ==============================================================
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from matplotlib.widgets import Slider, RadioButtons, Button, TextBox

from ..commons import NumberSequence, unique_string

from .sm_linear_fittings import linear_fitting_sm

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining the linear fitting functions to perform linear regression 
on the specified data using the method provided 
by the statsmodels library.
"""

__all__ = [
    "static_linear_fitting_sm",
    "interactive_linear_fitting_sm",
]


# 定义 ==============================================================
def static_linear_fitting_sm(y: NumberSequence, x: NumberSequence, **kwargs):
    """
    基于statsmodels提供的线性拟合方法（OLS或RLM）对指定的数据（y，x）执行拟合。

        要求：

            1. y为一维数值数组。

            2. x为一维数值数组。

        可选关键字参数：

            1. region_start：int，要拟合数据在原始数据上的起始索引。

            2. region_length：int，要拟合数据的长度。

            3. method: str，拟合方法。

            4. view_start：int，数据视图的起始索引。

            5. view_length：int，数据视图的长度。

            6. is_data_out: bool，指示是否输出拟合结果。

            7. data_outfile_name: str，输出数据文件的名称。

            8. data_outpath: str，数据输出路径。

            9. is_print_summary: bool，是否打印summary。

            10. is_plot: bool，指示是否绘图。

            11. is_fig_out: bool，指示是否输出图形。

            12. fig_outfile_name: str，图形输出文件名。

            13. fig_outpath: str，图形输出路径。

            14. is_show_fig: bool，指示是否显示绘图。

            15. title: str，图标题，默认值："Linear Fitting"

            16. figsize: Tuple[int,int]，图尺寸。默认值：(12, 8)

            17. s: int，滤波前数据的散点大小，缺省值：5。

            18. marker: str，滤波前数据的散点形状，缺省值：'o'。

    :param y: 因变量。
    :param x: 自变量。
    :param kwargs: 拟合所需关键字参数。
    :return: 拟合结果，...。
    """
    # 拟合数据准备 ---------------------------------------
    ys = np.asarray(y)
    ys_len = ys.shape[0]
    xs = np.asarray(x) if x is not None else np.arange(ys_len)
    xs_len = xs.shape[0]
    data_len = xs_len if ys_len > xs_len else ys_len
    # ------------------------------------------------
    # 解析可选关键字参数 ---------------------------------
    region_start: int = kwargs.pop("region_start", 0)
    region_length: int = kwargs.pop("region_length", data_len - region_start)
    method: str = kwargs.pop("method", "ols")
    view_start: int = kwargs.pop("view_start", 0)
    view_length: int = kwargs.pop("view_length", data_len - view_start)
    #  ------------------------------------------------
    is_data_out = kwargs.pop("is_data_out", False)
    data_outfile_name = kwargs.pop(
        "data_outfile_name", "LinearFittingSm_" + unique_string()
    )
    data_outpath = kwargs.pop("data_outpath", os.path.expanduser("~"))
    data_outfile = os.path.join(data_outpath, "{}.csv".format(data_outfile_name))
    # -----------------------------------------------------------
    is_print_summary = kwargs.pop("is_print_summary", False)
    # -----------------------------------------------------------
    is_plot = kwargs.pop("is_plot", False)
    is_fig_out = kwargs.pop("is_fig_out", False)
    fig_outfile_name = kwargs.pop(
        "fig_outfile_name", "LinearFitting{}_".format(method) + unique_string()
    )
    fig_outpath = kwargs.pop("fig_outpath", os.path.expanduser("~"))
    fig_outfile = os.path.join(fig_outpath, "{}.png".format(fig_outfile_name))
    is_show_fig = kwargs.pop("is_show_fig", False)
    title = kwargs.pop("title", "Linear Fitting {}".format(method))
    figsize = kwargs.pop("figsize", (15, 8))
    s = kwargs.pop("s", 5)
    marker = kwargs.pop("marker", "o")
    # 数据准备与拟合 -------------------------------------------------
    y_var = ys[region_start : region_start + region_length]
    x_var = xs[region_start : region_start + region_length]
    fitting_result = linear_fitting_sm(y_var, x_var, method=method)
    var_y_fitted = fitting_result.fittedvalues
    var_y_error = y_var - var_y_fitted
    # 其他功能区 -----------------------------------------------------
    if is_print_summary:
        print(fitting_result.summary())

    if is_data_out:
        if not os.path.exists(data_outpath):
            os.makedirs(data_outpath, exist_ok=True)
        assert data_outfile is not None
        data = pd.DataFrame(
            {"var_x": x_var, "var_y": y_var, "var_y_fitted": var_y_fitted}
        )
        data.to_csv(data_outfile, index=False)

    if is_show_fig or is_fig_out or is_plot:
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

        # 画图
        ax1.cla()
        ax1.scatter(x_var, y_var, color="blue", s=s, marker=marker)
        ax1.plot(x_var, var_y_fitted, color="red")
        ax1.set_xlabel("X")
        ax1.set_ylabel("Y")
        fig_legend_other_text = "Fitting x:[{:.0f},{:.0f}]".format(x_var[0], x_var[-1])
        handles, labels = ax1.get_legend_handles_labels()
        handles.append(mpatches.Patch(color="none", label=fig_legend_other_text))
        plt.rc("legend", fontsize=10)
        ax1.legend(loc="best", handles=handles)

        ax2.cla()
        ax2.plot(x_var, var_y_error)
        ax2.set_xlabel("X")
        ax2.set_ylabel("Y")
        fig_legend_other_text = "Residual x:[{:.0f},{:.0f}]".format(x_var[0], x_var[-1])
        handles, labels = ax2.get_legend_handles_labels()
        handles.append(mpatches.Patch(color="none", label=fig_legend_other_text))
        plt.rc("legend", fontsize=10)
        ax2.legend(loc="best", handles=handles)

        ax3.cla()
        view_x = xs[view_start : view_start + view_length]
        view_y = ys[view_start : view_start + view_length]
        ax3.scatter(view_x, view_y, s=s, marker=marker)
        ax3.plot(x_var, var_y_fitted)
        ax3.set_xlabel("X")
        ax3.set_ylabel("Y")
        fig_legend_other_text = "View x:[{:.0f},{:.0f}]".format(view_x[0], view_x[-1])
        handles, labels = ax3.get_legend_handles_labels()
        handles.append(mpatches.Patch(color="none", label=fig_legend_other_text))
        plt.rc("legend", fontsize=10)
        ax3.legend(loc="best", handles=handles)

    if is_fig_out:
        if not os.path.exists(fig_outpath):
            os.makedirs(fig_outpath, exist_ok=True)
        assert fig_outfile is not None
        plt.savefig(fig_outfile)

    if is_show_fig:
        plt.show()
    # --------------------------------------------------------------
    return var_y_fitted, y_var, x_var, fitting_result
    # ---------------------------------------------------------------


# ==================================================================


def interactive_linear_fitting_sm(y: NumberSequence, x: NumberSequence, **kwargs):
    """
    基于statsmodels提供的线性拟合方法（OLS或RLM）对指定的数据（y，x）执行拟合。

        要求：

            1. y为一维数值数组。

            2. x为一维数值数组。

        可选关键字参数：

            1. title: str，图标题。默认值："Linear Fitting"

            2. figsize: tuple，图形的尺寸。默认值：(15, 8)

            3. s: int，滤波前数据散点的大小，缺省值：5。

            4. marker: str，滤波前数据散点的形状，缺省值：'o'。

            5. region_start：int，要处理数据在原始数据上的起始索引。

            6. region_length：int，要处理数据的长度。

            7. method: str，拟合方法。

            8. view_start: int，数据视图的起始索引。

            9. view_length: int，数据视图的长度。

    :param y: 因变量。
    :param x: 自变量。
    :param kwargs: 可选关键字参数。
    :return: 拟合后的拟合区数据y，拟合区数据y，拟合区数据x，拟合结果。
    """
    # 拟合数据准备 ---------------------------------------
    ys = np.asarray(y)
    ys_len = ys.shape[0]
    xs = np.asarray(x) if x is not None else np.arange(ys_len)
    xs_len = xs.shape[0]
    data_len = xs_len if ys_len > xs_len else ys_len
    methods = ["ols", "rlm"]
    # ------------------------------------------------
    # 解析可选关键字参数 ---------------------------------
    default_region_start: int = kwargs.pop("region_start", 0)
    default_region_length: int = kwargs.pop(
        "region_length", data_len - default_region_start
    )
    default_method: str = kwargs.pop("method", "ols")
    default_view_start: int = kwargs.pop("view_start", 0)
    default_view_length: int = kwargs.pop("view_length", data_len - default_view_start)
    title = kwargs.pop("title", "Linear Fitting")
    figsize = kwargs.pop("figsize", (12, 8))
    s = kwargs.pop("s", 5)
    marker = kwargs.pop("marker", "o")
    save_path = kwargs.pop("save_path", os.path.expanduser("~"))
    save_file_name = kwargs.pop(
        "save_file", "LinearFittingSm_" + unique_string() + ".csv"
    )
    #  ------------------------------------------------
    # 定义交互参数 ------------------------------------------------
    region_start_selected: int = default_region_start
    region_length_selected: int = default_region_length
    method_selected: str = default_method
    view_start_selected: int = default_view_start
    view_length_selected: int = default_view_length
    # 过程变量 ----------------------------------------------------
    region_data_x = None
    region_data_y = None
    fitting_result = None
    region_data_y_fitted = None
    region_data_y_error = None
    # 初始化图形 ---------------------------------------------------
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
    plt.subplots_adjust(bottom=0.3)  # 底部留出空间

    # 定义更新函数 --------------------------------------------------
    def _update():
        nonlocal ax1
        nonlocal ax2
        nonlocal ax3
        nonlocal region_start_selected
        nonlocal region_length_selected
        nonlocal method_selected
        nonlocal view_start_selected
        nonlocal view_length_selected
        nonlocal region_data_x
        nonlocal region_data_y
        nonlocal fitting_result
        nonlocal region_data_y_fitted
        nonlocal region_data_y_error

        # 截取数据。
        region_data_y = ys[
            region_start_selected : region_start_selected + region_length_selected
        ]
        region_data_x = xs[
            region_start_selected : region_start_selected + region_length_selected
        ]
        # 计算数据。
        fitting_result = linear_fitting_sm(
            region_data_y, region_data_x, method=method_selected
        )
        region_data_y_fitted = fitting_result.fittedvalues
        region_data_y_error = region_data_y - region_data_y_fitted

        # 画图
        ax1.cla()
        ax1.scatter(region_data_x, region_data_y, color="blue", s=s, marker=marker)
        ax1.plot(region_data_x, region_data_y_fitted, color="red")
        ax1.set_xlabel("X")
        ax1.set_ylabel("Y")
        fig_legend_other_text = "Fitting x:[{:.0f},{:.0f}]".format(
            region_data_x[0], region_data_x[-1]
        )
        handles, labels = ax1.get_legend_handles_labels()
        handles.append(mpatches.Patch(color="none", label=fig_legend_other_text))
        plt.rc("legend", fontsize=10)
        ax1.legend(loc="best", handles=handles)

        ax2.cla()
        ax2.plot(region_data_x, region_data_y_error)
        ax2.set_xlabel("X")
        ax2.set_ylabel("Y")
        fig_legend_other_text = "Residual x:[{:.0f},{:.0f}]".format(
            region_data_x[0], region_data_x[-1]
        )
        handles, labels = ax2.get_legend_handles_labels()
        handles.append(mpatches.Patch(color="none", label=fig_legend_other_text))
        plt.rc("legend", fontsize=10)
        ax2.legend(loc="best", handles=handles)

        ax3.cla()
        view_x = xs[view_start_selected : view_start_selected + view_length_selected]
        view_y = ys[view_start_selected : view_start_selected + view_length_selected]
        ax3.scatter(view_x, view_y, s=s, marker=marker)
        ax3.plot(region_data_x, region_data_y_fitted)
        ax3.set_xlabel("X")
        ax3.set_ylabel("Y")
        fig_legend_other_text = "View x:[{:.0f},{:.0f}]".format(view_x[0], view_x[-1])
        handles, labels = ax3.get_legend_handles_labels()
        handles.append(mpatches.Patch(color="none", label=fig_legend_other_text))
        plt.rc("legend", fontsize=10)
        ax3.legend(loc="best", handles=handles)

    _update()

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
        valmax=data_len - 3,
        valinit=default_view_start,
        valstep=1,
    )

    view_length_slider = Slider(
        ax=view_length_slider_ax,
        label="View Length",
        valmin=0,
        valmax=data_len,
        valinit=default_view_length,
        valstep=1,
    )

    region_start_slider = Slider(
        ax=region_start_slider_ax,
        label="Region Start",
        valmin=0,
        valmax=data_len - 3,
        valinit=default_region_start,
        valstep=1,
    )

    region_length_slider = Slider(
        ax=region_length_slider_ax,
        label="Region Length",
        valmin=0,
        valmax=data_len,
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
        mode_radio_ax, methods, active=methods.index(default_method)
    )
    # 增加标签的字体大小
    for label in mode_radio.labels:
        label.set_fontsize(12)  # 设置字体大小为 12

    save_button = Button(save_button_ax, "Save")
    reset_button = Button(reset_button_ax, "Reset")

    # 窗口部件的事件 ----------------------------------------------
    def on_view_start_changed(val):
        nonlocal view_start_selected
        view_start_selected = int(val)
        view_start_text_box.set_val(str(view_start_selected))
        _update()

    view_start_slider.on_changed(on_view_start_changed)

    def on_view_length_changed(val):
        nonlocal view_length_selected
        view_length_selected = int(val)
        view_length_text_box.set_val(str(view_length_selected))
        _update()

    view_length_slider.on_changed(on_view_length_changed)

    # noinspection PyShadowingNames,DuplicatedCode
    def on_region_start_changed(val):
        nonlocal region_length_selected
        region_start_selected = int(val)
        region_start_text_box.set_val(str(region_start_selected))
        _update()

    region_start_slider.on_changed(on_region_start_changed)

    def on_region_length_changed(val):
        nonlocal region_length_selected
        region_length_selected = int(val)
        region_length_text_box.set_val(str(region_length_selected))
        _update()

    region_length_slider.on_changed(on_region_length_changed)

    def view_start_text_box_change(text):
        nonlocal view_start_selected
        view_start_selected = int(text)
        view_start_slider.set_val(view_start_selected)
        _update()

    view_start_text_box.on_submit(view_start_text_box_change)

    def view_length_text_box_change(text):
        nonlocal view_length_selected
        view_length_selected = int(text)
        view_length_slider.set_val(view_length_selected)
        _update()

    view_length_text_box.on_submit(view_length_text_box_change)

    def start_text_box_change(text):
        nonlocal region_start_selected
        region_start_selected = int(text)
        region_start_slider.set_val(region_start_selected)
        _update()

    region_start_text_box.on_submit(start_text_box_change)

    def length_text_box_change(text):
        nonlocal region_length_selected
        region_length_selected = int(text)
        region_length_slider.set_val(region_length_selected)
        _update()

    region_length_text_box.on_submit(length_text_box_change)

    def mode_change_option(val):
        nonlocal method_selected
        method_selected = val
        _update()

    mode_radio.on_clicked(mode_change_option)

    # noinspection PyUnusedLocal
    def on_save_button_change(val):
        nonlocal region_data_x, region_data_y, region_data_y_fitted
        nonlocal save_path, save_file_name
        if not os.path.exists(save_path):
            os.makedirs(save_path, exist_ok=True)
        data_outfile = os.path.abspath(os.path.join(save_path, save_file_name))
        assert data_outfile is not None
        # noinspection PyUnresolvedReferences
        data = pd.DataFrame(
            {
                "region_data_x": region_data_x,
                "region_data_y": region_data_y,
                "var_y_filtered": region_data_y_fitted,
            }
        )
        data.to_csv(data_outfile, index=False)

    save_button.on_clicked(on_save_button_change)

    # noinspection PyUnusedLocal
    def on_reset_button_change(val):
        nonlocal default_view_start
        nonlocal default_view_length
        nonlocal default_region_start
        nonlocal default_region_length
        nonlocal default_method
        nonlocal view_start_selected
        nonlocal view_length_selected
        nonlocal region_start_selected
        nonlocal region_length_selected
        nonlocal method_selected
        # ----------------------------------------------------------
        view_start_selected = default_view_start
        view_length_selected = default_view_length
        region_start_selected = default_region_start
        region_length_selected = default_region_length
        method_selected = default_method
        # ----------------------------------------------------------
        view_start_slider.set_val(view_start_selected)
        view_length_slider.set_val(view_length_selected)
        region_start_slider.set_val(region_start_selected)
        region_length_slider.set_val(region_length_selected)
        # ----------------------------------------------------------
        view_start_text_box.set_val(str(view_start_selected))
        view_length_text_box.set_val(str(view_length_selected))
        region_start_text_box.set_val(str(region_start_selected))
        region_length_text_box.set_val(str(region_length_selected))
        # ----------------------------------------------------------
        mode_radio.set_active(methods.index(default_method))
        # ----------------------------------------------------------
        _update()

    reset_button.on_clicked(on_reset_button_change)
    # ---------------------------------------------------------------
    plt.show()
    # noinspection PyUnresolvedReferences
    return region_data_y_fitted, region_data_y, region_data_x, fitting_result
    # ---------------------------------------------------------------


# ============================================================
