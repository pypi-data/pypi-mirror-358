#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        test_pdf2png_core.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试pdf2png_core.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/13     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import unittest
import os
from pathlib import Path
from .pdf2png_core import (
    mkdir,
    pdf2img
)

from ..commons import (
    folder_cleanup
)


# 定义 ==============================================================
class TestPdf2pngCore(unittest.TestCase):
    """
    测试pdf2png_core.py。
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

    def test_mkdir(self):
        path = "."
        base_name = "a"
        ext = ".txt"

        print(mkdir(path, base_name))
        print(mkdir(path, base_name, ext))

        # ------------------------------------------------------------------
        this_file = __file__
        print("this file: %s" % this_file)
        this_file_path, this_file_name = os.path.split(this_file)
        print('this file name: %s' % this_file_name)
        print('this file path: %s' % this_file_path)
        # ------------------------------------------------------------------
        test_out = "test_out"
        path = os.path.join(this_file_path, test_out)

        print(mkdir(path, base_name))
        os.makedirs(mkdir(path, base_name), exist_ok=True)
        print(mkdir(path, base_name, ext))

        folder_cleanup(path, target_type="dir")

    def test_pdf2img(self):
        # ------------------------------------------------------------------
        this_file = __file__
        print("this file: %s" % this_file)
        this_file_path, this_file_name = os.path.split(this_file)
        print('this file name: %s' % this_file_name)
        print('this file path: %s' % this_file_path)
        # ------------------------------------------------------------------
        test_data = "test_data"
        test_file_names = ['a.pdf', 'b.pdf', 'c.pdf']

        test_file_a = os.path.join(this_file_path, test_data, test_file_names[0])
        test_file_b = os.path.join(this_file_path, test_data, test_file_names[1])
        test_file_c = os.path.join(this_file_path, test_data, test_file_names[2])

        pdf2img(test_file_a, 2, 'png')
        pdf2img(test_file_b, 9, 'png')
        pdf2img(test_file_c, 6, 'png')

        folder_cleanup(os.path.join(this_file_path, test_data), target_type="dir")

        test_out = Path(this_file_path) / "test_out"
        pdf2img(test_file_a, 2, 'png', out_path=test_out)
        pdf2img(test_file_b, 9, 'png', out_path=test_out)
        pdf2img(test_file_c, 6, 'png', out_path=test_out)

        folder_cleanup(test_out, target_type="dir")


# 主函数 =============================================================
if __name__ == '__main__':
    unittest.main()
