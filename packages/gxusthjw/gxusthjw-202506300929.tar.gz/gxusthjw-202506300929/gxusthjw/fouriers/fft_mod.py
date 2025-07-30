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
from scipy.fft import fft, ifft
from scipy.interpolate import interp1d

# 假设你已实现以下函数：
from .spectra_edges import spectra_edges
from .filter_fourier import filter_fourier
from .inv_filter_fourier import inv_filter_fourier
# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
"""

__all__ = [
    'fft_mod',
]
# 定义 ==============================================================



def fft_mod(wave, data, method, options):
    """
    执行基于傅里叶变换的数据处理（如导数、平滑、去噪、插值等）

    参数:
        wave (np.ndarray): 一维波数或时间数组。
        data (np.ndarray): 输入数据，可以是列向量或矩阵 (n_wave, n_times)
        method (str): 操作模式，可选:
                      "Fderivative", "FSD", "Fsmooth", "Fresolution", "Interpolation"
        options (SimpleNamespace or dict): 包含傅里叶变换参数的配置对象，需包含如下字段：
            - x_linearityTol: 波数非线性容忍度
            - BorderExtension: 边界扩展点数
            - Border: 边界扩展方式，如 'mirror', 'none' 等
            - DerivativeOrder: 导数阶数
            - PhaseCorrection: 是否开启相位校正，取值为 'On' 或 'Off'
            - FSD_FWHHL, FSD_FWHHG, FSD_narrowing: FSD 相关参数
            - Filter: 滤波器类型
            - Interpolation: 插值倍数

    返回:
        wave_modified (np.ndarray): 修改后的波数轴
        data_modified (np.ndarray): 处理后的数据
    """
    wave = np.asarray(wave).flatten()
    data = np.asarray(data)

    n_wave = len(wave)
    ntimes = data.shape[1] if data.ndim > 1 else 1

    if n_wave != data.shape[0]:
        raise ValueError("Data size and wavenumber/time do not match.")

    # 如果数据不是等间距的，进行插值
    df = np.diff(wave)
    linearity_error = (df.max() - df.min()) / df.mean()
    if linearity_error > options.x_linearityTol:
        print("Warning: The x axis is not uniformly spaced.")
        print("Data will be interpolated to make it linearly spaced.")
        old_wave = wave.copy()
        new_spacing = np.median(df)
        new_wave = np.arange(old_wave[0], old_wave[-1] + new_spacing, new_spacing)
        interpolator = interp1d(old_wave, data, kind='linear', axis=0, fill_value="extrapolate")
        data = interpolator(new_wave)
        wave = new_wave
        n_wave = len(wave)

    wave_ini = wave[0]
    wave_end = wave[-1]
    df = (wave_end - wave_ini) / (n_wave - 1)

    # 扩展数据以避免边缘不连续
    if hasattr(options, 'BorderExtension') and options.BorderExtension > 0:
        options.BorderExtension = round(options.BorderExtension / df)
        data_extended = spectra_edges(data, options)
    else:
        data_extended = data.copy()

    ntn = data_extended.shape[0]

    # 构建 FT 的 t 轴
    T = 1 / abs(df)
    dtn = T / ntn
    t = np.concatenate([
        np.arange(0, (ntn // 2)) * dtn,
        np.arange(-ntn // 2, 0) * dtn
    ])

    # FFT
    DataExtendedInterferogram = abs(df) * fft(data_extended, axis=0)

    # 获取滤波器函数
    Filter = filter_fourier(t, method, options)

    # 获取反滤波器函数
    if method in ["Fderivative"]:
        n_der = options.DerivativeOrder
        if options.PhaseCorrection == "On":
            InvFilter = (2 * np.pi * np.abs(t)) ** n_der
        else:
            InvFilter = (1j * 2 * np.pi * t) ** n_der
    elif method == "FSD":
        fwhhL = options.FSD_FWHHL
        fwhhG = options.FSD_FWHHG
        InvFilter = np.exp(fwhhL * np.pi * np.abs(t) + (fwhhG * np.pi / (2 * np.sqrt(np.log(2)))) ** 2 * t ** 2)
    elif method == "Fsmooth":
        InvFilter = 1.0
    elif method == "Fresolution":
        InvFilter = inv_filter_fourier(t, options)
    elif method == "Interpolation":
        Filter = np.ones_like(t)
        InvFilter = np.ones_like(t)
    else:
        raise ValueError(f"Unsupported method for fftMod_function: {method}")

    # 合成滤波器
    FilterTotal = Filter * InvFilter

    # 应用滤波器
    DataExtendedInterferogram_Modified = DataExtendedInterferogram * FilterTotal[:, None]

    # IFFT
    DataExtended_Modified = np.real(ifft(DataExtendedInterferogram_Modified, axis=0) / abs(df))

    # 插值输出
    if getattr(options, 'Interpolation', 1) != 1:
        # 使用 scipy 的快速傅里叶重采样
        target_len = ntn * options.Interpolation
        DataExtended_Modified = np.apply_along_axis(
            lambda x: np.fft.irfft(np.fft.rfft(x), target_len), axis=0, arr=DataExtended_Modified
        )

    # 构建新的波数轴
    wave_modified = np.arange(wave_ini, wave_end + df / options.Interpolation, df / options.Interpolation)
    wave_modified = wave_modified[:len(DataExtended_Modified)]

    data_modified = DataExtended_Modified[:len(wave_modified), :]

    return wave_modified, data_modified
