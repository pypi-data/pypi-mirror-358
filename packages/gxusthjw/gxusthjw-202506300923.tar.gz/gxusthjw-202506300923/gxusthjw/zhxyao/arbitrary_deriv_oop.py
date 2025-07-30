#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        arbitrary_deriv_oop.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      对带有噪音的谱数据进行任意阶求导。
#                   该算法最初由广西科技大学“姚志湘”老师开发，
#                   本代码是针对广西科技大学“姚志湘”老师开发算法
#                   的面向对象封装。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/15     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import os
import math
from abc import ABCMeta, abstractmethod
from typing import Optional, Tuple

import numpy as np
import numpy.typing as npt
from scipy.fft import fft, ifft, fftshift
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import threading
from ..statistics import FittingStatistics
from ..commons import DataTable

# 定义 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Perform arbitrary-order differentiation on spectral data with noise. 
This algorithm was originally developed by Professor Yao Zhixiang from 
Guangxi University of Science and Technology. 
This code is an object-oriented encapsulation of the algorithm 
developed by Professor Yao Zhixiang.
"""

__all__ = [
    'EnvelopeFunction',
    'QuasiSechEnvelope',
    'GeneralPeakEnvelope',
    'ArbitraryOrderDerivativeAlgorithm',
    'ArbitraryOrderDerivativeZhxyaoGl',
    'ArbitraryOrderDerivative',
]


# ==================================================================
class UnivariateFunction(metaclass=ABCMeta):
    """
    类`UnivariateFunction`表征”单变量函数“。

    继承此类的类的对象均可被视为"单变量函数"对象。
    """

    # 函数对象被创建的数量。
    __object_count = 0

    # 线程锁
    __count_lock = threading.Lock()

    def __init__(self, **kwargs):
        """
        类`UnivariateFunction`的初始化方法。

        :param kwargs: 可选关键字参数，这些参数将全部转换为对象的实例变量。
        """
        for key in kwargs:
            if not hasattr(self, key):
                setattr(self, key, kwargs[key])

        # 原子化增加对象计数
        cls = type(self)
        cls._increment_count()

        # 设置对象ID
        self.__object_id = cls.__object_count

    def __del__(self):
        """
        销毁对象（del object）时，此方法会被自动调用，
        借此，将对象计数减一。
        """
        try:
            cls = type(self)
            cls._decrement_count()
        except Exception as e:
            print(f"Error occurred during object destruction: {e}")

    @classmethod
    def _increment_count(cls):
        """
        类方法，用于增加当前对象的计数。

        该方法是类方法，因此它操作的是类变量而不是实例变量。
        使用锁来确保线程安全，在多线程环境下防止竞态条件。


        参数:
            - cls: 类本身，由@classmethod装饰器提供。

        :return: 无
        """
        # 使用类的锁来确保在多线程环境下对计数器的操作是线程安全的
        with cls.__count_lock:
            # 增加类的私有属性__object_count，用于记录对象的数量
            cls.__object_count += 1

    @classmethod
    def _decrement_count(cls):
        """
        类方法，用于减少当前对象的计数。

        该方法是类方法，因此它操作的是类变量而不是实例变量。
        使用锁来确保线程安全，在多线程环境下防止竞态条件。


        参数:
            - cls: 类本身，由@classmethod装饰器提供。

        :return: 无
        """
        # 使用类变量__count_lock来确保线程安全
        with cls.__count_lock:
            # 递减对象计数
            cls.__object_count -= 1

    @property
    def object_id(self):
        """
        获取对象的ID值。

        :return: 对象的ID值。
        """
        return self.__object_id

    @abstractmethod
    def values(self, x: npt.ArrayLike, *args, **kwargs) -> npt.NDArray:
        """
        计算函数的值。

        :param x: 自变量。
        :param args: 可选参数。
        :param kwargs: 可选关键字参数。
        :return: 函数值。
        """
        pass

    def __call__(self, x: npt.ArrayLike, *args, **kwargs) -> npt.NDArray:
        """
        重写__call__方法可使“对象调用”语法可用。

        :param x: 自变量。
        :param args: 可选参数。
        :param kwargs: 可选关键字参数。
        :return: 函数值。
        """
        return self.values(x, *args, **kwargs)

    def reviews(self, x: npt.ArrayLike, *args, **kwargs) -> \
            Tuple[npt.NDArray, npt.NDArray]:
        """
        审阅函数。

        可选关键字参数：

            1. is_data_out： bool，指示是否输出数据。

            2. data_outfile_name：str，数据输出文件名（不含扩展名）。

            3. data_outpath：str，数据输出文件路径（目录路径）。

            4. is_print_data： bool，指示是否print数据。

            5. is_plot：bool，指示是否绘图。

            6. label_text：str，数据绘图时的标签文本。

            7. is_fig_out： bool，指示是否输出绘图。

            8. fig_outfile_name：str，绘图输出文件名（不含扩展名）。

            9. fig_outpath：str，绘图输出文件路径（目录路径）。

            10. is_show_fig： bool，指示是否show绘图。

        :param x: 自变量。
        :param args: 可选参数。
        :param kwargs: 可选关键字参数。
        :return: tuple，(x,y)
        """
        # ------------------------------------------------
        if not isinstance(x, np.ndarray):
            x = np.asarray(x)
        y = self.values(x, *args, **kwargs)
        # ------------------------------------------------

        class_name = self.__class__.__name__
        # 数据输出 -----------------------------------------
        if 'is_data_out' in kwargs and kwargs['is_data_out']:
            # 准备数据。
            data = pd.DataFrame({'x': x, 'y': y})

            # 数据文件名。
            data_outfile_name = "{}_{}".format(class_name, self.object_id)
            if 'data_outfile_name' in kwargs and kwargs['data_outfile_name'] is not None:
                data_outfile_name = kwargs['data_outfile_name']

            # 数据输出路径。
            data_outpath = os.path.abspath(os.path.dirname(__file__))
            if 'data_outpath' in kwargs and kwargs['data_outpath'] is not None:
                data_outpath = kwargs['data_outpath']

            if not os.path.exists(data_outpath):
                os.makedirs(data_outpath, exist_ok=True)

            data_outfile = os.path.join(data_outpath, "{}.csv".format(data_outfile_name))
            data.to_csv(data_outfile, index=False)
        # ------------------------------------------------

        # print数据 ---------------------------------------
        if 'is_print_data' in kwargs and kwargs['is_print_data']:
            print("x:{}".format(x))
            print("y:{}".format(y))
        # ------------------------------------------------

        # 数据绘图 ---------------------------------------
        if 'is_plot' in kwargs and kwargs['is_plot']:
            # 绘图时显示中文。
            plt.rcParams['font.family'] = 'SimHei'
            plt.rcParams['axes.unicode_minus'] = False

            plt.figure(figsize=(8, 6))
            if 'label_text' in kwargs and kwargs['label_text'] is not None:
                label_text = kwargs['label_text']
            else:
                label_text = "{}: y~x".format(class_name)

            plt.plot(x, y, label=label_text)
            plt.xlabel('x')
            plt.ylabel('y')

            other_legend_text = "x:[{},{}]".format(min(x), max(x))
            ax = plt.gca()
            handles, labels = ax.get_legend_handles_labels()
            handles.append(mpatches.Patch(color='none', label=other_legend_text))
            plt.rc('legend', fontsize=12)
            plt.legend(loc='best', handles=handles)

            if 'is_fig_out' in kwargs and kwargs['is_fig_out']:
                fig_outfile_name = "{}_{}".format(class_name, self.object_id)
                if 'fig_outfile_name' in kwargs and kwargs['fig_outfile_name'] is not None:
                    fig_outfile_name = kwargs['fig_outfile_name']

                fig_outpath = os.path.abspath(os.path.dirname(__file__))
                if 'fig_outpath' in kwargs and kwargs['fig_outpath'] is not None:
                    fig_outpath = kwargs['fig_outpath']

                if not os.path.exists(fig_outpath):
                    os.makedirs(fig_outpath, exist_ok=True)

                fig_outfile = os.path.join(fig_outpath, "{}.png".format(fig_outfile_name))
                plt.savefig(fig_outfile)

            if 'is_show_fig' in kwargs and kwargs['is_show_fig']:
                plt.show()

        return x, y


# 定义包络函数 ------------------------------------------------------
class EnvelopeFunction(UnivariateFunction, metaclass=ABCMeta):
    """
    类`EnvelopeFunction`表征包络函数。
    """

    def __init__(self, **kwargs):
        """
        类`EnvelopeFunction`的初始化方法。

        :param kwargs: 可选关键字参数，这些参数将全部转换为实例变量。
        """
        super(EnvelopeFunction, self).__init__(**kwargs)


class QuasiSechEnvelope(EnvelopeFunction):
    """
    类`QuasiSechEnvelope`表征基于"拟双曲正割函数"的包络函数。
    """

    def __init__(self, peak_width: float = 20.0, peak_steepness: float = 1.0,
                 magnitude: float = 1.0, **kwargs):
        """
        类`QuasiSechEnvelope`的初始化方法。

        :param peak_width: 峰宽（width）。
        :param peak_steepness: 峰陡峭度指数（an index for peak steepness）。
        :param magnitude: 振幅（缩放倍数）。
        """
        # 默认值。
        self.peak_width = peak_width
        self.peak_steepness = peak_steepness
        self.magnitude = magnitude
        super(QuasiSechEnvelope, self).__init__(**kwargs)

    def values(self, x: npt.ArrayLike, *args, **kwargs) -> npt.NDArray:
        """
        计算函数的值。

            可选关键字参数：

                1. peak_width：峰宽（width）。

                2. peak_steepness：峰陡峭度指数（an index for peak steepness）。

                3. magnitude：振幅（缩放倍数）。

            可选关键字参数可覆盖可选参数。

        :param x: 自变量。
        :param args: 可选参数。第1个值为peak_width（若存在），
                             第2个值为peak_steepness（若存在），
                             第3个值为magnitude（若存在）。
                             其余值忽略。
        :param kwargs: 可选关键字参数。
        :return: 函数值。
        """
        b_arg = self.peak_width
        p_arg = self.peak_steepness
        magnitude_arg = self.magnitude

        if len(args) == 1:
            b_arg = args[0]
        elif len(args) == 2:
            b_arg = args[0]
            p_arg = args[1]
        elif len(args) >= 3:
            b_arg = args[0]
            p_arg = args[1]
            magnitude_arg = args[2]
        else:
            pass

        if 'peak_width' in kwargs:
            # noinspection PyBroadException
            try:
                b_arg = float(kwargs['peak_width'])
            except Exception:
                pass

        if 'peak_steepness' in kwargs:
            # noinspection PyBroadException
            try:
                p_arg = float(kwargs['peak_steepness'])
            except Exception:
                pass

        if 'magnitude' in kwargs:
            # noinspection PyBroadException
            try:
                magnitude_arg = float(kwargs['magnitude'])
            except Exception:
                pass

        with np.errstate(all='ignore'):
            xs = np.asarray(x)
            sech_arg = (xs * b_arg) ** p_arg
            res = magnitude_arg * (2.0 / (np.exp(sech_arg) + np.exp(-sech_arg)))

        return res


class GeneralPeakEnvelope(EnvelopeFunction):
    """
    类`GeneralPeakEnvelope`表征基于"常见峰函数"的包络函数。

        常见峰函数包括：

            1. 高斯函数。

            2. 洛伦茨函数。

            3. 高斯-洛伦茨复合函数。

        上述峰函数经傅里叶变换后，均具有统一的表达式：
            a * exp(-(b*x)**p)
    """

    def __init__(self, peak_width: float = 20.0,
                 peak_steepness: float = 1.0,
                 magnitude: float = 1.0,
                 **kwargs):
        """
        类`GeneralPeakEnvelope`的初始化方法。

        :param peak_width: 峰宽（width）。
        :param peak_steepness: 峰陡峭度指数（an index for peak steepness）。
        :param magnitude: 振幅（缩放倍数）。
        """
        # 默认值。
        self.peak_width = peak_width
        self.peak_steepness = peak_steepness
        self.magnitude = magnitude
        super(GeneralPeakEnvelope, self).__init__(**kwargs)

    def values(self, x: npt.ArrayLike, *args, **kwargs) -> npt.NDArray:
        """
        计算函数的值。

        :param x: 自变量。
        :param args: 可选参数。
        :param kwargs: 可选关键字参数。
        :return: 函数值。
        """
        b_arg = self.peak_width
        p_arg = self.peak_steepness
        magnitude_arg = self.magnitude

        if len(args) == 1:
            b_arg = args[0]
        elif len(args) == 2:
            b_arg = args[0]
            p_arg = args[1]
        elif len(args) >= 3:
            b_arg = args[0]
            p_arg = args[1]
            magnitude_arg = args[2]
        else:
            pass

        if 'peak_width' in kwargs:
            # noinspection PyBroadException
            try:
                b_arg = float(kwargs['peak_width'])
            except Exception:
                pass

        if 'peak_steepness' in kwargs:
            # noinspection PyBroadException
            try:
                p_arg = float(kwargs['peak_steepness'])
            except Exception:
                pass

        if 'magnitude' in kwargs:
            # noinspection PyBroadException
            try:
                magnitude_arg = float(kwargs['magnitude'])
            except Exception:
                pass

        with np.errstate(all='ignore'):
            xs = np.asarray(x)
            exp_arg = -(xs * b_arg) ** p_arg
            res = magnitude_arg * np.exp(exp_arg)

        return res


# -------------------------------------------------------------------

# 定义任意阶导数算法 ---------------------------------------------------
class ArbitraryOrderDerivativeAlgorithm(UnivariateFunction, metaclass=ABCMeta):
    """
    类`ArbitraryOrderDerivativeAlgorithm`表征"任意阶导数算法"。
    """

    def __init__(self, deriv_order: float = 0, **kwargs):
        """
        类`ArbitraryOrderDerivativeAlgorithm`的初始化方法。

        :param kwargs: 可选关键字参数，这些参数将全部转换为实例变量。
        """
        self.deriv_order = deriv_order
        super(ArbitraryOrderDerivativeAlgorithm, self).__init__(**kwargs)

    @abstractmethod
    def deriv(self, x: npt.ArrayLike, *args, **kwargs) -> npt.NDArray:
        """
        计算指定数据（x）的指定阶导数。

        :param x: 指定的要求导的数据。
        :param args: 可选参数。
        :param kwargs: 可选关键字参数。
        :return: 导数。
        """
        pass

    def values(self, x: npt.ArrayLike, *args, **kwargs) -> npt.NDArray:
        """
        计算函数的值。

        :param x: 自变量。
        :param args: 可选参数。
        :param kwargs: 可选关键字参数。
        :return: 函数值。
        """
        return self.deriv(x, *args, **kwargs)

    def reviews(self, y: npt.ArrayLike, *args, **kwargs):
        """
        审阅函数。

        可选关键字参数：

            1. is_data_out： bool，指示是否输出数据。

            2. data_outfile_name：str，数据输出文件名（不含扩展名）。

            3. data_outpath：str，数据输出文件路径（目录路径）。

            4. is_print_data： bool，指示是否print数据。

            5. is_plot：bool，指示是否绘图。

            6. label_text：str，数据绘图时的标签文本。

            7. is_fig_out： bool，指示是否输出绘图。

            8. fig_outfile_name：str，绘图输出文件名（不含扩展名）。

            9. fig_outpath：str，绘图输出文件路径（目录路径）。

            10. is_show_fig： bool，指示是否show绘图。

        :param y: 自变量。
        :param args: 可选参数。
        :param kwargs: 可选关键字参数。
        :return: tuple，(y,dy)
        """
        # ------------------------------------------------
        if not isinstance(y, np.ndarray):
            y = np.array(y)
        dy = self.deriv(y, *args, **kwargs)
        # ------------------------------------------------

        class_name = self.__class__.__name__
        # 数据输出 -----------------------------------------
        if 'is_data_out' in kwargs and kwargs['is_data_out']:
            # 准备数据。
            data = pd.DataFrame({'y': y, 'dy': dy})

            # 数据文件名。
            data_outfile_name = "{}_{}".format(class_name, self.object_id)
            if 'data_outfile_name' in kwargs and kwargs['data_outfile_name'] is not None:
                data_outfile_name = kwargs['data_outfile_name']

            # 数据输出路径。
            data_outpath = os.path.abspath(os.path.dirname(__file__))
            if 'data_outpath' in kwargs and kwargs['data_outpath'] is not None:
                data_outpath = kwargs['data_outpath']

            if not os.path.exists(data_outpath):
                os.makedirs(data_outpath, exist_ok=True)

            data_outfile = os.path.join(data_outpath, "{}.csv".format(data_outfile_name))
            data.to_csv(data_outfile, index=False)
        # ------------------------------------------------

        # print数据 ---------------------------------------
        if 'is_print_data' in kwargs and kwargs['is_print_data']:
            print("y:{}".format(y))
            print("dy:{}".format(dy))
        # ------------------------------------------------

        # 数据绘图 ---------------------------------------
        if 'is_plot' in kwargs and kwargs['is_plot']:
            # 绘图时显示中文。
            plt.rcParams['font.family'] = 'SimHei'
            plt.rcParams['axes.unicode_minus'] = False

            plt.figure(figsize=(8, 6))
            if 'label_text' in kwargs and kwargs['label_text'] is not None:
                label_text = kwargs['label_text']
            else:
                label_text = "{}: y~No.".format(class_name)

            plt.subplot(2, 1, 1)
            plt.plot(y, label=label_text)
            plt.xlabel('Serial number')
            plt.ylabel('y')

            plt.subplot(2, 1, 2)
            plt.plot(dy, label="{},Order={}".format(label_text, self.deriv_order))
            plt.xlabel('Serial number')
            plt.ylabel('dy')

            other_legend_text = "x:[{},{}]".format(min(y), max(y))
            ax = plt.gca()
            handles, labels = ax.get_legend_handles_labels()
            handles.append(mpatches.Patch(color='none', label=other_legend_text))
            plt.rc('legend')
            plt.legend(loc='best', handles=handles)

            if 'is_fig_out' in kwargs and kwargs['is_fig_out']:
                fig_outfile_name = "{}_{}".format(class_name, self.object_id)
                if 'fig_outfile_name' in kwargs and kwargs['fig_outfile_name'] is not None:
                    fig_outfile_name = kwargs['fig_outfile_name']

                fig_outpath = os.path.abspath(os.path.dirname(__file__))
                if 'fig_outpath' in kwargs and kwargs['fig_outpath'] is not None:
                    fig_outpath = kwargs['fig_outpath']

                if not os.path.exists(fig_outpath):
                    os.makedirs(fig_outpath, exist_ok=True)

                fig_outfile = os.path.join(fig_outpath, "{}.png".format(fig_outfile_name))
                plt.savefig(fig_outfile)

            if 'is_show_fig' in kwargs and kwargs['is_show_fig']:
                plt.show()

        return y, dy


class ArbitraryOrderDerivativeZhxyaoGl(ArbitraryOrderDerivativeAlgorithm):
    """
    类`ArbitraryOrderDerivativeZhxyaoGl`表征"姚志祥老师写的任意阶导数算法"，
        该算法基于格伦瓦尔德·莱特尼科夫（Grunwald-Letnikov,GL）定义。
    """

    def __init__(self, deriv_order: float = 0, **kwargs):
        """
        类`ArbitraryOrderDerivativeZhxyaoGl`的初始化方法。

        :param deriv_order: 导数的阶。
        """
        super(ArbitraryOrderDerivativeZhxyaoGl, self).__init__(deriv_order, **kwargs)

    def deriv(self, x: npt.ArrayLike, *args, **kwargs) -> npt.NDArray:
        """
        计算指定数据（x）的指定阶导数。

        可选关键字参数：

            1.deriv_order：导数的阶。

        :param x: 指定的要求导的数据。
        :param args: 可选参数。
        :param kwargs: 可选关键字参数。
        :return:
        """
        v_arg = self.deriv_order

        if len(args) >= 1:
            v_arg = args[0]

        if 'deriv_order' in kwargs:
            # noinspection PyBroadException
            try:
                v_arg = float(kwargs['deriv_order'])
            except Exception:
                pass

        xs = np.array(x, dtype=np.float64)
        qt = len(xs)
        gj = np.ones(qt, dtype=np.float64)
        res = np.zeros(qt, dtype=np.float64)
        for j in range(1, qt):
            gj[j] = gj[j - 1] * (1 - (v_arg + 1) / j)
        for j2 in range(qt):
            res[j2] = np.dot(gj[0:(j2 + 1)], xs[0:(j2 + 1)][::-1])
        return res


# -------------------------------------------------------------------
def envelope_ifft_oop(envelope: Optional[EnvelopeFunction] = None,
                      r_values: Optional[npt.ArrayLike] = None,
                      n_ifft: Optional[int] = None,
                      side_len: Optional[int] = None):
    """
    生成“包络函数”数据，并对其进行逆傅里叶变换，返回变换后的实数数据。

    :param envelope: 包络函数。
    :param r_values: 包络函数的自变量。
    :param n_ifft: int,逆傅里叶变换变换所需的参数n。
    :param side_len: int,用于压制边波动的数据长度。
    :return:tuple，(“拟双曲正割函数”经逆傅里叶变换后的实数数据，
            “拟双曲正割函数”数据，“拟双曲正割函数”的自变量)
    """
    if envelope is None:
        envelope = QuasiSechEnvelope()

    if r_values is None:
        r_arange = (0, 20, 0.0001)
        r_len = int((r_arange[1] - r_arange[0]) / r_arange[2]) + 1
        r_values = np.linspace(r_arange[0], r_arange[1], r_len,
                               endpoint=True, dtype=np.float64)
    else:
        r_values = np.array(r_values, dtype=np.float64)

    if n_ifft is None:
        n_ifft = 5000

    if side_len is None:
        side_len = 10

    with np.errstate(all='ignore'):
        igg = envelope(r_values)
        yt = ifft(igg, n=n_ifft)
        tc = np.real(fftshift(yt))
        # 主要是为了压制边的波动。
        tc = tc - np.mean([tc[:side_len]])
        tc = tc / np.sum(tc)

    return tc, igg, r_values


def arbitrary_deriv_oop(data_y: npt.ArrayLike, deriv_order: float,
                        envelope: Optional[EnvelopeFunction] = None,
                        deriv_alg: Optional[ArbitraryOrderDerivativeAlgorithm] = None,
                        r_values: Optional[npt.ArrayLike] = None,
                        n_ifft: Optional[int] = None,
                        side_len: Optional[int] = None,
                        y_side_len: Optional[int] = None,
                        deriv_slice_len: Optional[int] = None):
    """
    基于“指定的包络函数和指定的任意阶导数算法”，计算指定数据（data_y）的指定阶（deriv_order）导数。

    :param data_y: 要求的数据。
    :param envelope: 包络函数。
    :param deriv_alg: 导数算法。
    :param deriv_order: 导数的阶。
    :param r_values: 包络函数的自变量。
    :param n_ifft: int,逆傅里叶变换变换所需的参数n。
    :param side_len: int,用于压制边波动的数据长度。
    :param y_side_len: y数据两端的扩展长度。
    :param deriv_slice_len:导数数据两端的切去长度。
    :return: tuple，(导数数据，“拟双曲正割函数”经逆傅里叶变换后的实数数据的导数数据，
                    “拟双曲正割函数”经逆傅里叶变换后的实数数据，
                    “拟双曲正割函数”数据，“拟双曲正割函数”的自变量)
    """
    data_y = np.array(data_y, dtype=np.float64)

    if envelope is None:
        envelope = QuasiSechEnvelope()

    if deriv_alg is None:
        deriv_alg = ArbitraryOrderDerivativeZhxyaoGl()

    if y_side_len is None:
        y_side_len = 100

    if deriv_slice_len is None:
        deriv_slice_len = 500

    with np.errstate(all='ignore'):
        mr = np.concatenate([data_y[0] * np.ones(y_side_len),
                             data_y, data_y[-1] * np.ones(y_side_len)],
                            axis=0)
        sc0, igg, r_values = envelope_ifft_oop(envelope, r_values, n_ifft, side_len)
        sc = deriv_alg.deriv(sc0, deriv_order)
        sc1 = sc[(deriv_slice_len + math.floor(deriv_order) - 1): (len(sc) - deriv_slice_len + 1)]

        # 注意：matlab的conv方法与numpy的convolve方法并不相同。
        npad = len(sc1) - 1
        s0 = np.convolve(mr, sc1, 'full')
        first = npad - npad // 2
        s0 = s0[first:first + len(mr)]

        s2 = s0[y_side_len:(y_side_len + len(data_y))]
        s1 = s0[(y_side_len + 1):(y_side_len + len(data_y) + 1)]
        s = ((deriv_order - math.floor(deriv_order / 2.0) * 2.0) * s1) / 2.0 + \
            ((-deriv_order + math.floor(deriv_order / 2.0) * 2.0 + 2.0) * s2) / 2.0

    return s, sc, sc0, igg, r_values


class ArbitraryOrderDerivative(object):
    """
    类`ArbitraryOrderDerivativeSpectrum`用于计算“指定谱数据的任意阶导数”。
    """

    def __init__(self, envelope: Optional[EnvelopeFunction] = None,
                 deriv_alg: Optional[ArbitraryOrderDerivativeAlgorithm] = None,
                 **kwargs):
        """
        类`ArbitraryOrderDerivativeSpectrum`的初始化方法。

        :param envelope: 包络函数。
        :param deriv_alg: 任意阶导数的算法。
        :param kwargs: 可选关键字参数。
        """
        if envelope is None:
            self.envelope = QuasiSechEnvelope()
        else:
            self.envelope = envelope

        if deriv_alg is None:
            self.deriv_alg = ArbitraryOrderDerivativeZhxyaoGl()
        else:
            self.deriv_alg = deriv_alg

        for key in kwargs.keys():
            if hasattr(self, key):
                continue
            else:
                setattr(self, key, kwargs[key])

    def deriv(self, y: npt.ArrayLike, deriv_order: float = 0,
              x: Optional[npt.ArrayLike] = None, **kwargs):
        """
        计算指定谱数据的指定阶导数。

        :param y: 指定的谱数据。
        :param deriv_order: 导数的阶。
        :param x: 指定的谱数据所对应的x数据。
        :param kwargs: 可选关键字参数。
        :return: (s,tc,igg)
        """
        y = np.array(y, dtype=np.float64)
        y_len = len(y)
        if x is None:
            x = np.arange(y_len, dtype=np.int32)
        else:
            x = np.array(x)

        if y_len != len(x):
            raise ValueError(
                "Expected the len of x and y is same, "
                "but got {{len(x) = {},len(y) = {}}}.".format(
                    len(x), y_len)
            )

        if "envelope" in kwargs and isinstance(kwargs['envelope'],
                                               EnvelopeFunction):
            envelope = kwargs['envelope']
        elif self.envelope is not None:
            envelope = self.envelope
        else:
            raise ValueError("Expected a EnvelopeFunction object. but got none.")

        if "deriv_alg" in kwargs and isinstance(kwargs['deriv_alg'],
                                                ArbitraryOrderDerivativeAlgorithm):
            deriv_alg = kwargs['deriv_alg']
        elif self.deriv_alg is not None:
            deriv_alg = self.deriv_alg
        else:
            raise ValueError("Expected a ArbitraryOrderDerivativeAlgorithm object. but got none.")

        if 'r_values' in kwargs:
            r_values = kwargs['r_values']
        elif hasattr(self, 'r_values'):
            r_values = self.r_values
        else:
            r_values = None

        # 逆傅里叶变换变换所需的参数n，int类型。
        if 'n_ifft' in kwargs:
            n_ifft = kwargs['n_ifft']
        elif hasattr(self, 'n_ifft'):
            n_ifft = self.n_ifft
        else:
            n_ifft = None

        # 用于压制边波动参数，int类型。
        if 'side_len' in kwargs:
            side_len = kwargs['side_len']
        elif hasattr(self, 'side_len'):
            side_len = self.side_len
        else:
            side_len = None

        if 'y_side_len' in kwargs:
            y_side_len = kwargs['y_side_len']
        elif hasattr(self, 'y_side_len'):
            y_side_len = self.y_side_len
        else:
            y_side_len = None

        if 'deriv_slice_len' in kwargs:
            deriv_slice_len = kwargs['deriv_slice_len']
        elif hasattr(self, 'deriv_slice_len'):
            deriv_slice_len = self.deriv_slice_len
        else:
            deriv_slice_len = None

        t, t_deriv, t_envelope_ifft, t_envelope, t_r_values = arbitrary_deriv_oop(
            y, 0, envelope, deriv_alg,
            r_values, n_ifft, side_len, y_side_len,
            deriv_slice_len)
        s, s_deriv, s_envelope_ifft, s_envelope, s_r_values = arbitrary_deriv_oop(
            y, deriv_order, envelope, deriv_alg,
            r_values, n_ifft, side_len, y_side_len,
            deriv_slice_len)
        fs = FittingStatistics(y, t, x=x)
        data_table = DataTable(x, y, t, t_deriv, t_envelope_ifft, t_envelope, t_r_values,
                               s, s_deriv, s_envelope_ifft, s_envelope, s_r_values, fs,
                               item_names=('x', 'y', 't', 't_deriv', 't_envelope_ifft',
                                          't_envelope', 't_r_values', 's', 's_deriv',
                                          's_envelope_ifft', 's_envelope', 's_r_values', 'fs'))
        # 数据输出 -----------------------------------------
        class_name = self.__class__.__name__
        if 'is_data_out' in kwargs and kwargs['is_data_out']:
            # 准备数据。
            data = pd.DataFrame({'x': x, 'y': y, 's': s, 't': t})
            t_data = pd.DataFrame({'x': x, 't': t})
            s_data = pd.DataFrame({'x': x, 's': s})
            # 数据文件名。
            data_outfile_name = "{}_{}".format(class_name, deriv_order)
            if 'data_outfile_name' in kwargs and kwargs['data_outfile_name'] is not None:
                data_outfile_name = kwargs['data_outfile_name']

            # 数据输出路径。
            data_outpath = os.path.abspath(os.path.dirname(__file__))
            if 'data_outpath' in kwargs and kwargs['data_outpath'] is not None:
                data_outpath = kwargs['data_outpath']

            if not os.path.exists(data_outpath):
                os.makedirs(data_outpath, exist_ok=True)

            data_outfile = os.path.join(data_outpath, "{}.csv".format(data_outfile_name))
            t_data_outfile = os.path.join(data_outpath, "{}_t.csv".format(data_outfile_name))
            s_data_outfile = os.path.join(data_outpath, "{}_s.csv".format(data_outfile_name))
            data.to_csv(data_outfile, index=False)
            t_data.to_csv(t_data_outfile, index=False)
            s_data.to_csv(s_data_outfile, index=False)
        # ------------------------------------------------

        # print数据 ---------------------------------------
        if 'is_print_data' in kwargs and kwargs['is_print_data']:
            print("x:{}".format(x))
            print("y:{}".format(y))
            print("s:{}".format(s))
            print("t:{}".format(t))
        # ------------------------------------------------

        # 数据绘图 ---------------------------------------
        if 'is_plot' in kwargs and kwargs['is_plot']:
            # 绘图时显示中文。
            plt.rcParams['font.family'] = 'SimHei'
            plt.rcParams['axes.unicode_minus'] = False

            plt.figure(figsize=(8, 6))

            plt.subplot(2, 2, 1)
            plt.plot(x, y, label='Raw')
            plt.plot(x, t, label="Deriv 0")
            plt.title('RAW & 0-ORDER')
            plt.legend(loc='best')

            plt.subplot(2, 2, 2)
            plt.plot(x, s, label="Deriv {}".format(deriv_order))
            plt.title('RESULTS')
            plt.legend(loc='best')

            plt.subplot(2, 2, 3)
            plt.plot(x, y - t, label='T-Domain Residuals')
            plt.title('T-DOMAIN RESIDUALS')
            plt.legend(loc='best')

            plt.subplot(2, 2, 4)
            plt.plot(x, np.real(fftshift(fft(y - t))),
                     label='F-Domain Residuals')

            other_legend_text = "x:[{},{}]".format(min(y), max(y))
            ax = plt.gca()
            handles, labels = ax.get_legend_handles_labels()
            handles.append(mpatches.Patch(color='none', label=other_legend_text))
            plt.rc('legend', fontsize=12)
            plt.legend(loc='best', handles=handles)

            if 'is_fig_out' in kwargs and kwargs['is_fig_out']:
                fig_outfile_name = "{}_{}".format(class_name, deriv_order)
                if 'fig_outfile_name' in kwargs and kwargs['fig_outfile_name'] is not None:
                    fig_outfile_name = kwargs['fig_outfile_name']

                fig_outpath = os.path.abspath(os.path.dirname(__file__))
                if 'fig_outpath' in kwargs and kwargs['fig_outpath'] is not None:
                    fig_outpath = kwargs['fig_outpath']

                if not os.path.exists(fig_outpath):
                    os.makedirs(fig_outpath, exist_ok=True)

                fig_outfile = os.path.join(fig_outpath, "{}.png".format(fig_outfile_name))
                plt.savefig(fig_outfile)

            if 'is_show_fig' in kwargs and kwargs['is_show_fig']:
                plt.show()

        return data_table
