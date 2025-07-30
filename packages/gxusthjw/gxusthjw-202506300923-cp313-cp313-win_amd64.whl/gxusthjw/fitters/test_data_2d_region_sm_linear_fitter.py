#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        test_data_2d_region_sm_linear_fitter.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试data_2d_region_sm_linear_fitter.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2024/10/22     revise
# ------------------------------------------------------------------
# 导包 =============================================================
import unittest

import numpy as np
import statsmodels.api as sm
from .data_2d_region_sm_linear_fitter import Data2dRegionSmLinearFitter


# ==================================================================
class TestData2dRegionSmLinearFitter(unittest.TestCase):
    """
    测试data_2d_region_sm_linear_fitter.py。
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



if __name__ == '__main__':
    unittest.main()
