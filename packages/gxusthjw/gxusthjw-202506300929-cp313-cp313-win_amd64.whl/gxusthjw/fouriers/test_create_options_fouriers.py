#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        test_create_options_fouriers.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试create_options_fouriers.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/18     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import unittest

from .create_options_fouriers import create_options_fouriers
# 定义 ==============================================================
class TestCreateOptionsFouriers(unittest.TestCase):
    """
    测试create_options_fouriers.py。
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


    def test_create_options_fouriers(self):
        options = create_options_fouriers()
        print(options)
        options.A = 1
        print(options)
        del options.A
        print(options)

        method = getattr(options, 'Border', None)
        print(method)
# 主函数 =============================================================
if __name__ == '__main__':
    unittest.main()
