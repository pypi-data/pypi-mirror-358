#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        test_xxxxxx.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试xxxxxx.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/xx/xx     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import unittest

import numpy as np
from .create_options_fouriers import create_options_fouriers
from .filter_fourier import filter_fourier
# 定义 ==============================================================
class TestXxxxxx(unittest.TestCase):
    """
    测试xxxxxx.py。
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

        options = create_options_fouriers()

        # 构建 t 轴
        ntn = 2048
        dtn = 1 / (0.1 * ntn)  # 假设 df = 0.1
        t = np.concatenate([
            np.arange(0, ntn // 2) * dtn,
            np.arange(-ntn // 2, 0) * dtn
        ])

        # 调用函数
        filter_function = filter_fourier(t, "FSD", options)

        print("滤波器长度:", len(filter_function))


# 主函数 =============================================================
if __name__ == '__main__':
    unittest.main()
