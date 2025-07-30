#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        data_xy.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“表征`拥有XY两列数据的数据集`的类”。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/24     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
from typing import (
    Optional, Tuple, Iterator
)

import numpy as np
import numpy.typing as npt
import pandas as pd
import matplotlib.pyplot as plt

from .typings import (
    NumberSequence,
    Number,
    to_number_1darray
)

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defines a class that represents `a dataset with two columns (X and Y)`.
"""

__all__ = [
    'DataXY'
]


# 定义 ==============================================================

class DataXY(object):
    """
    类`DataXY`表征“拥有XY两列数据的数据集”。

        拥有XY两列数据的数据集拥有2列，分别被命名为：

            1. data_y: 一维数组，通常表征"因变量"数据。

            2. data_x: 一维数组，通常表征"自变量"数据，可选。
               当data_x被指定None时，采用`np.arange(len(data_y))`替换。

        注意：

            此类所表征的拥有XY两列数据的数据集可以是不对齐的，
            即两个数据列（data_y与data_x）的长度可以不相同。
    """

    def __init__(self, data_y: NumberSequence,
                 data_x: Optional[NumberSequence] = None):
        """
        类`DataXY`的初始化方法。

        :param data_y: 因变量（数据y）。
        :param data_x: 自变量（数据x,可选）。
        """
        # ----------------------------------------------------------
        # 初始化数据y。
        self.__data_y = to_number_1darray(data_y)
        # 禁止修改data_y。
        self.__data_y.setflags(write=False)
        self.__data_y_len = self.__data_y.shape[0]
        # ----------------------------------------------------------
        # 初始化数据x。
        # 注意：这里并不要求data_x长度与data_y长度一致。
        if data_x is None:
            self.__data_x = np.arange(self.__data_y_len)
        else:
            self.__data_x = to_number_1darray(data_x)
        # 禁止修改data_x。
        self.__data_x.setflags(write=False)
        self.__data_x_len = self.__data_x.shape[0]
        # ----------------------------------------------------------
        # 数据的长度取data_x和data_y中长度短的那个。
        if self.__data_x_len > self.__data_y_len:
            self.__data_len = self.__data_y_len
        else:
            self.__data_len = self.__data_x_len
        # ----------------------------------------------------------
        # 迭代索引。
        self.__iter_index = 0
        # ----------------------------------------------------------

    @property
    def data_y(self) -> npt.NDArray[np.number]:
        """
        返回因变量（数据y）。

        :return: 因变量（数据y）。
        """
        return self.__data_y

    @property
    def data_y_len(self) -> int:
        """
        返回因变量（数据y）的长度。

        :return: 因变量（数据y）的长度。
        """
        return self.__data_y_len

    @property
    def data_x(self) -> npt.NDArray[np.number]:
        """
        返回自变量（数据x）。

        :return: 自变量（数据x）。
        """
        return self.__data_x

    @property
    def data_x_len(self) -> int:
        """
        返回自变量（数据x）的长度。

        :return: 自变量（数据x）的长度。
        """
        return self.__data_x_len

    @property
    def data_len(self) -> int:
        """
        返回数据的长度。

            取因变量（数据y）和自变量（数据x）中长度短的那个长度。

        :return: 数据的长度。
        """
        return self.__data_len

    # -------------------------------------------------------------
    @property
    def data(self) -> pd.DataFrame:
        """
        返回数据。

        :return: 数据。
        """
        data_y_df = pd.DataFrame({"data_y": self.data_y})
        data_x_df = pd.DataFrame({"data_x": self.data_x})
        return pd.concat([data_y_df, data_x_df], axis=1)

    @property
    def exog(self) -> npt.NDArray[np.number]:
        """
        返回自变量（解释变量）。

            参考：
                在statsmodels库中，exog是“exogenous”的缩写，指的是外生变量。
                外生变量是指模型中的解释变量或独立变量（independent variables），
                它们被用来预测或解释内生变量（endogenous variable）的变化。
                在外生变量的选择上，我们假定这些变量不受模型内部因素的影响，
                而是由模型外部的因素决定的。

        :return: 自变量（解释变量）。
        """
        return self.data_x

    @property
    def endog(self) -> npt.NDArray[np.number]:
        """
        返回内生变量。

            参考：

                在statsmodels库中，endog是“endogenous”的缩写，指的是内生变量。
                内生变量是指模型中被解释的变量，也就是我们试图预测或解释的那个变量。
                在回归分析等统计建模过程中，内生变量通常是因变量（dependent variable），
                它依赖于一个或多个外生变量（exogenous variables）或
                独立变量（independent variables）。

        :return: 内生变量。
        """
        return self.data_y

    @property
    def is_aligned(self) -> bool:
        """
        判断数据是否为齐次的（即data_x与data_y是否等长）。

        :return: 如果data_x与data_y等长，返回True，否则返回False。
        """
        return self.data_x_len == self.data_y_len

    # -------------------------------------------------------------
    # noinspection PyTypeChecker
    def get_x(self, index: int) -> Optional[Number]:
        """
        获取指定索引处的x分量。

        :param index: 指定的索引。
        :return: 指定索引处的x分量。
        """
        if 0 <= index < self.data_x_len:
            return self.data_x[index]
        else:
            if self.data_x_len <= index < self.data_y_len:
                return None
            else:
                raise IndexError("Index out of range.")

    # noinspection PyTypeChecker
    def get_y(self, index: int) -> Optional[Number]:
        """
        获取指定索引处的y分量。

        :param index: 指定的索引。
        :return: 指定索引处的y分量。
        """
        if 0 <= index < self.data_y_len:
            return self.data_y[index]
        else:
            if self.data_y_len <= index < self.data_x_len:
                return None
            else:
                raise IndexError("Index out of range.")

    def get_xy(self, index: int) -> Tuple[Optional[Number], Optional[Number]]:
        """
        获取指定索引处的x和y分量。

        :param index: 指定的索引。
        :return: 指定索引处的(x,y)分量。
        """
        return self.get_x(index), self.get_y(index)

    # -------------------------------------------------------------
    def __len__(self) -> int:
        """
        返回数据的长度。

            取因变量（数据y）和自变量（数据x）中长度长的那个长度。

        :return: 数据的长度。
        """
        return self.data_x_len if self.data_x_len > self.data_y_len else self.data_y_len

    def __getitem__(self, index: int) -> Tuple[Optional[Number], Optional[Number]]:
        """
        通过索引获取数据点。

        :return: (xi,yi)。
        """
        return self.get_xy(index)

    # noinspection PyTypeChecker
    def __iter__(self) -> Iterator[Tuple[Optional[Number], Optional[Number]]]:
        """
        返回一个迭代器，用于遍历数据点。

        :return: 数据迭代器。
        """
        self.__iter_index = 0
        return self

    def __next__(self):
        """
        实现迭代器的__next__方法。

        :return: (xi,yi)。
        """
        if self.__iter_index < self.__len__():
            result = self.get_xy(self.__iter_index)
            self.__iter_index += 1
            return result
        else:
            raise StopIteration

    # -------------------------------------------------------------

    def __eq__(self, other):
        """
        比较与另一个对象的相等性。

        :param other: 另一个对象。
        :return: 相等返回True，否则返回False。
        """
        if not isinstance(other, DataXY):
            return False
        return np.array_equal(self.data_y, other.data_y) and \
            np.array_equal(self.data_x, other.data_x)

    def __ne__(self, other):
        """
        比较与另一个对象的不相等性。

        :param other: 另一个对象。
        :return: 不相等返回True，否则返回False。
        """
        return not self.__eq__(other)

    def __str__(self):
        """
        获取对象的字符串表示。

        :return: 对象的字符串表示。
        """
        return (
            f"DataXY(data_y={self.data_y.tolist()}, " f"data_x={self.data_x.tolist()})"
        )

    def __repr__(self):
        """
        获取对象的表示字符串。

        :return:对象的表示字符串。
        """
        return (
            f"DataXY(data_y=np.array({self.data_y.tolist()}), "
            f"data_x=np.array({self.data_x.tolist()}))"
        )

    def __hash__(self):
        """
        获取对象的hashcode码。

        :return: 对象的hashcode码。
        """
        return hash((tuple(self.data_y), tuple(self.data_x)))

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
            **kwargs,
        )
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        if label is not None:
            plt.legend(loc="best")
        plt.show()

    def span_select(self, **kwargs):
        """
        交互式的选取数据。

            说明：利用`matplotlib.widgets.SpanSelector`对数据进行交互式的选取，
                并生成新的DataXY对象。

        :param kwargs: 可选关键字参数，除“label”和“title”外，全部被传入plot方法。
        :return: 新的DataXY对象。
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

        select_x, select_y = x, y
        (line2,) = ax2.plot(select_x, select_y, color="blue")
        ax2.set_xlabel(xlabel)
        ax2.set_ylabel(ylabel)

        def onselect(xmin, xmax):
            nonlocal select_x, select_y
            nonlocal line2
            indmin, indmax = np.searchsorted(x, (xmin, xmax))
            indmax = min(len(x) - 1, indmax)

            select_x = x[indmin:indmax]
            select_y = y[indmin:indmax]

            if len(select_x) >= 2:
                line2.set_data(select_x, select_y)
                line2.set_color("red")
                # ax2.set_xlim(select_x[0], select_x[-1])
                # ax2.set_ylim(select_y.min(), select_y.max())
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
        return select_y, select_x

# ================================================================
