#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        test_data_xy.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试data_xy.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/23     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import unittest
from pprint import pprint
import numpy as np
from numpy.testing import assert_array_equal

from .data_xy import (
    DataXY
)


# 定义 ==============================================================
class TestDataXY(unittest.TestCase):
    """
    测试data_xy.py。
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
        x = [1, 2, 3, 4]
        y = [2, 3, 4, 5, 6]
        d1 = DataXY(y, x)
        assert_array_equal(d1.data_x, np.array([1, 2, 3, 4]))
        assert_array_equal(d1.data_y, np.array([2, 3, 4, 5, 6]))
        pprint(d1.data_y)
        pprint(d1.data_x)

        d2 = DataXY(y)
        assert_array_equal(d2.data_x, np.array([0, 1, 2, 3, 4]))
        assert_array_equal(d2.data_y, np.array([2, 3, 4, 5, 6]))
        pprint(d2.data_x)
        pprint(d2.data_y)

        with self.assertRaises(ValueError):
            d2.data_x[0] = 10
        assert_array_equal(d2.data_x, np.array([0, 1, 2, 3, 4]))
        pprint(d2.data_x)

        x2 = [[1, 2], [3, 4]]
        with self.assertRaises(ValueError) as e:
            DataXY(y, x2)
        print(e.exception)
        self.assertEqual(str(e.exception),
                         "Input data cannot be converted to a numeric 1D array.")
        y2 = {1, 2, 3, 4, 5}
        with self.assertRaises(ValueError):
            # noinspection PyTypeChecker
            DataXY(y2, x)

        pprint(d1.data_len)
        self.assertEqual(d1.data_len, len(x))
        self.assertEqual(d1.data_x_len, len(x))
        self.assertEqual(d1.data_y_len, len(y))

        pprint(d2.data_len)
        self.assertEqual(d2.data_len, len(y))
        self.assertEqual(d2.data_x_len, len(y))
        self.assertEqual(d2.data_y_len, len(y))

    def test_data(self):
        x = [1, 2, 3, 4]
        y = [2, 3, 4, 5, 6]
        d1 = DataXY(y, x)
        pprint(d1.data)
# 主函数 =============================================================
if __name__ == '__main__':
    unittest.main()
