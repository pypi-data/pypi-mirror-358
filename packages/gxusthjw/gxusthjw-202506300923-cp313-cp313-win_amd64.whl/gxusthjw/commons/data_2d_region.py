#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        data_2d_region.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“表征`二维数据区域`的类”。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2024/10/28     finish
# ------------------------------------------------------------------
# 导包 ==============================================================
from typing import Optional

import numpy as np
import numpy.typing as npt
import matplotlib.pyplot as plt

from .typings import NumberSequence

from .data_2d import Data2d

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining a class that represents `the region of two-dimensional data`.
"""

__all__ = [
    "Data2dRegion",
]


# 定义 ============================================================
class Data2dRegion(Data2d):
    """
    类`Data2dRegion`表征“二维数据区域”。

        二维数据拥有2列，分别被命名为：

            1. data_y: 一维数组，通常表征"因变量"数据。

            2. data_x: 一维数组，通常表征"自变量"数据，可选。
                当data_x被指定None时，采用`np.arange(len(data_y))`替换。

        相对于`Data2d`，类`Data2dRegion`添加了如下属性：

            1. region_start：表征“数据区域”在原数据中的起始索引位置。

            2. region_length：表征“数据区域”的长度。

        注意：

            原数据可能是不等长的，但原数据上的“数据区域”必须等长。
    """

    def __init__(
        self,
        data_y: NumberSequence,
        data_x: Optional[NumberSequence] = None,
        region_start: int = 0,
        region_length: Optional[int] = None,
    ):
        """
        类`Data2dRegion`的初始化方法。

        :param data_y: 因变量（数据y）。
        :param data_x: 自变量（数据x,可选）。
        :param region_start: “数据区域”的起始索引位置，默认值为0。
        :param region_length: “数据区域”的长度，默认值为`data_len - region_start`。
        """
        super(Data2dRegion, self).__init__(data_y, data_x)
        # ------------------------------------------------------------------
        self.__region_start = region_start
        if region_length is not None:
            self.__region_length = region_length
        else:
            self.__region_length = self.data_len - region_start
        # 检查数据。
        self.region_weak_check()
        # -------------------------------------------------------------------
        self.__is_parameter_changed = False
        # 初始化结束 ----------------------------------------------------------

    # -------------------------------------------------------------
    def region_weak_check(self):
        """
        检查“数据区域”参数的合法性。

            注意，此方法所实现的检查并不完整。
        """
        if (
            self.__region_start < 0
            or self.__region_length < 0
            or self.__region_start >= self.data_len
        ):
            raise ValueError("The region_start or region_length is invalid.")

    # -------------------------------------------------------------
    @property
    def region_start(self) -> int:
        """
        返回“数据区域”的起始索引位置。

        :return: “数据区域”的起始索引位置。
        """
        return self.__region_start

    @region_start.setter
    def region_start(self, region_start: int):
        """
        设置“数据区域”的起始索引位置。

            注意：最好只在此类或此类的子类中调用。

        :param region_start: “数据区域”的起始索引位置。
        """
        if region_start != self.region_start:
            self.__region_start = region_start
            self.__is_parameter_changed = True

    @property
    def region_length(self) -> int:
        """
        返回“数据区域”的长度。

        :return: “数据区域”的长度。
        """
        return self.__region_length

    @region_length.setter
    def region_length(self, region_length: int):
        """
        设置“数据区域”的长度。

            注意：最好只在此类或此类的子类中调用。

        :param region_length: “数据区域”的长度。
        """
        if region_length != self.region_length:
            self.__region_length = region_length
            self.__is_parameter_changed = True

    @property
    def is_parameter_changed(self) -> bool:
        """
        指示参数是否被改变。

        :return: 如果参数有被改变，返回True，否则返回False。
        """
        return self.__is_parameter_changed

    @is_parameter_changed.setter
    def is_parameter_changed(self, is_parameter_changed: bool):
        """
        设置参数是否被改变的标志。

            注意：最好只在此类或此类的子类中调用。

        :param is_parameter_changed: 参数是否被改变的标志，
                                     参数有被改变，则为True，否则为False。
        """
        if is_parameter_changed != self.is_parameter_changed:
            self.__is_parameter_changed = is_parameter_changed

    # -------------------------------------------------------------
    @property
    def region_stop(self) -> int:
        """
        返回“数据区域”的终止位置（不包含）。

        :return: “数据区域”的终止位置（不包含）。
        """
        return self.region_start + self.region_length

    @property
    def region_slice(self) -> slice:
        """
        返回“数据区域”的slice对象。

            slice对象的创建方式：

                1. slice(stop)

                2. slice(start, stop[, step])

        :return: “数据区域”的slice对象。
        """
        return slice(self.region_start, self.region_stop, 1)

    @region_slice.setter
    def region_slice(self, region_slice: slice):
        """
        设置“数据区域”的slice对象。

            注意：

                1. 创建slice对象时，如果不指定start，则start缺省为None，而非1。

                2. 创建slice对象时，如果不指定step，则step缺省为None，而非1。

                3. start,stop,step 都有可能是None

                4. 最好只在此类或此类的子类中调用。

        :param region_slice: “数据区域”的slice对象。
        """
        if region_slice.step in (None, 1):
            self.region_start = (
                region_slice.start if region_slice.start is not None else 0
            )
            stop = (
                region_slice.stop if region_slice.stop is not None else self.region_stop
            )
            self.region_length = stop - self.region_start
        else:
            raise ValueError(
                "Expected region_slice.step is None or region_slice.step == 1."
            )

    def set_region_slice(self, start: int, length: int):
        """
        设置“数据区域”的起始索引和长度。

            注意：最好只在此类或此类的子类中调用。

        :param start: “数据区域”的起始索引。
        :param length: “数据区域”的长度。
        """
        self.region_start = start
        self.region_length = length

    @property
    def region_data_y(self) -> npt.NDArray:
        """
        返回“数据区域”的数据y。

        :return: “数据区域”的数据y。
        """
        return self.data_y[self.region_slice]

    @property
    def region_data_x(self) -> npt.NDArray:
        """
        返回“数据区域”的数据x。

        :return: “数据区域”的数据x。
        """
        return self.data_x[self.region_slice]

    @property
    def region_data_len(self) -> int:
        """
        返回"数据区域"数据的长度。

            注意：

                1. self.region_data_len有可能不等于self.region_length。

                2. 理论上，self.region_data_len <= self.region_length。

        :return: "数据区域"数据的长度。
        """
        self.region_data_check()
        return self.region_data_y.shape[0]

    @property
    def region_data_stop(self) -> int:
        """
        返回"数据区域"数据在原始数据上的实际终止索引。

        :return: "数据区域"数据在原始数据上的实际终止索引。
        """
        return self.region_start + self.region_data_len

    def region_data_check(self):
        """
        检查"数据区域"数据是否具有相同的长度。

            如果不具有相同的长度，则抛出ValueError异常。
        """
        if self.region_data_x.shape != self.region_data_y.shape:
            raise ValueError("Expected region_data_x.shape == region_data_y.shape.")

    @property
    def is_region_data_aligned(self) -> bool:
        """
        判断"数据区域"的数据是否具有相同的长度。

        :return: 如果具有相同的长度，返回True，否则返回False。
        """
        return self.region_data_x.shape == self.region_data_y.shape

    # -------------------------------------------------------------
    def view(self, **kwargs):
        """
        数据视图。

        :param kwargs: 可选关键字参数，除“label”外，全部被传入plot方法。
        :return: None
        """
        label = kwargs.pop("label", None)
        xlabel = kwargs.pop("xlabel", "data_x")
        ylabel = kwargs.pop("ylabel", "data_y")
        plt.plot(
            self.data_x[: self.data_len],
            self.data_y[: self.data_len],
            label=label,
            **kwargs
        )
        plt.scatter(self.region_data_x, self.region_data_y, label="Region", color="red")
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        if label is not None:
            plt.legend(loc="best")
        plt.show()

    def span_select(self, **kwargs):
        """
        交互式的选取数据。

            说明：利用`matplotlib.widgets.SpanSelector`对数据进行交互式的选取，
                并生成新的Data2d对象。

        :param kwargs: 可选关键字参数，除“label”和“title”外，全部被传入plot方法。
        :return: 新的Data2d对象。
        """
        # ------------------------------------------------------------
        from matplotlib.widgets import SpanSelector

        # ------------------------------------------------------------
        x, y = self.data_x[: self.data_len], self.data_y[: self.data_len]
        # ------------------------------------------------------------
        label = kwargs.pop("label", None)
        title = kwargs.pop(
            "title",
            "Press left mouse button and drag"
            " to select a region in the top"
            " graph",
        )
        figsize = kwargs.pop("figsize", (8, 6))
        hspace = kwargs.pop("hspace", 0.4)
        xlabel = kwargs.pop("xlabel", "data_x")
        ylabel = kwargs.pop("ylabel", "data_y")
        # ------------------------------------------------------------
        fig, (ax1, ax2) = plt.subplots(
            2, figsize=figsize, gridspec_kw={"hspace": hspace}
        )

        ax1.plot(x, y, label=label, **kwargs)
        ax1.set_xlabel(xlabel)
        ax1.set_ylabel(ylabel)
        if label is not None:
            ax1.legend(loc="best")
        ax1.set_title(title)

        (line2,) = ax2.plot(self.region_data_x, self.region_data_y, color="blue")
        ax2.set_xlabel(xlabel)
        ax2.set_ylabel(ylabel)

        def onselect(xmin, xmax):
            nonlocal line2
            indmin, indmax = np.searchsorted(x, (xmin, xmax))
            indmax = min(len(x) - 1, indmax)

            self.region_start = indmin
            self.region_length = indmax - indmin

            if len(self.region_data_x) >= 2:
                line2.set_data(self.region_data_x, self.region_data_y)
                line2.set_color("red")
                # ax2.set_xlim(self.region_data_x[0], self.region_data_x[-1])
                # ax2.set_ylim(self.region_data_y.min(), self.region_data_y.max())
                fig.canvas.draw_idle()

        # noinspection PyUnusedLocal
        span = SpanSelector(
            ax1,
            onselect,
            "horizontal",
            useblit=True,
            props=dict(alpha=0.5, facecolor="tab:blue"),
            interactive=True,
            drag_from_anywhere=True,
        )
        # Set useblit=True on most backends for enhanced performance.
        plt.show()
        return self.region_data_y, self.region_data_x


# =====================================================================
