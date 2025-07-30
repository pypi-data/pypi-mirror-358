#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        xxxxxx.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      xxxxxx。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/xx/xx     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import numpy as np
from scipy.interpolate import (
    interp1d,
    PchipInterpolator,
    UnivariateSpline
)

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
"""

__all__ = [
    'spectra_baseline_correction'
]


# 定义 ==============================================================
def spectra_baseline_correction(wave, data, wave_values, r, method='linear'):
    """
    对光谱数据进行基线校正。

    :param wave: np.ndarray，波数/时间的一维数组。
    :param data: np.ndarray，数据矩阵，行数应与 `wave` 长度一致。
    :param wave_values: list or np.ndarray，要设为零点的波数值列表。
    :param r: int，在每个波数值周围的点数（范围）。
    :param method:插值方法，可选 'linear', 'pchip', 'spline'。
    :return: 元组，
            1. DataBaselineCorr (np.ndarray): 基线校正后的数据。
            2. baseline (np.ndarray): 插值得到的完整基线。
            3. baselinePoints (np.ndarray): 用于插值的点集。
    """
    wave = np.asarray(wave).flatten()
    data = np.asarray(data)
    wave_values = np.asarray(wave_values).flatten()

    w_l = len(wave)

    if w_l != data.shape[0]:
        raise ValueError("Data size and wavenumber/time do not match.")

    # 确保 wave_values 是列向量
    wave_values = wave_values.reshape(-1, 1)

    wave_ini = wave[0]
    wave_end = wave[-1]
    slope = (wave_end - wave_ini) / (w_l - 1)

    index_wave = ((wave_values - wave_ini) / slope + 1).round().astype(int).flatten()
    index_wave = np.sort(index_wave)
    index_wave = np.clip(index_wave, 1, w_l)

    step = int(np.ceil((r - 1) / 2))
    index_range = np.column_stack([index_wave - step, index_wave + step])
    index_range[:, 0] = np.clip(index_range[:, 0], 1, None)
    index_range[:, 1] = np.clip(index_range[:, 1], None, w_l)

    wave_points = wave[index_wave - 1]

    # 提取指定范围内的平均值
    if r > 1:
        data_points = []
        for i in range(len(index_wave)):
            start_idx = index_range[i, 0] - 1
            end_idx = index_range[i, 1]
            data_points.append(np.mean(data[start_idx:end_idx], axis=0))
        data_points = np.array(data_points)
    else:
        data_points = data[index_wave - 1]

    # 确保是二维数组
    if data_points.ndim == 1:
        data_points = data_points.reshape(1, -1)

    # 添加首尾两点以确保插值范围覆盖整个 wave
    if index_wave[0] > 1:
        first_point = data_points[0:1]  # 使用切片保持二维
        wave_points = np.insert(wave_points, 0, wave[0])
        data_points = np.vstack([first_point, data_points])

    if index_wave[-1] < w_l:
        last_point = data_points[-1:]  # 使用切片保持二维
        wave_points = np.append(wave_points, wave[-1])
        data_points = np.vstack([data_points, last_point])

    # 使用指定插值方法生成基线
    if method == 'pchip':
        interpolator = PchipInterpolator(wave_points, data_points, axis=0)
    elif method == 'spline':
        interpolator = UnivariateSpline(wave_points, data_points, k=3)
    else:
        interpolator = interp1d(
            wave_points, data_points,
            kind='linear', axis=0,
            fill_value="extrapolate"
        )

    baseline = interpolator(wave)
    data_baseline_corr = data - baseline
    baseline_points = np.hstack([wave_points.reshape(-1, 1), data_points])

    return data_baseline_corr, baseline, baseline_points
