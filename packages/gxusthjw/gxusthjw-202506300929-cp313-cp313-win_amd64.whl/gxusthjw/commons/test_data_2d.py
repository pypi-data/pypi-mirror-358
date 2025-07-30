#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        test_data_2d.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试data_2d.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/05     finish
# ------------------------------------------------------------------
# 导包 =============================================================
import unittest

import numpy as np

from .data_2d import Data2d


# ==================================================================
class TestData2d(unittest.TestCase):
    """
    测试data_2d.py。
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
        d = Data2d([1])
        self.assertTrue(np.array_equal(d.data_y, np.array([1])))
        self.assertTrue(np.array_equal(d.data_x, np.array([0])))
        self.assertEqual(1, d.data_len)
        self.assertEqual(1, d.data_x_len)
        self.assertEqual(1, d.data_y_len)

        da = Data2d([1, 2])
        self.assertTrue(np.array_equal(da.data_y, np.array([1, 2])))
        self.assertTrue(np.array_equal(da.data_x, np.array([0, 1])))
        self.assertEqual(2, da.data_len)
        self.assertEqual(2, da.data_x_len)
        self.assertEqual(2, da.data_y_len)

        x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        y = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        d1 = Data2d(y)
        self.assertTrue(np.allclose(d1.data_y, np.asarray(y)))
        self.assertTrue(np.allclose(d1.data_x, np.arange(11)))
        self.assertEqual(d1.data_len, 11)
        self.assertEqual(d1.data_x_len, 11)
        self.assertEqual(d1.data_y_len, 11)
        self.assertTrue(d1.is_aligned)
        print(d1.data)
        print(d1.exog)
        print(d1.endog)

        d2 = Data2d(y, x)
        self.assertTrue(np.allclose(d2.data_y, np.asarray(y)))
        self.assertTrue(np.allclose(d2.data_x, np.asarray(x)))
        self.assertEqual(d2.data_len, 10)
        self.assertEqual(d2.data_x_len, 10)
        self.assertEqual(d2.data_y_len, 11)
        self.assertFalse(d2.is_aligned)
        print(d2.data)
        print(d2.exog)
        print(d2.endog)

        d3 = Data2d([])
        print(d3.data_y)

    def test_iter(self):
        x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        y = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        d2 = Data2d(y, x)
        for xi, yi in d2:
            print(xi, yi)

    def test_str(self):
        x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        y = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        d1 = Data2d(y, x)
        self.assertEqual(d1.__len__(), 11)
        print(d1.__str__())
        print(d1.__repr__())
        d2 = eval(repr(d1))
        print(d2)

        d3 = eval(str(d1))
        print(d3)
        print(d2.data)
        print(d2.get_x(5))
        print(d2.get_y(5))
        print(d2.get_xy(5))


class TestData2d2(unittest.TestCase):
    """
    测试Data2d类。
    """

    def setUp(self):
        # 初始化一个标准的 Data2d 实例用于测试
        self.data_y = [1, 2, 3, 4]
        self.data_x = [10, 20, 30, 40]
        self.data2d = Data2d(self.data_y, self.data_x)

    def test_init_with_data_x(self):
        self.assertTrue(np.array_equal(self.data2d.data_y, np.array([1, 2, 3, 4])))
        self.assertTrue(np.array_equal(self.data2d.data_x, np.array([10, 20, 30, 40])))

    def test_init_without_data_x(self):
        data2d = Data2d([1, 2, 3])
        self.assertTrue(np.array_equal(data2d.data_x, np.arange(3)))

    def test_data_y_property(self):
        self.assertTrue(np.array_equal(self.data2d.data_y, np.array([1, 2, 3, 4])))

    def test_data_y_len_property(self):
        self.assertEqual(self.data2d.data_y_len, 4)

    def test_data_x_property(self):
        self.assertTrue(np.array_equal(self.data2d.data_x, np.array([10, 20, 30, 40])))

    def test_data_x_len_property(self):
        self.assertEqual(self.data2d.data_x_len, 4)

    def test_data_len_property(self):
        self.assertEqual(self.data2d.data_len, 4)
        data2d = Data2d([1, 2], [10, 20, 30])
        self.assertEqual(data2d.data_len, 2)

    # noinspection PyUnresolvedReferences
    def test_data_property(self):
        df = self.data2d.data
        self.assertEqual(df.shape, (4, 2))
        self.assertTrue((df['data_y'] == [1, 2, 3, 4]).all())
        self.assertTrue((df['data_x'] == [10, 20, 30, 40]).all())

    def test_exog_property(self):
        self.assertTrue(np.array_equal(self.data2d.exog, np.array([10, 20, 30, 40])))

    def test_endog_property(self):
        self.assertTrue(np.array_equal(self.data2d.endog, np.array([1, 2, 3, 4])))

    def test_is_aligned_property(self):
        self.assertTrue(self.data2d.is_aligned)
        data2d = Data2d([1, 2], [10, 20, 30])
        self.assertFalse(data2d.is_aligned)

    def test_get_x(self):
        self.assertEqual(self.data2d.get_x(0), 10)
        with self.assertRaises(IndexError) as e:
            self.data2d.get_x(10)  # 超出范围
        print(e)

    def test_get_y(self):
        self.assertEqual(self.data2d.get_y(0), 1)
        with self.assertRaises(IndexError):
            self.data2d.get_y(10)  # 超出范围

    def test_get_xy(self):
        self.assertEqual(self.data2d.get_xy(0), (10, 1))
        self.assertEqual(self.data2d.get_xy(3), (40, 4))

    def test_len(self):
        self.assertEqual(len(self.data2d), 4)
        data2d = Data2d([1, 2], [10, 20, 30])
        self.assertEqual(len(data2d), 3)

    def test_getitem(self):
        self.assertEqual(self.data2d[0], (10, 1))
        self.assertEqual(self.data2d[3], (40, 4))

    def test_iter_next(self):
        expected = [(10, 1), (20, 2), (30, 3), (40, 4)]
        for i, item in enumerate(self.data2d):
            self.assertEqual(item, expected[i])

    def test_eq_ne(self):
        d1 = Data2d([1, 2], [3, 4])
        d2 = Data2d([1, 2], [3, 4])
        d3 = Data2d([1, 2], [5, 6])
        self.assertTrue(d1 == d2)
        self.assertFalse(d1 != d2)
        self.assertTrue(d1 != d3)
        self.assertFalse(d1 == d3)

    def test_str_repr(self):
        self.assertEqual(str(self.data2d), "Data2d(data_y=[1, 2, 3, 4], data_x=[10, 20, 30, 40])")
        self.assertEqual(repr(self.data2d),
                         "Data2d(data_y=np.array([1, 2, 3, 4]), data_x=np.array([10, 20, 30, 40]))")

    def test_hash(self):
        d1 = Data2d([1, 2], [3, 4])
        d2 = Data2d([1, 2], [3, 4])
        d3 = Data2d([1, 2], [5, 6])
        self.assertEqual(hash(d1), hash(d2))
        self.assertNotEqual(hash(d1), hash(d3))

if __name__ == '__main__':
    unittest.main()
