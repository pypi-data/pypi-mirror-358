#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        test_file_path.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试file_path.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/02     revise
# ------------------------------------------------------------------
# 导包 =============================================================
import os
import unittest

from .file_path import (
    sep_file_path,
    join_file_path,
    list_files_with_suffix,
    print_files_and_folders,
    list_files_and_folders,
    get_this_path,
    get_project_path,
    get_root_path
)


# ==================================================================
class TestFilePath(unittest.TestCase):
    """
    测试file_path.py。
    """

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
    def test_file_path(self):
        """
        测试：sep_file_path函数。
        """
        self.assertEqual(sep_file_path("/path/to/directory/file.txt"), ("/path/to/directory", "file", ".txt"))
        self.assertEqual(sep_file_path("/path/to/directory/file"), ("/path/to/directory", "file", ""))
        self.assertEqual(sep_file_path("/path/to/directory/"), ("/path/to/directory", "", ""))
        self.assertEqual(sep_file_path("/path/to/directory/.hiddenfile"),
                         ("/path/to/directory", "", ".hiddenfile"))
        self.assertEqual(sep_file_path("/path/to/directory/file.txt", with_dot_in_ext=False),
                         ("/path/to/directory", "file", "txt"))
        self.assertEqual(sep_file_path("/path/to/directory/file", with_dot_in_ext=False),
                         ("/path/to/directory", "file", ""))
        self.assertEqual(sep_file_path("/path/to/directory/.hiddenfile", with_dot_in_ext=False),
                         ("/path/to/directory", "", "hiddenfile"))

        path = os.path.abspath(os.path.dirname(__file__))
        test_folder = "test_data"
        path = os.path.join(path, test_folder)
        file_name = "b"
        file_type = ".pdf"
        print(join_file_path(path, file_name, file_type))
        print(sep_file_path(join_file_path(path, file_name, file_type),
                            with_dot_in_ext=False))

        path = 'c:/a\\b.pdf'
        file_path, file_name, file_ext = sep_file_path(path)
        print(file_path)
        print(file_name)
        print(file_ext)
        self.assertEqual("c:/a", file_path)
        self.assertEqual("b", file_name)
        self.assertEqual(".pdf", file_ext)

    def test_join_file_path(self):
        """
        测试：join_file_path函数。
        """
        path = "c:/a"
        file_name = "b"
        file_type = ".pdf"
        print(join_file_path(path, file_name, file_type))
        self.assertEqual('c:/a\\b.pdf', join_file_path(path, file_name, file_type))
        file_type = "pdf"
        print(join_file_path(path, file_name, file_type))
        self.assertEqual('c:/a\\b.pdf', join_file_path(path, file_name, file_type))

        file_type = " pdf "
        print(join_file_path(path, file_name, file_type))
        self.assertEqual('c:/a\\b.pdf', join_file_path(path, file_name, file_type))

    def test_list_files_and_folders(self):
        """
        测试：list_files_and_folders函数。
        """
        folders, files = list_files_and_folders(get_root_path())
        print(folders)
        print(files)

    def test_print_files_and_folders(self):
        """
        测试：print_files_and_folders函数。
        """
        print_files_and_folders(get_root_path())
        print_files_and_folders(get_root_path(), include_subdirs=False)

    def test_list_files_with_suffix(self):
        """
        测试：list_files_with_suffix函数。
        """
        path = get_this_path()
        test_data_path = os.path.join(path, "test_data")
        files = list_files_with_suffix(path=test_data_path)
        print("\n".join(files))
        files = list_files_with_suffix(path=test_data_path, include_subdirs=False)
        print("\n".join(files))

    def test_get_this_path(self):
        """
        测试：get_this_path函数。
        """
        print(get_this_path())

    def test_get_project_path(self):
        """
        测试：get_project_path函数。
        """
        print(get_project_path())

    def test_get_root_path(self):
        """
        测试：get_root_path函数。
        """
        print(get_root_path())


if __name__ == '__main__':
    unittest.main()
