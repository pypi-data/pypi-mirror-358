#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        cross_hair_cursor.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义表征“十字线光标”的类。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/29     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import numpy as np
import matplotlib.pyplot as plt

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Define a class that represents a "cross-hair cursor".
"""

__all__ = [
    'TrackableDataCursor',
    'select_point_from',
]


# 定义 ==============================================================
class TrackableDataCursor:
    """
    类`TrackableDataCursor`表征一个“可跟踪数据点的十字线光标”。
    """

    def __init__(self, ax, line):
        """
        类`TrackableDataCursor`的初始化方法。

        :param ax: Matplotlib轴对象，用于绘制线条和文本。
        :param line: 十字光标要吸附的线。
        """
        # 存储传入的轴对象
        self.ax = ax

        if line.axes != ax or line not in ax.get_lines():
            raise ValueError('The line must belong to the provided axes (ax).')
        self.line = line

        # 绘制一条水平参考线，用于标示特定的y坐标值
        self.horizontal_line = ax.axhline(color='k', lw=0.8, ls='--')

        # 绘制一条垂直参考线，用于标示特定的x坐标值
        self.vertical_line = ax.axvline(color='k', lw=0.8, ls='--')

        self.x, self.y = line.get_data()

        self._last_index = None

        # 在坐标轴上定位文本，该文本在初始化时为空
        self.text = ax.text(0.72, 0.9, '', transform=ax.transAxes)

        self.__selected_x, self.__selected_y = None, None

        self.ax.figure.canvas.mpl_connect('motion_notify_event',
                                          self.on_mouse_move)
        self.ax.figure.canvas.mpl_connect('button_press_event',
                                          self.on_mouse_click)

    @property
    def selected_x(self):
        """
        获取当前所选数据的x坐标。

        :return: 当前所选数据的x坐标。
        """
        return self.__selected_x

    @property
    def selected_y(self):
        """
        获取当前所选数据的y坐标。

        :return: 当前所选数据的y坐标。
        """
        return self.__selected_y

    def set_cross_hair_visible(self, visible):
        """
        设置十字光标是否可见。

        该方法统一设置水平线、垂直线和文本标记的可见性，并判断是否需要重新绘制。

        :param visible: 指定十字光标是否可见。True 表示可见，False 表示不可见。
        :return: 返回是否需要重新绘制光标的值。如果可见性改变，则返回 True，否则返回 False。
        """
        # 判断水平线的可见性是否需要改变
        need_redraw = self.horizontal_line.get_visible() != visible
        # 设置水平线的可见性
        self.horizontal_line.set_visible(visible)
        # 设置垂直线的可见性
        self.vertical_line.set_visible(visible)
        # 设置文本标记的可见性
        self.text.set_visible(visible)
        # 返回是否需要重新绘制光标
        return need_redraw

    def on_mouse_move(self, event):
        """
        鼠标移动事件的处理函数，用于更新十字光标的位置和显示的坐标。

        当鼠标在绘图区域中移动时，此方法会被调用。它会根据鼠标的当前位置更新十字光标的位置，
        并在屏幕上显示当前坐标的文本信息。如果鼠标移出绘图区域，则隐藏十字光标。

        :param event: 包含鼠标移动事件信息的对象，例如鼠标的坐标。
        :return:
        """
        if not event.inaxes:
            self._last_index = None
            need_redraw = self.set_cross_hair_visible(False)
            if need_redraw:
                self.ax.figure.canvas.draw()
        else:
            self.set_cross_hair_visible(True)
            x, y = event.xdata, event.ydata
            # noinspection PyTypeChecker
            index = min(np.searchsorted(self.x, x), len(self.x) - 1)
            if index == self._last_index:
                return  # still on the same data point. Nothing to do.
            self._last_index = index
            x = self.x[index]
            y = self.y[index]

            # update the line positions
            self.horizontal_line.set_ydata([y])
            self.vertical_line.set_xdata([x])
            self.text.set_text(f'x={x:1.2f}, y={y:1.2f}')
            self.ax.figure.canvas.draw()

    def on_mouse_click(self, event):
        """
        鼠标点击事件的处理函数，用于捕获鼠标左键点击并输出坐标值。

        :param event: 包含鼠标点击事件信息的对象，包含按钮类型和坐标信息。
        """
        if event.inaxes and event.button == 1:  # button == 1 表示鼠标左键
            self.__selected_x, self.__selected_y = event.xdata, event.ydata
            print(f'x={self.__selected_x:1.2f}, y={self.__selected_y:1.2f}')


def select_point_from(x, y, **kwargs):
    """
    在一个单独的图形窗口中绘制给定的x和y数据点，并允许用户通过鼠标点击来选择一个数据点。

    :param x: 一维数组，表示数据点的x坐标。
    :param y: 一维数组，表示数据点的y坐标。
    :param kwargs: 可变关键字参数，用于自定义绘图的外观（例如，颜色、线型等）。
    :return: 返回用户选择的数据点的x和y坐标。
    """
    # 创建一个新的图形和子图
    fig, ax = plt.subplots()

    # 从kwargs中获取标题，如果没有提供则使用'Select Point'作为默认值
    title = kwargs.pop('title', 'Select Point')
    # 设置图形的标题
    ax.set_title(title)

    # 绘制数据点
    line = ax.plot(x, y, 'o', **kwargs)

    # 创建一个TrackableDataCursor实例，允许用户通过鼠标点击来选择数据点
    # noinspection PyUnresolvedReferences
    cursor = TrackableDataCursor(ax, line[0])

    # 显示图形
    plt.show()

    # 返回用户选择的数据点的坐标
    return cursor.selected_x, cursor.selected_y
