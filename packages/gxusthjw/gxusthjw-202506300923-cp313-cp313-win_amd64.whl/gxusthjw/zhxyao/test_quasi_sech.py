#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        test_quasi_sech.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试quasi_sech.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/10     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import unittest

import numpy as np

from .quasi_sech import (
    sech,
    sech_np,
    quasi_sech,
    quasi_sech_np,
)


# 定义 ==============================================================
class TestQuasiSech(unittest.TestCase):
    """
    测试quasi_sech.py。
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

    def test_sech(self):
        x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        y = np.sin(x)
        res = sech(y)
        res2 = sech_np(y)
        mat_sech = np.array([0.727047269818797, 0.693148436379773,
                             0.990124533179941, 0.769049102857867,
                             0.668405967924652, 0.962194282940023,
                             0.817199777488825, 0.653312278636619,
                             0.920700462711772, 0.868307805730772])
        self.assertTrue(np.allclose(res, mat_sech, rtol=0, atol=1e-15))
        self.assertTrue(np.allclose(res2, mat_sech, rtol=0, atol=1e-15))
        self.assertTrue(np.allclose(res, res2))

        y = (np.sin(x) + np.cos(x) + np.tan(x)) ** 5
        res = sech(y)
        res2 = sech_np(y)
        mat_sech = np.array([0.000000000000000, 0.000001907091248,
                             0.668952426160539, 0.999999470665475,
                             0, 0.999959560947206, 0.000000000000000,
                             0, 0.758005217097327, 0.977507532590036])
        self.assertTrue(np.allclose(res, mat_sech, rtol=0, atol=1e-15))
        self.assertTrue(np.allclose(res2, mat_sech, rtol=0, atol=1e-15))
        self.assertTrue(np.allclose(res, res2))

    def test_quasi_sech(self):
        x = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        y = np.sin(x)
        res = quasi_sech(y,1,2)
        res_np = quasi_sech_np(y,1,2)
        self.assertTrue(np.allclose(res, res_np))

        y = (np.sin(x) + np.cos(x) + np.tan(x)) ** 5
        res = quasi_sech(y,1,2)
        res_np = quasi_sech_np(y,1,2)
        self.assertTrue(np.allclose(res, res_np))

        res = quasi_sech(y,2,20)
        res_np = quasi_sech_np(y,2,20)
        self.assertTrue(np.allclose(res, res_np))

# 主函数 =============================================================
if __name__ == '__main__':
    unittest.main()
