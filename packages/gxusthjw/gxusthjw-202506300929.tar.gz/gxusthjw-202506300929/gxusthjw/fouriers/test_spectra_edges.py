#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        test_spectra_edges.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试spectra_edges.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/18     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import unittest
import numpy as np
from .create_options_fouriers import create_options_fouriers
from .spectra_edges import spectra_edges

# 定义 ==============================================================
class TestSpectraEdgesFunction(unittest.TestCase):
    """
    测试spectra_edges.py。
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

    def test_spectra_edges_function(self):
        # 示例输入
        wave = np.linspace(900, 3000, 2101)
        data = np.sin(wave)[:, None]  # 模拟单列光谱数据

        options = create_options_fouriers()
        options.Border = "refl-att"
        options.BorderExtension = 100

        # 调用函数
        signal_extended = spectra_edges(data, options)

        print("扩展后数据形状:", signal_extended.shape)


# 主函数 =============================================================
if __name__ == '__main__':
    unittest.main()
