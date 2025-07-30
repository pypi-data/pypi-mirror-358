#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        spectrum.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“表征`谱数据`”的类。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/17     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import math

from typing import (
    Union, Optional
)

import numpy as np
import numpy.typing as npt

from ..commons import (
    Specimen,
    is_sorted_ascending_np,
    is_sorted_descending_np,
    Ordering,
)

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Define a class that represents `spectrum`.
"""

__all__ = [
    'Spectrum'
]


# 定义 ==============================================================
class Spectrum(Specimen):
    """
    类`Spectrum`表征“谱数据”。

        “谱数据”可包含3列数据，分别为：

            1. y：y坐标数据。

            2. x：x坐标数据。

            3. e：误差数据。

        其中，y坐标数据是必要的，而x坐标数据和误差数据（e）则可以没有。

            1. 如果x坐标数据没有，则使用有序整数列（从0开始）代替。

            2. 如果误差数据没有，则使用None代替。
    """

    def __init__(self, *args, **kwargs):
        """
        类`Spectrum`的初始化方法。

            对于可选参数args，存在如下几种情况：

                1. 当`len(args) == 0`时，抛出`ValueError`，确保args必须至少包含1个值。

                2. 当`len(args) == 1`时，`args[0]`被认为是y坐标数据。

                3. 当`len(args) == 2`时，`args[0]`被认为是y坐标数据，`args[1]`被认为是x坐标数据。

                4. 当`len(args) == 3`时，`args[0]`被认为是y坐标数据，`args[1]`被认为是x坐标数据，
                   `args[2]`被认为是误差数据e。

                5. 当`len(args) > 3`时，`args[0]`被认为是y坐标数据，`args[1]`被认为是x坐标数据，
                   `args[2]`被认为是误差数据e，其余参数全部传给父类`Specimen`。

        :param args: 可选参数，必须至少包含一个值。
        :param kwargs: 可选关键字参数。
        """
        # ----------------------------------------------------------
        args_len = len(args)
        if args_len == 0:
            raise ValueError("args must contain at least one value.")
        elif args_len == 1:
            self.__y = args[0]
            self.__x = None
            self.__e = None
            super(Spectrum, self).__init__(**kwargs)
        elif args_len == 2:
            self.__y = args[0]
            self.__x = args[1]
            self.__e = None
            super(Spectrum, self).__init__(**kwargs)
        elif args_len == 3:
            self.__y = args[0]
            self.__x = args[1]
            self.__e = args[2]
            super(Spectrum, self).__init__(**kwargs)
        else:
            self.__y = args[0]
            self.__x = args[1]
            self.__e = args[2]
            rest_args = args[3:]
            super(Spectrum, self).__init__(*rest_args, **kwargs)
        # ----------------------------------------------------------
        # 初始化数据y。
        self.__y = np.array(self.__y, copy=True)
        # 禁止修改y。
        self.__y.setflags(write=False)
        # 检查data_y是否是一维数组。
        if self.__y.ndim != 1:
            raise ValueError("y must be a one-dimensional array.")
        self.__len = self.__y.shape[0]
        # ----------------------------------------------------------
        # 初始化数据x。
        if self.__x is None:
            self.__x = np.arange(self.__len)
        else:
            self.__x = np.array(self.__x, copy=True)
        # 禁止修改x。
        self.__x.setflags(write=False)
        # 检查x是否是一维数组。
        if self.__x.ndim != 1:
            raise ValueError("x must be a one-dimensional array.")
        # 确保x与y数据的长度相同。
        if self.__len != self.__x.shape[0]:
            raise ValueError(
                "Expected the length of x and y is same, "
                "but got {{len(x) = {},len(y) = {}}}.".format(
                    self.__x.shape[0], self.__len)
            )
        # ----------------------------------------------------------
        # 保存误差数据。
        if self.__e is not None:
            self.__e = np.array(self.__e, copy=True)
            # 禁止修改e。
            self.__e.setflags(write=False)
            # 检查x是否是一维数组。
            if self.__e.ndim != 1:
                raise ValueError("e must be a one-dimensional array.")
            # 确保e与y数据的长度相同。
            if self.__len != self.__e.shape[0]:
                raise ValueError(
                    "Expected the length of e and y is same, "
                    "but got {{len(e) = {},len(y) = {}}}.".format(
                        self.__e.shape[0], self.__len
                    )
                )
        # ----------------------------------------------------------
        # 判断x坐标数据的有序性。
        if is_sorted_ascending_np(self.__x):
            # 升序。
            self.__x_sorted_type = Ordering.ASCENDING
        elif is_sorted_descending_np(self.__x):
            # 降序。
            self.__x_sorted_type = Ordering.DESCENDING
        else:
            # 无序。
            self.__x_sorted_type = Ordering.UNORDERED
        # ----------------------------------------------------------
        self.data_logger.log(self.__x, 'x')
        self.data_logger.log(self.__y, 'y')
        self.data_logger.log(self.__e, 'e')
        # ==========================================================

    @property
    def y(self) -> npt.NDArray[np.number]:
        """
        获取y坐标数据。

        :return: y坐标数据。
        """
        return self.__y

    @property
    def x(self) -> npt.NDArray[np.number]:
        """
        获取x坐标数据。

        :return: x坐标数据。
        """
        return self.__x

    @property
    def e(self) -> Optional[npt.NDArray[np.number]]:
        """
        获取误差数据。

        :return: 误差数据。
        """
        return self.__e

    @property
    def len(self) -> int:
        """
        获取数据的长度。

        :return: 数据的长度。
        """
        return self.__len

    def s(self, sigma=None) -> npt.NDArray[np.number]:
        """
        获取理论计算误差数据列，参考自：fityk—manual。

               sigma: 理论计算误差数据的计算方式。

               （1）如果sigma是数字（float或int），则将其填充至理论计算误差数据。

               （2）如果sigma是列表、元组或np.ndarray，则将其转换为np.ndarray，赋值给理论计算误差数据。

               （3）如果sigma是可调用对象（callable），则以y为参数，调用该可调用对象计算理论计算误差数据，
                  再将所得计算值填充至理论计算误差数据。

               （4）如果未指定sigma参数或sigma参数为None或sigma参数为忽略大小写的‘default’，
                  则根据y数据，计算 max(sqrt(abs(y)),1)值作为理论计算误差数据。

               （5）除上述四种情况外，其他参数值将抛出异常。

        :param sigma: 理论计算误差数据的计算方式。
        :return: 理论计算误差数据列。
        """
        if isinstance(sigma, (int, float)):
            __s = np.full_like(self.__y, sigma)
        elif isinstance(sigma, (list, tuple, np.ndarray)):
            __s = np.array(sigma, copy=True)
        elif callable(sigma):
            __s = np.array([sigma(yi) for yi in self.__y],
                           copy=True, dtype=np.float64)
        elif sigma is None or (isinstance(sigma, str) and sigma.lower() == 'default'):
            __s = np.array([max(math.sqrt(abs(yi)), 1) for yi in self.__y],
                           copy=True, dtype=np.float64)
        else:
            raise ValueError(
                "Expected sigma is one of {{int, float, callable, "
                "None, 'default'(case-Ignored)}}, "
                "but got {} ({}) type.".format(type(sigma), sigma))

        setattr(self, "s", __s)
        self.data_logger.log(__s, "s")
        return __s

    @property
    def err(self) -> Optional[npt.NDArray[np.number]]:
        """
        获取误差数据。

        :return: 误差数据。
        """
        # 理论计算权重数据，参考自：fityk—manual。
        if self.e is not None:
            __err = self.e
        elif hasattr(self, "s"):
            __err = self.s
        else:
            __err = None
        return __err

    def w(self, weight=None) -> npt.NDArray[np.number]:
        """
        获取理论计算权重数据。

            weight: 理论计算权重数据的计算方式。

            （1）如果weight是数字（float或int），则将其填充至理论计算权重数据。

            （2）如果weight是列表、元组或np.ndarray，则将其转换为np.ndarray，赋值给理论计算权重数据。

            （3）如果weight是可调用对象（callable），则以e为参数（如果e为None,则以s为参数），
                   调用该可调用对象计算理论计算权重数据，所得计算值作为理论计算权重数据。

            （4）如果未指定weight参数或weight参数为None或weight参数为忽略大小写的‘default’，
                  则根据e数据，计算 1.0 / e**2 （如果e为None，则计算1.0 / s**2）值作为
                  理论计算权重数据。

            （5）除上述四种情况外，其他参数值将抛出异常。

        :param weight: 理论计算权重数据的计算方式。
        :return: 理论计算权重数据。
        """
        if isinstance(weight, (int, float)):
            __w = np.full_like(self.__y, weight)
        elif isinstance(weight, (list, tuple, np.ndarray)):
            __w = np.array(weight, copy=True)
        elif callable(weight):
            if self.err is None:
                self.s()
            __w = np.array([weight(err_i) for err_i in self.err],
                           copy=True, dtype=np.float64)
        elif weight is None or (isinstance(weight, str) and
                                weight.lower() == 'default'):
            if self.err is None:
                self.s()
            __w = 1.0 / np.power(self.err, 2.0)
        else:
            raise ValueError(
                "Expected weight is one of {{int, float, callable, "
                "None, 'default'(case-Ignored)}}, "
                "but got {} ({}) type.".format(type(weight), weight))
        setattr(self, "w", __w)
        self.data_logger.log(__w, "w")
        return __w

    @property
    def x_sorted_type(self) -> Ordering:
        """
        获取x坐标数据的有序性，潜在的结果为：

           “ascending”，“descending”，“unordered”。

        :return: x坐标数据的有序性
        """
        return self.__x_sorted_type

    # -------------------------------------------------------------------------
    @property
    def x_start(self):
        """
        获取x坐标数据的第一个值。

        :return: x坐标数据的第一个值。
        """
        return self.x[0]

    @property
    def x_end(self):
        """
        获取x坐标数据的最后一个值。

        :return: x坐标数据的最后一个值。
        """
        return self.x[-1]

    @property
    def x_min(self):
        """
        获取x坐标数据的最小值。

        :return: x坐标数据的最小值。
        """
        return np.min(self.x)

    @property
    def x_max(self):
        """
        获取x坐标数据的最大值。

        :return: x坐标数据的最大值。
        """
        return np.max(self.x)

    @property
    def x_width(self):
        """
        获取x坐标数据的宽度。

        :return:x坐标数据的宽度。
        """
        return self.x_max - self.x_min

    @property
    def y_start(self):
        """
        获取y坐标数据的第一个值。

        :return: y坐标数据的第一个值。
        """
        return self.y[0]

    @property
    def y_end(self):
        """
        获取y坐标数据的最后一个值。

        :return: y坐标数据的最后一个值。
        """
        return self.y[-1]

    @property
    def y_min(self):
        """
        获取y坐标数据的最小值。

        :return: y坐标数据的最小值。
        """
        return np.min(self.y)

    @property
    def y_max(self):
        """
        获取y坐标数据的最大值。

        :return: y坐标数据的最大值。
        """
        return np.max(self.y)

    @property
    def y_height(self):
        """
        获取y坐标数据的高度。

        :return:y坐标数据的高度。
        """
        return self.y_max - self.y_min

    # noinspection PyTypeChecker
    @property
    def y_mean(self):
        """
        获取y坐标数据的均值。

        :return:y坐标数据的均值。
        """
        return np.mean(self.y)

    # noinspection PyTypeChecker
    @property
    def y_var0(self):
        """
        获取y坐标数据的总体方差。

        :return:y坐标数据的总体方差。
        """
        return np.var(self.y, ddof=0)

    # noinspection PyTypeChecker
    @property
    def y_var1(self):
        """
        获取y坐标数据的样本方差。

        :return:y坐标数据的样本方差。
        """
        return np.var(self.y, ddof=1)

    # noinspection PyTypeChecker
    @property
    def y_std0(self):
        """
        获取y坐标数据的总体均方差。

        :return:y坐标数据的总体均方差。
        """
        return np.std(self.y, ddof=0)

    # noinspection PyTypeChecker
    @property
    def y_std1(self):
        """
        获取y坐标数据的样本均方差。

        :return:y坐标数据的样本均方差。
        """
        return np.std(self.y, ddof=1)

    @property
    def y_exp(self):
        """
        获取y坐标数据的exp值。

        :return: y坐标数据的exp值。
        """
        return np.exp(self.y)

    @property
    def y_log(self):
        """
        获取y坐标数据的log值。

        :return: y坐标数据的log值。
        """
        return np.log(self.y)

    @property
    def y_sqrt(self):
        """
        获取y坐标数据的sqrt值。

        :return: y坐标数据的sqrt值。
        """
        return np.sqrt(self.y)

    @property
    def y_square(self):
        """
        获取y坐标数据的square值。

        :return: y坐标数据的square值。
        """
        return np.square(self.y)

    # ================================================================

    def y_normalize(self, lower: Union[int, float] = 0,
                    upper: Union[int, float] = 1):
        """
        将y坐标数据归一化至指定的区间内。

        :param lower: 区间下限。
        :param upper: 区间上限。
        :return: 归一化的y坐标数据。
        """
        if upper <= lower:
            raise ValueError(
                "Expected upper > lower, "
                "but got {lower=%f,upper=%f}" % (lower, upper)
            )

        k = (upper - lower) / self.y_height
        return lower + k * (self.y - self.y_min)

    @property
    def y_norm(self):
        """
        将y坐标数据归一化至[0,1]区间内。

        :return: 归一化的y坐标数据。
        """
        return self.y_normalize()

    @property
    def y_zscore0(self):
        """
        获取y坐标数据的Z-Score (总体)。

        :return:y坐标数据的Z-Score (总体)。
        """
        return (self.y - self.y_mean) / self.y_var0

    @property
    def y_zscore1(self):
        """
        获取y坐标数据的Z-Score (样本)。

        :return:y坐标数据的Z-Score (样本)。
        """
        return (self.y - self.y_mean) / self.y_var1

    # ================================================================

    def find_index_x(self, xi: Union[int, float]):
        """
        找到指定xi值在x中的索引。如果在x中没有找到与xi值相等值的索引，
        则返回以一个与xi值最接近值的索引，此时，存在3种情况：

            1. x为升序排列，则找到一个小于xi值的最大索引。

            2. x为降序排列，则找到一个大于xi值的最小索引。

            3. x为无序的，则找到所有与xi值相等的索引，可能返回空list。

        :param xi: 指定的xi值。
        :return: 索引。
        """
        # 帮我优化以下代码
        if self.x_sorted_type == Ordering.ASCENDING:
            if xi >= self.x_max:
                return self.len - 1
            if xi <= self.x_min:
                return 0
            res_a = 0
            for i in range(self.len):
                if self.x[i] <= xi:
                    res_a = i
                else:
                    break
            return res_a
        elif self.x_sorted_type == Ordering.DESCENDING:
            if xi <= self.x_max:
                return 0
            if xi >= self.x_min:
                return self.len - 1
            res_d = 0
            for j in range(self.len):
                if self.x[j] >= xi:
                    res_d = j
                else:
                    break
            return res_d
        else:
            res_u = list()
            for k in range(self.len):
                if self.x[k] == xi:
                    res_u = k
                else:
                    break
            return res_u

    def find_index_xrange(
            self,
            xi: Union[int, float],
            xj: Union[int, float]
    ):
        """
        找到指定xi和xj的索引。

        :param xi: 指定的xi。
        :param xj: 指定的xi。
        :return: xi的索引和xj索引组成的元组，其中小者在前，大者在后。
        """
        xi_index = self.find_index_x(xi)
        xj_index = self.find_index_x(xj)
        if self.x_sorted_type == Ordering.ASCENDING or \
                self.x_sorted_type == Ordering.DESCENDING:
            return (xi_index, xj_index) if xi_index <= xj_index else (xj_index, xi_index)
        else:
            res_set = set(xi_index) | set(xj_index)
            if len(res_set) <= 1:
                raise RuntimeError("index range unfounded.")
            return min(res_set), max(res_set)

    def find_x_peak(self, x_start: Union[int, float],
                    x_end: Union[int, float],
                    peak_type: Union[int, float] = 0):
        """
        找到指定区间内的最大值或最小值所对应的x坐标。

        :param x_start: 指定的波数1。
        :param x_end: 指定的波数2。
        :param peak_type: 0表示找到最大值，1表示找到最小值。
        :return: 最大值或最小值的x值和y值。
        """
        index_xi, index_xj = self.find_index_xrange(x_start, x_end)
        slice_x = self.x[index_xi:index_xj + 1]
        slice_y = self.y[index_xi:index_xj + 1]
        if peak_type == 0 or peak_type.__eq__('max'):
            __extreme_value = np.max(slice_y)
        else:
            __extreme_value = np.min(slice_y)
        r = np.where(np.diff(np.sign(slice_y - __extreme_value)) != 0)
        idx = r + (__extreme_value - slice_y[r]) / (slice_y[r + np.ones_like(r)] - slice_y[r])
        idx = np.append(idx, np.where(slice_y == __extreme_value))
        idx = np.sort(idx)
        return slice_x[int(np.round(idx)[0])], __extreme_value

    # ======================================================================
    def rebuild_kwargs(self):
        """
        再造kwargs参数。

        :return: dict，再造的kwargs。
        """
        raw_dic = self.data_logger.to_dict(orient='series')
        new_dic = {}
        for key, item in raw_dic.items():
            new_key = f"{key}_{self.sample_name}"
            new_item = item.dropna()
            if len(new_item) == 1:
                new_dic[new_key] = new_item[0]
            else:
                new_dic[new_key] = np.asarray(new_item)
        return new_dic

    def slice(self, xi: Union[int, float], xj: Union[int, float]):
        """
        从光谱数据中截取一个片段。

        :param xi: 指定的波数1。
        :param xj: 指定的波数2。
        :return: 截取到的片段。
        """
        index_xi, index_xj = self.find_index_xrange(xi, xj)
        slice_x = self.x[index_xi:index_xj + 1]
        slice_y = self.y[index_xi:index_xj + 1]
        if self.e is not None:
            slice_e = self.e[index_xi:index_xj + 1]
        else:
            slice_e = None
        return Spectrum(slice_y, slice_x, slice_e,
                        **self.rebuild_kwargs())

    # ======================================================================
    def horizontal_shift(self, shift_amount: Union[int, float]):
        """
        谱数据横向移动。

        :param shift_amount:移动量。
        :return: 移动后的数据。
        """
        new_x = self.x + shift_amount
        self.data_logger.log(new_x, f"x_shift_{shift_amount}")
        return Spectrum(self.y, new_x, self.e, **self.rebuild_kwargs())

    def vertical_shift(self, shift_amount: Union[int, float]):
        """
        谱数据纵向移动。

        :param shift_amount:移动量。
        :return: 移动后的数据。
        """
        new_y = self.__y + shift_amount
        self.data_logger.log(new_y, f"y_shift_{shift_amount}")
        return Spectrum(new_y, self.x, self.e, **self.rebuild_kwargs())
