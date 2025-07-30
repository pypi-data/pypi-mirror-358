#!/usr/bin/env python3
# --*-- coding: utf-8 --*--
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        ampd_algorithm.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      寻峰算法。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2023/11/08     revise
#       Jiwei Huang        0.0.1         2024/06/28     finish
# ------------------------------------------------------------------
# 导包 ==============================================================
import numpy as np
import numpy.typing as npt

# 定义 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining helper methods and classes for peak detection.
"""

__all__ = [
    'ampd',
    'ampd_wangjy',
]


# =================================================================
def ampd_wangjy(data):
    """
    基于多尺度的自动峰值检测（automatic multiscale-based peak detection）。
    代码拷贝自：https://zhuanlan.zhihu.com/p/549588865
    参考文献：An Efficient Algorithm for Automatic Peak Detection in Noisy Periodic and Quasi-Periodic Signals

    :param data: 1-D numpy.ndarray。
    :return:波峰所在索引值的数组。
    :rtype: np.ndarray
    """
    p_data = np.zeros_like(data, dtype=np.int32)
    count = data.shape[0]
    arr_row_sum = []
    for k in range(1, count // 2 + 1):
        row_sum = 0
        for i in range(k, count - k):
            if data[i] > data[i - k] and data[i] > data[i + k]:
                row_sum -= 1
        arr_row_sum.append(row_sum)
    min_index = np.argmin(arr_row_sum)
    max_window_length = min_index
    for k in range(1, max_window_length + 1):
        for i in range(k, count - k):
            if data[i] > data[i - k] and data[i] > data[i + k]:
                p_data[i] += 1
    return np.where(p_data == max_window_length)[0]


def ampd(data: npt.ArrayLike, peak_type: int = 0, method="ampd", **kwargs):
    """
    基于多尺度的自动峰值检测（automatic multiscale-based peak detection）。
    参考文献：An Efficient Algorithm for Automatic Peak Detection in Noisy Periodic and Quasi-Periodic Signals

    支持的算法：

       1. find_peaks_original(spectrum, scale=scale, debug=debug)

       2. find_peaks(spectrum, scale=scale, debug=debug)

       3. find_peaks_adaptive(spectrum, window=window, debug=debug)

       4. ampd(spectrum, lsm_limit=lsm_limit)

       5. ampd_fast(spectrum, window_length=window_length, hop_length=hop_length, lsm_limit=lsm_limit, verbose=verbose)

       6. ampd_fast_sub(spectrum, order=order, lsm_limit=lsm_limit, verbose=verbose)

       7. ampd_wangjy(spectrum)

    :param data: 1-D numpy.ndarray。
    :param peak_type: 0代表波峰、1代表波谷。
    :param method: 算法库选择。
    :return: 峰所在索引值的数组。
    :rtype: np.ndarray
    """
    spectrum = np.array(data, copy=True)
    if peak_type == 1:
        spectrum = -spectrum
    from .pyampd import (
        find_peaks_original, find_peaks, find_peaks_adaptive
    )
    from ampdlib import ampd_fast, ampd_fast_sub
    from ampdlib import ampd as ampd_libs_ampd

    if method == "find_peaks_original":
        if "scale" in kwargs:
            scale = kwargs["scale"]
        else:
            scale = None
        if "debug" in kwargs:
            debug = kwargs["debug"]
        else:
            debug = False
        return find_peaks_original(spectrum, scale=scale, debug=debug)
    elif method == "find_peaks":
        if "scale" in kwargs:
            scale = kwargs["scale"]
        else:
            scale = None
        if "debug" in kwargs:
            debug = kwargs["debug"]
        else:
            debug = False
        return find_peaks(spectrum, scale=scale, debug=debug)
    elif method == "find_peaks_adaptive":
        if "window" in kwargs:
            window = kwargs["window"]
        else:
            window = None
        if "debug" in kwargs:
            debug = kwargs["debug"]
        else:
            debug = False
        return find_peaks_adaptive(spectrum, window=window, debug=debug)
    elif method == "ampd":
        if "lsm_limit" in kwargs:
            lsm_limit = kwargs["lsm_limit"]
        else:
            lsm_limit = 1
        return ampd_libs_ampd(spectrum, lsm_limit=lsm_limit)
    elif method == "ampd_fast":
        if "window_length" in kwargs:
            window_length = kwargs["window_length"]
        else:
            window_length = 200
        if "hop_length" in kwargs:
            hop_length = kwargs["hop_length"]
        else:
            hop_length = None
        if "lsm_limit" in kwargs:
            lsm_limit = kwargs["lsm_limit"]
        else:
            lsm_limit = 1
        if "verbose" in kwargs:
            verbose = kwargs["verbose"]
        else:
            verbose = False
        return ampd_fast(spectrum, window_length=window_length, hop_length=hop_length,
                         lsm_limit=lsm_limit, verbose=verbose)
    elif method == "ampd_fast_sub":
        if "order" in kwargs:
            order = kwargs["order"]
        else:
            order = 1
        if "lsm_limit" in kwargs:
            lsm_limit = kwargs["lsm_limit"]
        else:
            lsm_limit = 1
        if "verbose" in kwargs:
            verbose = kwargs["verbose"]
        else:
            verbose = False
        return ampd_fast_sub(spectrum, order=order, lsm_limit=lsm_limit, verbose=verbose)
    else:
        return ampd_wangjy(spectrum)
