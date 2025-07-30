#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        data_2d_region_view_savgol_filters.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“表征`带可调视图区的
#                   二维数据区域Savgol滤波器`的类”。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2024/10/24     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
from typing import Optional, Tuple, override

from scipy.signal import savgol_filter

from ..commons import NumberSequence
from ..smoothers import Data2dRegionViewSmoother

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining a class that represents `the savgol filter with adjustable
 view for the region of two-dimensional data`.
"""

__all__ = ["Data2dRegionViewSavgolFilter"]


# 定义 ==============================================================
class Data2dRegionViewSavgolFilter(Data2dRegionViewSmoother):
    """
    类`Data2dRegionViewSavgolFilter`表征“带可调视图区的
      二维数据区域Savgol滤波器”。
    """

    def __init__(
        self,
        data_y: NumberSequence,
        data_x: Optional[NumberSequence] = None,
        region_start: Optional[int] = 0,
        region_length: Optional[int] = None,
        view_start: Optional[int] = 0,
        view_length: Optional[int] = None,
        *,
        window_length: int = 11,
        polyorder: int = 2,
        deriv: int = 0,
        delta: float = 1.0,
        mode: str = "interp",
        cval: float = 0.0,
    ):
        """
        类`Data2dRegionViewSavgolFilter`的初始化方法。

        :param data_y: 因变量（数据y）。
        :param data_x: 自变量（数据x,可选）。
        :param region_start: “滤波区域”的起始位置。
        :param region_length: “滤波区域”的长度。
        :param view_start: “滤波视图区域”的起始位置。
        :param view_length: “滤波视图区域”的长度。
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
        super(Data2dRegionViewSavgolFilter, self).__init__(
            data_y,
            data_x,
            region_start=region_start,
            region_length=region_length,
            view_start=view_start,
            view_length=view_length,
        )
        self.__window_length = window_length
        self.__polyorder = polyorder
        self.__deriv = deriv
        self.__delta = delta
        self.__mode = mode
        self.__cval = cval

    # ==============================================================

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
        self.view_start: int = kwargs.pop("view_start", self.view_start)
        self.view_length: int = kwargs.pop("view_length", self.view_length)
        self.window_length: int = kwargs.pop("window_length", self.window_length)
        self.polyorder: int = kwargs.pop("polyorder", self.polyorder)
        self.deriv: int = kwargs.pop("deriv", self.deriv)
        self.delta: float = kwargs.pop("delta", self.delta)
        self.mode: str = kwargs.pop("mode", self.mode)
        self.cval: float = kwargs.pop("cval", self.cval)
        # 执行平滑处理 --------------------------------------
        return self.do_smooth()

    # ---------------------------------------------------------
    @override
    def interactive_smooth(self, **kwargs):
        """
        交互式执行拟合。

        :param kwargs: 可选关键字参数。
        :return: 拟合后的数据。
        """
        pass
