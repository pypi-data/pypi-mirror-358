#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        test_data_2d_region.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试data_2d_region.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2024/10/22     finish
# ------------------------------------------------------------------
# 导包 =============================================================
import unittest

import numpy as np

from .data_2d_region import Data2dRegion


# ==================================================================
class TestData2dRegion(unittest.TestCase):
    """
    测试data_2d_region.py。
    """

    # --------------------------------------------------------------------
    def setUp(self):
        """
        Hook method for setting up the test fixture before exercising it.
        """
        # 在每个测试方法之前运行，用于初始化测试数据
        self.data_y = np.array([1, 2, 3, 4, 5])
        self.data_x = np.array([6, 7, 8, 9, 10])
        self.region_start = 1
        self.region_length = 3
        self.data2d_region = Data2dRegion(self.data_y, self.data_x, self.region_start, self.region_length)
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

    # --------------------------------------------------------------------

    def test_init_(self):
        x1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        x2 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        y = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.10]
        d2r = Data2dRegion(y, x1)
        self.assertTrue(np.allclose(d2r.data_x, x1))
        self.assertTrue(np.allclose(d2r.data_y, y))
        self.assertEqual(d2r.data_x_len, 10)
        self.assertEqual(d2r.data_y_len, 10)
        self.assertEqual(d2r.data_len, 10)
        self.assertEqual(d2r.region_start, 0)
        self.assertEqual(d2r.region_length, 10)
        self.assertTrue(np.allclose(d2r.region_data_x, x1))
        self.assertTrue(np.allclose(d2r.region_data_y, y))

        d2r2 = Data2dRegion(y, x2)
        self.assertTrue(np.allclose(d2r2.data_x, x2))
        self.assertTrue(np.allclose(d2r2.data_y, y))
        self.assertEqual(d2r2.data_x_len, 11)
        self.assertEqual(d2r2.data_y_len, 10)
        self.assertEqual(d2r2.data_len, 10)
        self.assertEqual(d2r2.region_start, 0)
        self.assertEqual(d2r2.region_length, 10)
        self.assertTrue(np.allclose(d2r2.region_data_x, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))
        self.assertTrue(np.allclose(d2r2.region_data_y, y))

        y1 = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        d2r3 = Data2dRegion(y1, x1)
        self.assertTrue(np.allclose(d2r3.data_x, x1))
        self.assertTrue(np.allclose(d2r3.data_y, y1))
        self.assertEqual(d2r3.data_x_len, 10)
        self.assertEqual(d2r3.data_y_len, 9)
        self.assertEqual(d2r3.data_len, 9)
        self.assertEqual(d2r3.region_start, 0)
        self.assertEqual(d2r3.region_length, 9)
        self.assertTrue(np.allclose(d2r3.region_data_x, [1, 2, 3, 4, 5, 6, 7, 8, 9]))
        self.assertTrue(np.allclose(d2r3.region_data_y, y1))

    def test_parameter(self):
        x2 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        y = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.10]
        d2r = Data2dRegion(y, x2, region_start=1, region_length=5)
        self.assertEqual(d2r.region_start, 1)
        self.assertEqual(d2r.region_length, 5)
        self.assertTrue(np.allclose(d2r.region_data_x, [2, 3, 4, 5, 6]))
        self.assertTrue(np.allclose(d2r.region_data_y, [0.2, 0.3, 0.4, 0.5, 0.6]))
        self.assertEqual(d2r.region_stop, 6)
        d2r.region_start = 2
        self.assertEqual(d2r.region_start, 2)
        self.assertTrue(np.allclose(d2r.region_data_x, [3, 4, 5, 6, 7]))
        self.assertTrue(np.allclose(d2r.region_data_y, [0.3, 0.4, 0.5, 0.6, 0.7]))
        self.assertEqual(d2r.region_stop, 7)
        d2r.region_length = 3
        self.assertEqual(d2r.region_length, 3)
        self.assertTrue(np.allclose(d2r.region_data_x, [3, 4, 5]))
        self.assertTrue(np.allclose(d2r.region_data_y, [0.3, 0.4, 0.5]))
        self.assertEqual(d2r.region_stop, 5)

        d2r.region_slice = slice(1, 3)
        self.assertTrue(np.allclose(d2r.region_data_x, [2, 3]))
        self.assertTrue(np.allclose(d2r.region_data_y, [0.2, 0.3]))

    def test_region_slice_(self):
        x2 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        y = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.10]
        d2r = Data2dRegion(y, x2)
        # 测试不同的 slice 对象
        d2r.region_slice = slice(2, 6)
        assert d2r.region_slice == slice(2, 6, 1)
        assert d2r.region_data_len == 4

        d2r.region_slice = slice(None, 8)
        assert d2r.region_slice == slice(0, 8, 1)
        assert d2r.region_data_len == 8

        try:
            d2r.region_slice = slice(None, None, 2)
        except ValueError as e:
            assert str(e) == "Expected region_slice.step is None or region_slice.step == 1."

    def test_init(self):
        # 测试初始化方法
        self.assertEqual(self.data2d_region.region_start, self.region_start)
        self.assertEqual(self.data2d_region.region_length, self.region_length)
        self.assertEqual(self.data2d_region.region_stop, self.region_start + self.region_length)
        self.assertTrue(np.array_equal(self.data2d_region.region_data_y,
                                       self.data_y[self.region_start:self.region_start + self.region_length]))
        self.assertTrue(np.array_equal(self.data2d_region.region_data_x,
                                       self.data_x[self.region_start:self.region_start + self.region_length]))

    def test_region_start_setter(self):
        # 测试region_start的setter方法
        new_start = 2
        self.data2d_region.region_start = new_start
        self.assertEqual(self.data2d_region.region_start, new_start)
        self.assertTrue(self.data2d_region.is_parameter_changed)

    def test_region_length_setter(self):
        # 测试region_length的setter方法
        new_length = 2
        self.data2d_region.region_length = new_length
        self.assertEqual(self.data2d_region.region_length, new_length)
        self.assertTrue(self.data2d_region.is_parameter_changed)

    def test_region_slice(self):
        # 测试region_var_slice属性
        slice_obj = self.data2d_region.region_slice
        self.assertEqual(slice_obj.start, self.region_start)
        self.assertEqual(slice_obj.stop, self.region_start + self.region_length)
        self.assertEqual(slice_obj.step, 1)

    def test_set_region_slice(self):
        # 测试set_region_var_slice方法
        new_start = 2
        new_length = 2
        self.data2d_region.set_region_slice(new_start, new_length)
        self.assertEqual(self.data2d_region.region_start, new_start)
        self.assertEqual(self.data2d_region.region_length, new_length)

    def test_region_data_y(self):
        # 测试region_var_y属性
        self.assertTrue(np.array_equal(self.data2d_region.region_data_y,
                                       self.data_y[self.region_start:self.region_start + self.region_length]))

    def test_region_data_x(self):
        # 测试region_var_x属性
        self.assertTrue(np.array_equal(self.data2d_region.region_data_x,
                                       self.data_x[self.region_start:self.region_start + self.region_length]))

    def test_region_data_len(self):
        # 测试region_var_len属性
        self.assertEqual(self.data2d_region.region_data_len, self.region_length)

    def test_region_data_stop(self):
        # 测试region_var_stop属性
        self.assertEqual(self.data2d_region.region_data_stop, self.region_start + self.region_length)

    def test_region_data_check(self):
        # 测试region_var_check方法
        # 创建一个region_length比data_y或data_x的实际长度大的情况
        data_y = np.array([1, 2, 3])
        data_x = np.array([4, 5])
        region_start = 0
        region_length = 3  # 这个长度大于data_x的长度，将会触发异常

        data2d_region = Data2dRegion(data_y, data_x, region_start, region_length)

        # 调用region_var_check之前，我们需要确保region_var_x和region_var_y的长度不一致
        # 由于data_x的长度小于region_length，所以region_var_x和region_var_y的长度不一致
        with self.assertRaises(ValueError):
            data2d_region.region_data_check()

    def test_is_region_data_aligned(self):
        # 测试is_region_var_aligned属性
        self.assertTrue(self.data2d_region.is_region_data_aligned)




if __name__ == '__main__':
    unittest.main()
