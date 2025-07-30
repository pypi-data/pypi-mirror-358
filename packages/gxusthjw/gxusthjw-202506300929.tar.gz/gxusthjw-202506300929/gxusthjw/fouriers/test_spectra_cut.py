#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        test_spectra_cut_function.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试spectra_cut_function.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/18     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import unittest

import numpy as np
from .spectra_cut import spectra_cut_function
# 定义 ==============================================================
class TestSpectraCutFunction(unittest.TestCase):
    """
    测试spectra_cut_function.py。
    """

    # region
    # --------------------------------------------------------------
    def setUp(self):
        """
        Hook method for setting up the test fixture before exercising it.
        """
        print("\n\n-----------------------------------------------------")

    def tearDown(self):
        """
        Hook method for deconstructing the test fixture after testing it.
        """
        print("-----------------------------------------------------")

    @classmethod
    def setUpClass(cls):
        """
        Hook method for setting up class fixture before running tests in the class.
        """
        print("\n\n=======================================================")

    @classmethod
    def tearDownClass(cls):
        """
        Hook method for deconstructing the class fixture after running all tests in the class.
        """
        print("=======================================================")
    # --------------------------------------------------------------
    # endregion

    def test_(self):
        # 示例输入
        wave = np.linspace(900, 3000, 2101)  # 假设从 900 到 3000 共 2101 个点
        data = np.random.rand(2101, 5)  # 5 条光谱数据
        wave_range = [1000, 2500]

        # 调用函数
        wave_cut, data_cut, wave_values_cut = spectra_cut_function(wave, data, wave_range)

        print("截取后波数范围:", wave_values_cut)
        print("截取后数据形状:", data_cut.shape)

        wave_range = [1000, 1800]

        # 调用函数
        wave_cut, data_cut, wave_values_cut = spectra_cut_function(wave, data, wave_range)

        print("截取后波数范围:", wave_values_cut)
        print("截取后数据形状:", data_cut.shape)

# 主函数 =============================================================
if __name__ == '__main__':
    unittest.main()
