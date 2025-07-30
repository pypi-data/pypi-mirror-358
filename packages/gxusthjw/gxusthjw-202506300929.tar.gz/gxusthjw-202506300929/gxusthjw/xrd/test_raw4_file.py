#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        test_raw4_file.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试raw4_file.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/04     revise
# ------------------------------------------------------------------
# 导包 =============================================================
import os
import unittest

from .raw4_file import (
    read_raw4,
)


# 定义 ==============================================================
class TestRaw4File(unittest.TestCase):
    """
    测试raw4_file.py。
    """

    # region
    # --------------------------------------------------------------------
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

    # --------------------------------------------------------------------
    # endregion

    def test_read_raw4(self):
        # --------------------------------------------------------
        this_file = __file__
        print("this file: %s" % this_file)
        this_file_path, this_file_name = os.path.split(this_file)
        print('this file name: %s' % this_file_name)
        print('this_file_path: %s' % this_file_path)
        # --------------------------------------------------------

        test_data_folder = "test_data/raw4_files"
        test_data_folder_path = os.path.join(this_file_path, test_data_folder)
        # --------------------------------------------------------
        xrd_files = ["1.txt", "2.txt", "3.txt", "4.txt", "5.txt", "6.txt",
                     "7.txt", "8.txt", "9.txt", "10.txt", "11.txt"]
        # ---------------------------------------------------------

        for xrd_file in xrd_files:
            xrd_file_path = os.path.join(test_data_folder_path, xrd_file)
            theta2, intensity = read_raw4(xrd_file_path)
            print(theta2)
            print(intensity)


# 主函数 ==============================================================
if __name__ == '__main__':
    unittest.main()
