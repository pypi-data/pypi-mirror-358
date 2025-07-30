#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        test_xrdml.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试xrdml.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/02     revise
# ------------------------------------------------------------------
# 导包 =============================================================
import unittest
import os
from ..commons import read_txt
from .xrdml_file import (read_xrdml, XrdmlFile)
import numpy as np


# 定义 ==============================================================
class TestXrdml(unittest.TestCase):
    """
    测试xrdml.py。
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

    def test_read_xrdml(self):
        # --------------------------------------------------------
        this_file = __file__
        print("this file: %s" % this_file)
        this_file_path, this_file_name = os.path.split(this_file)
        print('this file name: %s' % this_file_name)
        print('this_file_path: %s' % this_file_path)
        # --------------------------------------------------------

        test_data_folder = "test_data/xrdml"
        test_data_folder_path = os.path.join(this_file_path, test_data_folder)
        # --------------------------------------------------------
        xrd_files = ["1.txt", "2.txt", "3.txt", "4.txt", "5.txt", "6.txt"]
        xrdml_files = ["1.xrdml", "2.xrdml", "3.xrdml", "4.xrdml", "5.xrdml", "6.xrdml"]
        # ---------------------------------------------------------
        test_out_folder = "test_out/xrdml"
        test_out_folder_path = os.path.join(this_file_path, test_out_folder)
        for i in range(len(xrd_files)):
            theta2_0, intensity_0 = read_xrdml(os.path.join(
                test_data_folder_path, xrdml_files[i]),
                head_discarded_num_points=3,
                is_out_file=True,
                out_file=os.path.join(test_out_folder_path, f"{i}.xy"))
            theta2_0_r, intensity_0_r = read_txt(os.path.join(
                test_data_folder_path, xrd_files[i]),
                skiprows=1,
                res_type="ndarrays")
            self.assertTrue(np.allclose(theta2_0, theta2_0_r))
            self.assertTrue(np.allclose(intensity_0, intensity_0_r))

    def test_XrdmlFile(self):
        # --------------------------------------------------------
        this_file = __file__
        print("this file: %s" % this_file)
        this_file_path, this_file_name = os.path.split(this_file)
        print('this file name: %s' % this_file_name)
        print('this_file_path: %s' % this_file_path)
        # --------------------------------------------------------

        test_data_folder = "test_data/xrdml"
        test_data_folder_path = os.path.join(this_file_path, test_data_folder)
        # --------------------------------------------------------
        xrdml_files = ["1.xrdml", "2.xrdml", "3.xrdml", "4.xrdml", "5.xrdml", "6.xrdml"]
        # ---------------------------------------------------------
        test_out_folder = "test_out/xrdml"
        test_out_folder_path = os.path.join(this_file_path, test_out_folder)
        for i in range(len(xrdml_files)):
            xrdml_file = os.path.join(test_data_folder_path, xrdml_files[i])
            xrdml = XrdmlFile(xrdml_file)
            xrdml.read(reset_data=True)
            xrdml.preprocessing(head_discarded_num_points=3,
                                theta2_round=6,
                                reset_data=True)
            xrdml.to_file(separator="\t", out_file=os.path.join(test_out_folder_path, f"{i}.raw"))


# 主函数 ==============================================================
if __name__ == '__main__':
    unittest.main()
