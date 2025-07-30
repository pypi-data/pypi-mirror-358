#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        deriv_quasi_sech_fp.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      基于“拟双曲正割函数”，计算指定数据的指定阶（可以是任意阶）
#                   导数 - `全参数（full parameters）`版。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/10     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import os
from typing import Tuple
import math
import numpy as np
import numpy.typing as npt
import pandas as pd
from matplotlib import pyplot as plt

from scipy.fft import (ifft, fftshift, fft)

from .quasi_sech import quasi_sech
from .deriv_gl import deriv_gl
from ..statistics import FittingStatistics
# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Compute the specified-order (can be any order) derivative of 
the given data based on the 'quasi-hyperbolic secant function' 
—— `Full Parameters` version.
"""

__all__ = [
    'quasi_sech_ifft_fp',
    'deriv_quasi_sech_fp',
    'deriv_quasi_sech_fp_reviews',
]


# 定义 ==============================================================


def quasi_sech_ifft_fp(peak_width: float, peak_steepness: float, **kwargs) \
        -> Tuple[
            npt.NDArray[np.float64], npt.NDArray[np.float64],
            npt.NDArray[np.float64]
        ]:
    """
    生成“拟双曲正割函数”数据，并对其进行逆傅里叶变换，返回变换后的实数数据。

        可选关键字参数：

            1. r_arange: tuple, (start,stop,step),
                         用于生成“拟双曲正割函数”的自变量，生成方法如下：

                         `N = int((r_arange[1] - r_arange[0]) / r_arange[2]) + 1`

                         `r = np.linspace(r_arange[0], r_arange[1], N, endpoint=True, dtype=np.float64)`

            2. n_ifft: int,逆傅里叶变换变换所需的参数n。

            3. side_len: int,用于压制边波动的数据长度。

    此算法由广西科技大学“姚志湘”老师开发，对应matlab代码为：Sechpf.m

    :param peak_width: 拟双曲正割函数的参数peak_width，称为“峰宽”。
    :param peak_steepness: 拟双曲正割函数的参数peak_steepness，称为“峰陡峭度指数”。
    :param kwargs: 其他可选关键字参数。
    :return: tuple，(“拟双曲正割函数”经逆傅里叶变换后的实数数据，
            “拟双曲正割函数”数据，“拟双曲正割函数”的自变量)
    """
    # numpy.arange所需的参数。
    if 'r_arange' in kwargs and isinstance(kwargs['r_arange'], tuple):
        r_arange = kwargs['r_arange']
    else:
        r_arange = (0, 20, 0.0001)

    # 逆傅里叶变换变换所需的参数n，int类型。
    if 'n_ifft' in kwargs and isinstance(kwargs['n_ifft'], int):
        n_ifft = kwargs['n_ifft']
    else:
        n_ifft = 5000

    # 用于压制边波动参数，int类型。
    if 'side_len' in kwargs and isinstance(kwargs['side_len'], int):
        side_len = kwargs['side_len']
    else:
        side_len = 10

    with np.errstate(all='ignore'):
        # 自变量。
        n = int((r_arange[1] - r_arange[0]) / r_arange[2]) + 1
        r = np.linspace(r_arange[0], r_arange[1], n, endpoint=True, dtype=np.float64)

        # 计算“拟双曲正割函数”，sech((r*b)**p)
        igg = quasi_sech(r, peak_width, peak_steepness)

        # 执行傅里叶逆变换。
        yt = ifft(igg, n=n_ifft)
        tc = np.real(fftshift(yt))

        # 下边这行代码是为了压制边的波动。
        tc = tc - np.mean([tc[:side_len]])

        # 执行均一化。
        tc = tc / np.sum(tc)
        return tc, igg, r


def deriv_quasi_sech_fp(data_y: npt.ArrayLike, deriv_order: float,
                        peak_width: float, peak_steepness: float,
                        **kwargs) \
        -> Tuple[
            npt.NDArray[np.float64], npt.NDArray[np.float64],
            npt.NDArray[np.float64], npt.NDArray[np.float64],
            npt.NDArray[np.float64]
        ]:
    """
    基于“拟双曲正割函数”，计算指定数据（data_y）的指定阶（deriv_order）导数。

        可选关键字参数：

            1. r_arange: tuple, (start,stop,step),
                         用于生成“拟双曲正割函数”的自变量，生成方法如下：

                         `N = int((r_arange[1] - r_arange[0]) / r_arange[2]) + 1`

                         `r = np.linspace(r_arange[0], r_arange[1], n, endpoint=True, dtype=np.float64)`

            2. n_ifft: int,逆傅里叶变换变换所需的参数n。

            3. side_len: int,用于压制边波动的数据长度。

            4. y_side_len: y数据两端的扩展长度。

            5. deriv_slice_len: 导数数据两端的切去长度。

    此算法由广西科技大学“姚志湘”老师开发，对应matlab代码：SHf.m

    :param data_y: 原数据。
    :param deriv_order: 导数的阶。
    :param peak_width: 拟双曲正割函数的参数peak_width，称为“峰宽”。
    :param peak_steepness: 拟双曲正割函数的参数peak_steepness，称为“峰陡峭度指数”。
    :param kwargs: 其他可选关键字参数。
    :return: tuple，(导数数据，“拟双曲正割函数”经逆傅里叶变换后的实数数据的导数数据，
                    “拟双曲正割函数”经逆傅里叶变换后的实数数据，
                    “拟双曲正割函数”数据，“拟双曲正割函数”的自变量)
    """
    if 'y_side_len' in kwargs and isinstance(kwargs['y_side_len'], int):
        y_side_len = kwargs['y_side_len']
    else:
        y_side_len: int = 100

    if 'deriv_slice_len' in kwargs and isinstance(kwargs['deriv_slice_len'], int):
        deriv_slice_len: int = kwargs['deriv_slice_len']
    else:
        deriv_slice_len: int = 500

    y_arr = np.array(data_y, dtype=np.float64)
    mr = np.concatenate([y_arr[0] * np.ones(y_side_len),
                         y_arr, y_arr[-1] * np.ones(y_side_len)],
                        axis=0)
    sc0, igg, r = quasi_sech_ifft_fp(peak_width, peak_steepness, **kwargs)
    sc = deriv_gl(sc0, deriv_order)
    sc1 = sc[(deriv_slice_len + math.floor(deriv_order) - 1): (len(sc) - deriv_slice_len + 1)]

    # 注意：matlab的conv方法与numpy的convolve方法并不相同。
    npad = len(sc1) - 1
    s0 = np.convolve(mr, sc1, 'full')
    first = npad - npad // 2
    s0 = s0[first:first + len(mr)]
    s2 = s0[y_side_len:(y_side_len + len(y_arr))]
    s1 = s0[(y_side_len + 1):(y_side_len + len(y_arr) + 1)]
    s = ((deriv_order - math.floor(deriv_order / 2.0) * 2.0) * s1) / 2.0 + \
        ((-deriv_order + math.floor(deriv_order / 2.0) * 2.0 + 2.0) * s2) / 2.0

    return s, sc, sc0, igg, r


# noinspection PyTypeChecker
def deriv_quasi_sech_fp_reviews(data_y: npt.ArrayLike, deriv_order: float,
                             peak_width: float = 20, peak_steepness: float = 2,
                             data_x: npt.ArrayLike = None,
                             **kwargs) -> dict:
    """
    基于“拟双曲正割函数”，计算指定数据（data_y）的指定阶（deriv_order）导数。

    可选关键字参数：

            1. r_arange: tuple, (start,stop,step),
                         用于生成“拟双曲正割函数”的自变量，生成方法如下：

                         `N = int((r_arange[1] - r_arange[0]) / r_arange[2]) + 1`

                         `r = np.linspace(r_arange[0], r_arange[1], n, endpoint=True, dtype=np.float64)`

            2. n_ifft: int,逆傅里叶变换变换所需的参数n。

            3. side_len: int,用于压制边波动的数据长度。

            4. y_side_len: y数据两端的扩展长度。

            5. deriv_slice_len: 导数数据两端的切去长度。

            ---------------------------------------

            6. is_data_out：指示是否输出数据。

            7. data_outfile_name:指定输出数据的文件名。

            8. data_outpath：指定输出数据的路径。

            9. is_print_data：指定是否打印数据。

            10. is_plot: 指定是否绘图。

            11. is_fig_out：指定是否输出绘图。

            12. fig_outfile_name：指定输出绘图的文件名称。

            13. fig_outpath：指定输出绘图的路径。

            14. is_show_fig: 指定是否显示绘图。

            15. data_name: 数据名。

    :param data_y: 原数据。
    :param deriv_order: 导数的阶。
    :param peak_width: 拟正割函数的参数b，称为“峰宽”。
    :param peak_steepness: 拟正割函数的参数p，称为“峰陡峭度指数”。
    :param data_x: 与原数据y对应的x数据。
    :param kwargs: 其他关键字参数。
    :return: 数据字典。
    """
    data_y = np.array(data_y, dtype=np.float64, copy=True)

    if data_x is None:
        data_x = np.arange(len(data_y), dtype=np.int32)
    else:
        data_x = np.array(data_x, copy=True)

    t = deriv_quasi_sech_fp(data_y, 0, peak_width, peak_steepness, **kwargs)
    s = deriv_quasi_sech_fp(data_y, deriv_order, peak_width, peak_steepness, **kwargs)
    fs = FittingStatistics(data_y, t[0], x=data_x)
    # 数据输出 -----------------------------------------
    data_dict = {'x': data_x, 'y': data_y, 't': t[0], 's': s[0]}
    if 'is_data_out' in kwargs and kwargs['is_data_out']:
        t_data = pd.DataFrame({'x': data_x, 't': t[0]})
        # 准备数据。
        data = pd.DataFrame(data_dict)

        data_name = "data"
        if 'data_name' in kwargs:
            if kwargs['data_name'] is not None:
                data_name = kwargs['data_name']

        # 数据文件名。
        data_outfile_name = "{}_deriv_quasi_sech_{}_{}_{}".format(data_name,
                                                                  deriv_order, peak_width,
                                                                  peak_steepness)
        t_data_outfile_name = "{}_deriv_quasi_sech_{}_{}_{}_t".format(data_name,
                                                                      deriv_order, peak_width,
                                                                      peak_steepness)

        if 'data_outfile_name' in kwargs and kwargs['data_outfile_name'] is not None:
            data_outfile_name = kwargs['data_outfile_name']

        # 数据输出路径。
        data_outpath = os.path.abspath(os.path.dirname(__file__))
        if 'data_outpath' in kwargs and kwargs['data_outpath'] is not None:
            data_outpath = kwargs['data_outpath']

        if not os.path.exists(data_outpath):
            os.makedirs(data_outpath, exist_ok=True)

        data_outfile = os.path.join(
            data_outpath, "{}.csv".format(data_outfile_name))
        t_data.to_csv(os.path.join(
            data_outpath, "{}.csv".format(t_data_outfile_name)), index=False)
        data.to_csv(data_outfile, index=False)

        # print数据 ---------------------------------------
        if 'is_print_data' in kwargs and kwargs['is_print_data']:
            # 设置pandas显示所有列
            pd.set_option('display.max_columns', None)
            # 设置pandas显示所有行
            pd.set_option('display.max_rows', None)
            # 设置pandas显示所有字符
            pd.set_option('display.max_colwidth', None)
            print("data:\n{}".format(data))
        # ------------------------------------------------

    # 数据绘图 ---------------------------------------
    if 'is_plot' in kwargs and kwargs['is_plot']:
        # 绘图时显示中文。
        plt.rcParams['font.family'] = 'SimHei'
        plt.rcParams['axes.unicode_minus'] = False

        plt.subplot(2, 2, 1)
        plt.plot(data_x, data_y, label='Raw')
        plt.plot(data_x, t[0], label="Deriv 0")
        plt.title('RAW & 0-ORDER')
        plt.legend(loc='best')

        plt.subplot(2, 2, 2)
        plt.plot(data_x, s[0], label="Deriv {}".format(deriv_order))
        plt.title('RESULTS')
        plt.legend(loc='best')

        plt.subplot(2, 2, 3)
        plt.plot(data_x, data_y - t[0], label='T-Domain Residuals')
        plt.title('T-DOMAIN RESIDUALS')
        plt.legend(loc='best')

        plt.subplot(2, 2, 4)
        plt.plot(data_x, np.real(fftshift(fft(data_y - t[0]))),
                 label='F-Domain Residuals')
        plt.title('F-DOMAIN RESIDUALS')
        plt.legend(loc='best')
        plt.tight_layout()

        if 'is_fig_out' in kwargs and kwargs['is_fig_out']:
            data_name = "data"
            if 'data_name' in kwargs:
                if kwargs['data_name'] is not None:
                    data_name = kwargs['data_name']
            fig_outfile_name = "{}_deriv_quasi_sech_{}_{}_{}".format(
                data_name, deriv_order, peak_width, peak_steepness)

            if 'fig_outfile_name' in kwargs and kwargs['fig_outfile_name'] is not None:
                fig_outfile_name = kwargs['fig_outfile_name']

            fig_outpath = os.path.abspath(os.path.dirname(__file__))
            if 'fig_outpath' in kwargs and kwargs['fig_outpath'] is not None:
                fig_outpath = kwargs['fig_outpath']

            if not os.path.exists(fig_outpath):
                os.makedirs(fig_outpath, exist_ok=True)

            fig_outfile = os.path.join(
                fig_outpath, "{}.png".format(fig_outfile_name))
            plt.savefig(fig_outfile)

        if 'is_show_fig' in kwargs and kwargs['is_show_fig']:
            plt.show()

    data_dict['deriv_order'] = deriv_order
    data_dict['peak_width'] = peak_width
    data_dict['peak_steepness'] = peak_steepness
    data_dict['fitting_statistics'] = fs
    return data_dict