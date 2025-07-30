#!/usr/bin/env python3
# --*-- coding: utf-8 --*--
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        fourier_deconv.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“傅里叶自去卷积函数”。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2023/10/15     revise
# ------------------------------------------------------------------
# 导包 =============================================================
import numpy as np
import numpy.typing as npt
from numpy import trapz
from scipy.fft import fft, ifft
import matplotlib.pyplot as plt

from .peak_shape import gauss, lorentz, logistic, gauss_lorentz
from .fourier_filter import fourier_filter


# ==================================================================

# noinspection PyUnboundLocalVariable,PyPep8Naming,PyTypeChecker
def fourier_self_deconv(x: npt.ArrayLike, y: npt.ArrayLike,
                        peak_shape: str, dw: float, m: float,
                        da: float, frequency_cut_off: float,
                        cut_off_rate: float, is_plot_all_steps: bool,
                        is_plot_frequency_spectra: bool):
    """
    傅里叶自去卷积。

    :param x: 时间
    :param y: 谱数据。
    :param peak_shape:峰形。
    :param dw: 去卷积的宽度，Deconvolution width
    :param m: 高斯所占比例。
    :param da: 分母增加量（denominator addition，百分比值）。
    :param frequency_cut_off: 频率截止。
    :param cut_off_rate: 截止率。
    :param is_plot_all_steps: bool型，绘图步骤。
    :param is_plot_frequency_spectra: bool型，绘制频率谱。
    :return:
    """
    x = np.array(x, copy=True, dtype=np.float64)
    y = np.array(y, copy=True, dtype=np.float64)
    num_points = len(x)
    match peak_shape.lower():
        case "gaussian":
            # 峰形。
            df = gauss(x, np.min(x), dw) + gauss(x, np.max(x), dw)
            # 去卷积后的谱数据。
            ydc = ifft(fft(y) / fft(df)) * np.sum(df)
        case "lorentzian":
            # 峰形。
            df = lorentz(x, np.min(x), dw) + lorentz(x, np.max(x), dw)
            # 去卷积后的谱数据。
            ydc = ifft(fft(y) / fft(df)) * np.sum(df)
        case "logistic":
            # 峰形。
            df = logistic(x, np.min(x), dw) + logistic(x, np.max(x), dw)
            # 去卷积后的谱数据。
            ydc = ifft(fft(y) / fft(df)) * np.sum(df)
        case "gauss_lorentz":
            # 峰形。
            df = gauss_lorentz(x, np.min(x), dw, m) + gauss_lorentz(x, np.max(x), dw, m)
            # 去卷积后的谱数据。
            ydc = ifft(fft(y) / fft(df)) * np.sum(df)
        case _:
            raise ValueError("The value of peak_shape must be one of "
                             "{{'gaussian','lorentzian','logistic','gauss_lorentz'}}, "
                             "but got {}.".format(peak_shape))

    # Apply only denominator addition to reduce noise and ringing
    fftc = fft(df)

    # Deconvolution by fft/ifft with Denominator addition
    ydcDA = ifft(fft(y) / (fftc + da * 0.01 * np.max(fftc))) * np.sum(df)

    # 对去卷积后的谱数据进行滤波处理。
    # Apply only Fourier filtering to reduce noise and ringing，Low-pass mode
    sy = fourier_filter(x, ydc, 0,
                        frequency_cut_off * 0.01 * len(x),
                        cut_off_rate, 1)

    # Apply both denominator addition and Fourier filtering to reduce noise
    # and ringing; Low-pass mode
    syDA = fourier_filter(x, ydcDA, 0,
                          frequency_cut_off * 0.01 * len(x),
                          cut_off_rate, 1)

    if is_plot_all_steps:
        plt.figure(0)
        plt.clf()
        plt.subplot(2, 2, 1)
        plt.plot(x, y, 'k')
        plt.title('Original data')
        plt.xlabel('Deconvolution width = ' + str(dw) + "%")

        plt.subplot(2, 2, 3)
        plt.plot(x, ydcDA, 'b')
        plt.title('FSD, with denominator addition only')
        plt.xlabel('Denom. Addition = ' + str(da) + "%")

        plt.subplot(2, 2, 2)
        plt.plot(x, sy, 'g')
        plt.title('FSD with filtering only')
        plt.xlabel('FrequencyCutoff = ' + str(frequency_cut_off))

        plt.subplot(2, 2, 4)
        plt.plot(x, syDA, 'r')
        plt.title('Both filtering and denom. addition')
    else:
        plt.figure(0)
        plt.clf()
        plt.plot(x, y, 'k', x, syDA)
        plt.title('Original data')
        plt.legend('Original data', 'Self-Deconvoluted')

    AreaRecovery = 100.0 * trapz(x, syDA) / trapz(x, y)
    plt.xlabel('Area recovery: ' + str(AreaRecovery) + ' %')

    if is_plot_frequency_spectra:
        plt.figure(1)
        plt.clf()
        fyc = fft(ydcDA)
        syc = fyc * np.conj(fyc)
        psrange = range(0, len(fyc) // 2)
        psyc = np.real(syc[psrange])
        plt.loglog(psrange, psyc, 'b', linewidth=1)

        fyc = fft(sy)
        syc = fyc * np.conj(fyc)
        psyc = np.real(syc[psrange])
        plt.loglog(psrange, psyc, 'g', linewidth=1)

        fyc = fft(y)
        syc = fyc * np.conj(fyc)
        minspec = np.min(syc)
        maxspec = np.max(syc)
        psyc = np.real(syc[psrange])
        plt.loglog(psrange, psyc, 'k', linewidth=1)

        fyc = fft(syDA)
        syc = fyc * np.conj(fyc)
        psyc = np.real(syc[psrange])
        plt.loglog(psrange, psyc, 'r', linewidth=1)

        plt.axis((1, num_points / 4, minspec, maxspec))
        plt.title('Frequency spectra')
        plt.xlabel('Frequency')
        plt.legend(('Denominator addition only',
                    'Filtering only',
                    'Original signal',
                    'Both filtering and denom. addition'),
                   loc='best')
        plt.show()

    return x, y, df, ydc, fftc, ydcDA, sy, syDA
