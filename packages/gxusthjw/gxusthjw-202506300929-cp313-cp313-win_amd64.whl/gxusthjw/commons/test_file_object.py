#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        test_file_object.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试file_object.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/02     finish
# ------------------------------------------------------------------
# 导包 =============================================================
import os
import unittest
from pathlib import Path
from .file_info import FileInfo
from .file_object import FileObject


# 定义 ==============================================================
class TestFileObject(unittest.TestCase):
    """
    测试file_object.py。
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

    # noinspection PyUnresolvedReferences
    def test_file_object_repr(self):
        """
        测试`FileObject`
        """
        file = FileInfo("c:/", "a",
                        "txt", encoding="GBT", C="C",
                        O=20.2, E=True)
        file_object = FileObject(file)

        print(file_object)
        self.assertEqual(file_object.file_full_path, Path("c:\\a.txt"))
        print(str(file_object))

        print(repr(file_object))

        print(file_object.C)
        self.assertEqual(file_object.C, "C")
        print(file_object.E)
        self.assertEqual(file_object.E, True)
        print(file_object.O)
        self.assertEqual(file_object.O, 20.2)

    def test_file_object_make_file(self):
        """
        测试`FileObject`
        """
        this_file = __file__
        print("this file: %s" % this_file)
        this_file_path, this_file_name = os.path.split(this_file)
        print('this file name: %s' % this_file_name)
        print('this_file_path: %s' % this_file_path)

        test_out = "test_out/file_object"

        file_path = os.path.join(this_file_path, "{}/make_a_file2.txt".format(test_out))

        file_object = FileObject(file_path, encoding="GBK", C="C", O=20.2, E=True)

        # file.make_directory()
        file_object.make_file()


# 主函数 ==============================================================
if __name__ == '__main__':
    unittest.main()
