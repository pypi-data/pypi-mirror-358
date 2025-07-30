#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        tests.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“测试”相关的函数和类。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/09     revise
# ------------------------------------------------------------------
# 导包 ==============================================================

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Define functions and classes related to 'testing'.
"""

__all__ = [
    'run_tests'
]


# 定义 ==============================================================
def run_tests(start_dir='.'):
    """
    运行指定路径下的所有测试。

        使用方式:
            > import gxusthjw
            > gxusthjw.run_tests()  # 使用默认路径
            > gxusthjw.run_tests('/path/to/test_directory')  # 指定测试路径

    :param start_dir: 测试用例所在的目录路径，默认为当前目录.
    :return:
    """
    import unittest
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(start_dir)
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(test_suite)
