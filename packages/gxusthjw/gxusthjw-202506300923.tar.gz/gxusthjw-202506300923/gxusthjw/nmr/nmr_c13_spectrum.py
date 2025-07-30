#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        nmr_c13_spectrum.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“表征`NMR C13 谱数据`的类”。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/17     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
from typing import Union

import numpy as np
import numpy.typing as npt

from ..spectrum import (
    Spectrum,
)

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Define a class that represents `NMR C13 spectrum`.
"""

__all__ = [
    'NmrC13Spectrum',
]


# 定义 ==============================================================
class NmrC13Spectrum(Spectrum):
    """
    类`NmrC13Spectrum`表征“NMR C13 谱数据”。
    """

    def __init__(self, ppm: npt.NDArray[np.number],
                 intensity: npt.NDArray[np.number],
                 **kwargs):
        """
        类`NmrC13Spectrum`的初始化方法。

        :param ppm: 化学位移数据。
        :param intensity: 强度数据。
        :param kwargs: 其他可选关键字。
        """
        super(NmrC13Spectrum, self).__init__(intensity, ppm, **kwargs)
        self.data_logger.log(intensity, 'intensity')
        self.data_logger.log(ppm, "ppm")

    @property
    def intensity(self):
        """
        获取强度数据。

        :return: 强度数据。
        """
        return self.y

    @property
    def ppm(self):
        """
        获取化学位移数据。

        :return: 化学位移数据。
        """
        return self.x

    def slice(self, xi: Union[int, float], xj: Union[int, float]):
        """
        从光谱数据中截取一个片段。

        :param xi: 指定的波数1。
        :param xj: 指定的波数2。
        :return: 截取到的片段。
        """
        index_xi, index_xj = self.find_index_xrange(xi, xj)
        slice_ppm = self.ppm[index_xi:index_xj + 1]
        slice_intensity = self.intensity[index_xi:index_xj + 1]
        return NmrC13Spectrum(slice_ppm, slice_intensity, **self.rebuild_kwargs())

    def horizontal_shift(self, shift_amount: Union[int, float]):
        """
        谱数据横向移动。

        :param shift_amount:移动量。
        :return: 移动后的数据。
        """
        new_ppm = self.ppm + shift_amount
        self.data_logger.log(new_ppm, f"ppm_shift_{shift_amount}")
        return NmrC13Spectrum(new_ppm, self.intensity, **self.rebuild_kwargs())

    def vertical_shift(self, shift_amount: Union[int, float]):
        """
        谱数据纵向移动。

        :param shift_amount:移动量。
        :return: 移动后的数据。
        """
        new_intensity = self.intensity + shift_amount
        self.data_logger.log(new_intensity, f"intensity_shift_{shift_amount}")
        return NmrC13Spectrum(self.ppm, new_intensity, **self.rebuild_kwargs())

    def normalize(self, upper: float = 1.0):
        """
        使谱数据规范化。

        :param upper: 规范化区间的上限。
        :return: 规范化后的强度值。
        """
        new_intensity = self.y_normalize(upper=upper)
        self.data_logger.log(new_intensity, f"intensity_normalized_{upper}")
        return NmrC13Spectrum(self.ppm, new_intensity, **self.rebuild_kwargs())

    def find_alignment_point(self, x_start=110, x_end=120):
        """
        在指定的范围内找到一个定点，该定点可作为基准，用于矫正谱偏离。

        :param x_start: 起始范围。
        :param x_end: 终止范围。
        :return: 定点的x坐标值，定点的y坐标值。
        """
        return self.find_x_peak(x_start, x_end)
