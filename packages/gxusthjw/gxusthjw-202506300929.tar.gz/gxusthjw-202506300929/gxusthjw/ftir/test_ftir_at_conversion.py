#!/usr/bin/env python3
# --*-- coding: utf-8 --*--
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        test_ftir_at_conversion.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试ftir_at_conversion.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/15     finish
# ------------------------------------------------------------------
# 导包 =============================================================
import unittest
import os

import numpy as np

from ..commons import read_txt

from .ftir_at_conversion import (
    transmittance_to_absorbance,
    transmittance_to_absorbance2,
    absorbance_to_transmittance,
    absorbance_to_transmittance2
)


# ==================================================================
class TestFtirAtConversion(unittest.TestCase):
    """
    测试ftir_at_conversion.py。
    """

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

    # noinspection PyUnusedLocal
    def test_at_convert(self):
        """
        与OMNIC对比。
        """
        this_path = os.path.abspath(os.path.dirname(__file__))
        test_file_folder = "test_data"
        raw_file_name = "10%.csv"
        omnic_absorbance_file_name0 = "10%-A.csv"
        omnic_absorbance_file_name1 = "10%-A2.csv"

        raw_file = os.path.join(this_path, "{}/{}".format(test_file_folder, raw_file_name))
        omnic_absorbance_file0 = os.path.join(
            this_path, "{}/{}".format(test_file_folder, omnic_absorbance_file_name0)
        )
        omnic_absorbance_file1 = os.path.join(
            this_path, "{}/{}".format(test_file_folder, omnic_absorbance_file_name1)
        )

        raw_x, raw_y = read_txt(raw_file, sep=',', skiprows=2, res_type='ndarrays')
        omnic_absorbance0_x, omnic_absorbance0_y = read_txt(
            omnic_absorbance_file0, sep=',',
            res_type='ndarrays'
        )
        omnic_absorbance1_x, omnic_absorbance1_y = read_txt(
            omnic_absorbance_file1, sep=',',
            res_type='ndarrays'
        )

        absorbance_y = transmittance_to_absorbance(raw_y)
        absorbance_y2 = transmittance_to_absorbance2(raw_y)

        self.assertTrue(np.allclose(absorbance_y,absorbance_y2))
        transmittance_y = absorbance_to_transmittance(absorbance_y)
        transmittance_y2 = absorbance_to_transmittance(absorbance_y2)
        transmittance_y3 = absorbance_to_transmittance2(absorbance_y)
        transmittance_y4 = absorbance_to_transmittance2(absorbance_y2)
        self.assertTrue(np.allclose(transmittance_y, transmittance_y2))
        self.assertTrue(np.allclose(transmittance_y, transmittance_y3))
        self.assertTrue(np.allclose(transmittance_y, transmittance_y4))

if __name__ == '__main__':
    unittest.main()
