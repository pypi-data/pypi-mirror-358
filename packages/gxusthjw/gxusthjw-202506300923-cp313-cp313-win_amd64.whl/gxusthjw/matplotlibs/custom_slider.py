#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        custom_slider.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“表征`Slider与TextBox组合的部件`”的类。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/27     finish
# ------------------------------------------------------------------
# 导包 ============================================================
from typing import Optional

from matplotlib.widgets import Slider, TextBox

from .matplotlib_utils import import_mpl

# 声明 ============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining a class that represents a widget that 
combines 'Slider' and 'TextBox'.
"""

__all__ = [
    'SliderTextBox',
]


# 定义 ============================================================
class SliderTextBox(object):
    """
    类`SliderTextBox`表征“Slider与TextBox组合的部件”。
    """

    def __init__(self, ax, label: str, valmin: float, valmax: float,
                 valinit: float = 0.5, valstep: float = None,
                 textfmt: Optional[str] = "%.2g",
                 textbox_width: float = 0.05,
                 gap: float = 0.02, **kwargs):
        """
        类`SliderTextBox`的初始化方法。

        :param ax: 滑块部件的轴。
        :param label: 滑块部件的标签。
        :param valmin: 滑块的最小值。
        :param valmax: 滑块的最大值。
        :param valinit: 滑块的初始值。
        :param valstep: 滑块值得步长。
        :param textfmt: 文本框中显示的文本格式。
        :param textbox_width: 文本框的宽度。
        :param gap: 组合部件之间的间隙。
        :param kwargs: 传给滑块的可选关键字参数。
        """
        # 禁止指定'valfmt'和'orientation'
        # 因Slider组合部件不显示值，且必须是水平放置的。
        if 'valfmt' in kwargs or 'orientation' in kwargs:
            raise TypeError("'valfmt' and 'orientation' can not be"
                            " specified as keyword arguments.")
        self.__gap = gap
        self.__textbox_width = textbox_width
        if textfmt is None:
            self.__textfmt = "%.2g"
        else:
            self.__textfmt = textfmt
        self.__slider_ax = ax
        # 创建滑块。
        self.__slider = Slider(self.__slider_ax, label, valmin, valmax,
                               valinit=valinit, valstep=valstep,
                               orientation='horizontal',
                               **kwargs)
        # 这里禁止显示滑块的文本标签。
        self.__slider.valtext.set_visible(False)
        plt = import_mpl()
        # 获取滑块轴的尺寸
        left, bottom, width, height = ax.get_position().bounds
        # 创建文本框的轴
        self.__textbox_ax = plt.axes((left + width + self.__gap,
                                      bottom, textbox_width, height))
        # 创建文本框。
        self.__textbox = TextBox(self.__textbox_ax, label="",
                                 initial=self.__textfmt % self.__slider.val,
                                 textalignment='center')
        # 注册文本框的回调。
        self.__textbox.on_submit(lambda val: self.__slider.set_val(float(val)))

    def on_changed(self, func):
        """
        注册值变化的回调函数。

        :param func: 回调函数，当滑动块被改变时调用的函数，
                    该函数必须接受一个浮点数作为参数。
        """

        def func_wrapper(val):
            self.__textbox.set_val(self.__textfmt % val)
            func(val)

        self.__slider.on_changed(func_wrapper)

    def get_width(self):
        """
        获取组合部件的宽度。

        :return: 组合部件的宽度。
        """
        return (self.__slider_ax.get_width() +
                self.__textbox_ax.get_width() + self.__gap)
# =================================================================
