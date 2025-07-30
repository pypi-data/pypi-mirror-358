#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        test_spectrum.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试spectrum.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/17     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import unittest

import numpy as np

from ..commons import Ordering

from .spectrum import Spectrum


# 定义 ==============================================================
class TestSpectrum(unittest.TestCase):
    """
    测试spectrum.py。
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

    def test_init(self):
        x = np.arange(0, 10, 0.01)
        y = np.sin(x)
        print('x: ', x)
        print('y: ', y)
        print('len(x):', len(x), "len(y):", len(y))

        spec = Spectrum(y)
        self.assertEqual(1000, spec.len)
        print('spec.y: ', spec.y)
        print(spec.y.dtype)
        self.assertEqual(1000, len(spec.y))
        self.assertEqual(1000, len(spec.x))
        self.assertEqual(np.float64, spec.y.dtype)
        print('spec.x: ', spec.x)
        self.assertEqual(np.int64, spec.x.dtype)
        self.assertTrue(np.allclose(spec.y, y))
        self.assertTrue(np.allclose(spec.x, np.arange(0, 1000, dtype=np.int32)))
        self.assertEqual(Ordering.ASCENDING, spec.x_sorted_type)
        self.assertEqual(np.int32, Spectrum(np.arange(0, 1000, dtype=np.int32)).y.dtype)
        print(Spectrum(np.arange(0, 1000, dtype=np.int32)).y.dtype)

        spec2 = Spectrum(y, x)
        self.assertEqual(1000, spec2.len)
        self.assertEqual(1000, len(spec2.y))
        self.assertEqual(1000, len(spec2.x))
        self.assertEqual(np.float64, spec2.x.dtype)
        self.assertEqual(np.float64, spec2.y.dtype)
        self.assertTrue(np.allclose(spec2.y, y))
        self.assertTrue(np.allclose(spec2.x, x))
        self.assertEqual(Ordering.ASCENDING, spec2.x_sorted_type)
        e = np.random.randn(1000) * 0.2
        print('e: ', e)

    def test_init2(self):
        x = np.arange(0, 10, 0.01)
        print(x)
        y = np.sin(x)
        e = np.random.randn(1000) * 0.2
        spec = Spectrum(y, x, e)
        print(spec.find_index_x(spec.x_end))


# 主函数 =============================================================
if __name__ == '__main__':
    unittest.main()
