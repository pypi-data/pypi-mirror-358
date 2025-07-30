#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        spectra_edges_function.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      xxxxxx。
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
"""

__all__ = [
    'spectra_edges'
]


# 定义 ==============================================================


def spectra_edges(data, options):
    """
    修改光谱数据的边缘以减少不连续性，从而降低傅里叶变换中的失真。

    参数:
        data (np.ndarray): 输入光谱数据，可以是列向量或矩阵。
        options (SimpleNamespace or dict): 包含边缘处理选项的对象。
            - Border: 边缘扩展方法（"none", "mirror", "refl-att", "refl-inv-att"）
            - BorderExtension: 扩展点数（仅当 method != 'none' 时有效）

    返回:
        signal_extended (np.ndarray): 处理后的扩展信号。
    """
    method = getattr(options, 'Border', None)
    nextra = getattr(options, 'BorderExtension', 0)

    n_wave, ntimes = data.shape
    if ntimes == 1:
        is_vector = True
    else:
        is_vector = False

    if not method or method == "none":
        e = np.ceil(np.log2(n_wave))
        ntn = int(2 ** e)
        signal_extended = np.vstack([data, np.zeros((ntn - n_wave, ntimes))])

    elif method == "refl-att":  # reflection-attenuation
        e = np.ceil(np.log2(n_wave + 2 * nextra))
        ntn = int(2 ** e)

        if is_vector:
            inicio = data[:nextra] * (1 - (np.arange(nextra) / nextra)[:, None]) ** 2 ** 2
            final = data[n_wave - nextra:] * (1 - (np.arange(nextra)[::-1] / nextra)[:, None]) ** 2 ** 2
        else:
            weights_inicio = (1 - (np.arange(nextra) / nextra)[:, None]) ** 2 ** 2
            weights_final = (1 - (np.arange(nextra)[::-1] / nextra)[:, None]) ** 2 ** 2
            inicio = weights_inicio * data[:nextra]
            final = weights_final * data[n_wave - nextra:]

        signal_extended = np.vstack([
            data,
            np.flipud(final),
            np.zeros((ntn - n_wave - 2 * nextra, ntimes)),
            np.flipud(inicio)
        ])

    elif method == "refl-inv-att":  # Reflect-invers-atenuation
        e = np.ceil(np.log2(n_wave + 2 * nextra))
        ntn = int(2 ** e)

        if is_vector:
            inicio = -data[:nextra + 1]
            inicio = (inicio[1:] - 2 * inicio[0]) * (1 - (np.arange(nextra) / nextra)[:, None]) ** 2 ** 2
            final = -data[n_wave - nextra - 1:n_wave]
            final = (final[:nextra] - 2 * final[nextra]) * (1 - (np.arange(nextra)[::-1] / nextra)[:, None]) ** 2 ** 2
        else:
            inicio = -data[:nextra + 1]
            inicio = (inicio[1:] - 2 * inicio[[0], :]) * (1 - (np.arange(nextra) / nextra)[:, None]) ** 2 ** 2
            final = -data[n_wave - nextra - 1:n_wave]
            final = (final[:nextra] - 2 * final[[nextra], :]) * (
                        1 - (np.arange(nextra)[::-1] / nextra)[:, None]) ** 2 ** 2

        signal_extended = np.vstack([
            data,
            np.flipud(final),
            np.zeros((ntn - n_wave - 2 * nextra, ntimes)),
            np.flipud(inicio)
        ])

    elif method == "mirror":
        e = np.ceil(np.log2(2 * n_wave))
        ntn = int(2 ** e)

        if is_vector:
            if np.max(np.abs(data[-1])) >= np.max(np.abs(data[0])):
                signal_extended = np.vstack([
                    data,
                    np.flipud(data),
                    np.ones((ntn - 2 * n_wave, 1)) * data[[0]]
                ])
            else:
                signal_extended = np.vstack([
                    data,
                    np.ones((ntn - 2 * n_wave, 1)) * data[[-1]],
                    np.flipud(data)
                ])
        else:
            if np.mean(np.abs(data[-1, :])) >= np.mean(np.abs(data[0, :])):
                signal_extended = np.vstack([
                    data,
                    np.flipud(data),
                    np.ones((ntn - 2 * n_wave, ntimes)) * data[[0], :]
                ])
            else:
                signal_extended = np.vstack([
                    data,
                    np.ones((ntn - 2 * n_wave, ntimes)) * data[[-1], :],
                    np.flipud(data)
                ])

    else:
        raise ValueError(f"Unsupported border method: {method}")

    return signal_extended
