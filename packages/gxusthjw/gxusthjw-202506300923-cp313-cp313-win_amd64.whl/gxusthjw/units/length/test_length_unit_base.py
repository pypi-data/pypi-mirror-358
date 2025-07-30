#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        test_length_unit_base.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试length_unit_base.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2024/09/14     revise
# ------------------------------------------------------------------
# 导包 =============================================================
import unittest

# noinspection PyUnresolvedReferences
from .length_unit_base import (LengthUnit,
                               MetricLengthUnit,
                               Kilometer,
                               Meter,
                               Decimeter,
                               Centimeter,
                               Millimeter,
                               Micrometer,
                               Nanometer,
                               Picometer,
                               Angstrom,
                               km,
                               m,
                               dm,
                               cm,
                               mm,
                               µm,
                               nm,
                               pm,
                               Å)


# ==================================================================
class TestLengthUnitBase(unittest.TestCase):
    """
    测试length_unit_base.py。
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

    def test_kilometer(self):
        km0 = Kilometer()
        self.assertEqual(id(km), id(km0))

        unit = km
        self.assertEqual(unit.name, "Kilometer")
        self.assertEqual(unit.symbol, "km")


if __name__ == '__main__':
    unittest.main()
