#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        spectra_cut_function.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义一个函数用于对谱数据进行截取。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/18     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import numpy as np

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Define a function that cuts off a portion of the spectral data.
"""

__all__ = [
    'spectra_cut_function'
]
# 定义 ==============================================================
def spectra_cut_function(wave, data, wave_range):
    """
    截取指定波数范围内的光谱数据。

    :param wave: 波数或时间的一维数组。
    :param data: 数据矩阵，行数应与 `wave` 长度一致。
    :param wave_range: 要保留的波数范围 [low, high]。
    :return: 元组，
            wave_cut (np.ndarray): 截取后的波数数组。
            data_cut (np.ndarray): 截取后的数据矩阵。
            wave_values_cut (np.ndarray): 实际截取的起始和结束波数值。
    """
    w_l = len(wave)

    if w_l != data.shape[0]:
        raise ValueError("data size and wavenumber or time mismatch")

    wave_ini = wave[0]
    slope = (wave[-1] - wave_ini) / (w_l - 1)

    index_wave = ((np.array(wave_range) - wave_ini) / slope) + 1
    index_wave = np.sort(index_wave).astype(int)

    index_wave[0] = np.floor(index_wave[0])
    index_wave[1] = np.ceil(index_wave[1])

    if index_wave[0] < 0:
        index_wave[0] = 0
    if index_wave[1] >= w_l:
        index_wave[1] = w_l - 1

    wave_cut = wave[index_wave[0]:index_wave[1] + 1]
    data_cut = data[index_wave[0]:index_wave[1] + 1, :]
    wave_values_cut = wave[[index_wave[0], index_wave[1]]]

    return wave_cut, data_cut, wave_values_cut