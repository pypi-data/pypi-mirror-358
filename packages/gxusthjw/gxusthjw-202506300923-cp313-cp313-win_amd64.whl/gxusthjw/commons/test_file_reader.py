#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        test_file_reader.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试file_reader.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/03     finish
# ------------------------------------------------------------------
# 导包 =============================================================
import unittest
import os

import numpy as np

from .file_reader import (
    read_txt, _read_text_df, read_text
)


# 定义 ==============================================================
class TestFileReader(unittest.TestCase):
    """
    测试file_reader.py。
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

    def test_read_txt(self):
        # ------------------------------------------------------------------
        this_file = __file__
        print("this file: %s" % this_file)
        this_file_path, this_file_name = os.path.split(this_file)
        print('this file name: %s' % this_file_name)
        print('this file path: %s' % this_file_path)
        # ------------------------------------------------------------------
        test_file_folder = "test_data/file_reader"
        test_file_name = "file1.csv"
        test_file = os.path.join(this_file_path, test_file_folder, test_file_name)
        print(test_file)
        # ------------------------------------------------------------------
        data1 = read_txt(test_file, skiprows=3, sep=",", res_type='list')
        print(data1)

    def test_read_text_df(self):
        # ------------------------------------------------------------------
        this_file = __file__
        print("this file: %s" % this_file)
        this_file_path, this_file_name = os.path.split(this_file)
        print('this file name: %s' % this_file_name)
        print('this file path: %s' % this_file_path)
        # ------------------------------------------------------------------
        test_file_folder = "test_data/file_reader"
        test_file_name = "file1.csv"
        test_file = os.path.join(this_file_path, test_file_folder, test_file_name)
        print(test_file)
        # ------------------------------------------------------------------
        data1 = read_txt(test_file, skiprows=3, sep=",", res_type='dataframe')
        print(data1)
        data2 = _read_text_df(test_file, skiprows=3, sep=",")
        print(data2)
        # ------------------------------------------------------------------
        test_file_name2 = "file2.csv"
        test_file2 = os.path.join(this_file_path, test_file_folder, test_file_name2)
        print(test_file2)
        # ------------------------------------------------------------------
        data3 = _read_text_df(test_file2, skiprows=3, sep=",")
        print(data3)

    def test_read_text(self):
        # ------------------------------------------------------------------
        this_file = __file__
        print("this file: %s" % this_file)
        this_file_path, this_file_name = os.path.split(this_file)
        print('this file name: %s' % this_file_name)
        print('this file path: %s' % this_file_path)
        # ------------------------------------------------------------------
        test_file_folder = "test_data/file_reader"
        test_file_name = "file1.csv"
        test_file = os.path.join(this_file_path, test_file_folder, test_file_name)
        print(test_file)
        test_file_name2 = "file2.csv"
        test_file2 = os.path.join(this_file_path, test_file_folder, test_file_name2)
        print(test_file2)
        # ------------------------------------------------------------------
        data1 = read_txt(test_file, skiprows=3, sep=",", res_type='dataframe')
        print(data1)
        data2 = read_text(test_file2, skiprows=3, sep=",", res_type='dataframe',
                          types={0: np.intp, 1: float, })
        print(data2)
        # ------------------------------------------------------------------
        data2 = read_text(test_file2, skiprows=3, sep=",", res_type='ndarrays',
                          types={0: np.intp, 1: float, })
        print(data2)
        # ------------------------------------------------------------------
        data2 = read_text(test_file2, skiprows=3, sep=",",
                          types={0: np.intp, 1: float, })
        print(data2.get(3))
        # ------------------------------------------------------------------
        data2 = read_text(test_file2, skiprows=3, sep=",",
                          types={0: np.intp, 1: float, })
        print(data2.get(4))
        # ------------------------------------------------------------------
        data2 = read_text(test_file2, skiprows=3, sep=",", res_type='dict',
                          types={0: np.intp, 1: float, })
        print(data2)
        # ------------------------------------------------------------------
        data2 = read_text(test_file2, skiprows=3, sep=",", res_type='list',
                          types={0: np.intp, 1: float, })
        print(data2)

    def test_read_text2(self):
        # ------------------------------------------------------------------
        this_file = __file__
        print("this file: %s" % this_file)
        this_file_path, this_file_name = os.path.split(this_file)
        print('this file name: %s' % this_file_name)
        print('this file path: %s' % this_file_path)
        # ------------------------------------------------------------------
        test_file_folder = "test_data/file_reader"
        test_file_name = "file3.txt"
        test_file = os.path.join(this_file_path, test_file_folder, test_file_name)
        print(test_file)
        # ------------------------------------------------------------------
        data = read_text(test_file, skiprows=4, types={0: np.intp, 1: float, },
                         names={0: "a", 1: "b", }, res_type="dataframe")
        print(data)
        # ------------------------------------------------------------------
        data = read_text(test_file, skiprows=4, types={0: np.intp, 1: float, },
                         names={0: "a", 1: "b", }, res_type="dict")
        print(data)
        # ------------------------------------------------------------------
        data = read_text(test_file, skiprows=4, types={0: np.intp, 1: float, },
                         names={0: "a", 1: "b", }, res_type="list")
        print(data)
        # ------------------------------------------------------------------
        data = read_text(test_file, skiprows=4, types={0: np.intp, 1: float, },
                         names={0: "a", 1: "b", }, res_type="datatable")
        print(data.get(2))
        # ------------------------------------------------------------------
        data = read_text(test_file, skiprows=4, types={0: np.intp, 1: float, },
                         names={0: "a", 1: "b", })
        print(data.get(1))


# 主函数 ==============================================================
if __name__ == '__main__':
    unittest.main()
