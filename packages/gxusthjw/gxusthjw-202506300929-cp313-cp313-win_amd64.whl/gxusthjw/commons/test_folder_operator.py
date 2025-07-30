#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        test_folder_operator.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试folder_operator.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/17     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import unittest
import os

from .folder_operator import (
    folder_cleanup,
    folder_create,
)


# 定义 ==============================================================
class TestFolderOperator(unittest.TestCase):
    """
    测试folder_operator.py。
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

    def test_folder_create_cleanup(self):
        # ------------------------------------------------------------------
        this_file = __file__
        print("this file: %s" % this_file)
        this_file_path, this_file_name = os.path.split(this_file)
        print('this file name: %s' % this_file_name)
        print('this file path: %s' % this_file_path)
        # ------------------------------------------------------------------

        test_folder = "test_data/folder_operator"
        test_folder_path = os.path.join(this_file_path, test_folder)

        folder_create(test_folder_path, ["a", "b", "c"],
                      {"a.txt": "1.txt", "b.txt": "2", "c.txt": "3"})

        folder_create(test_folder_path, ["a1", "b2", "c3"])
        folder_create(test_folder_path,
                      files = {"a1.txt": "1.txt", "b2.txt": "2", "c3.txt": "3"})

        folder_cleanup(test_folder_path)
# 主函数 =============================================================
if __name__ == '__main__':
    unittest.main()
