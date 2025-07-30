#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        test_linear_density_unit.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试linear_density_unit.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2023/10/02     revise
#       Jiwei Huang        0.0.1         2024/09/12     revise
# ------------------------------------------------------------------
# 导包 =============================================================
import unittest
from unittest import TestCase

from .linear_density_unit import (Denier, MetricCount, DTex, Tex,
                                  den, dtex, tex, Nm)


# ==================================================================

class TestDenier(TestCase):
    """
    测试Denier对象。
    """

    # ==============================================================
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

    # ==============================================================
    def test_denier(self):
        print(Denier().name)
        self.assertEqual("Denier", Denier().name)
        print(Denier().symbol)
        self.assertEqual("D", Denier().symbol)
        print(Denier().description)
        self.assertEqual("1 gram per 9000 meters.", Denier().description)
        print(Denier().family)
        self.assertEqual("LinearDensityUnit", Denier().family)
        print(Denier().benchmark_unit)
        self.assertEqual(Tex(), Denier().benchmark_unit)

        self.assertEqual(den, Denier())
        self.assertIsInstance(den, Denier)
        self.assertIs(den, Denier())

    def test_convert(self):
        print(den.convert(10, den))
        print(den.convert(10, dtex))
        print(den.convert(10, tex))
        print(den.convert(10, Nm))


class TestTex(TestCase):
    """
    测试Tex对象。
    """

    # ==============================================================
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

    # ==============================================================
    def test_tex(self):
        print(Tex().name)
        print(Tex().symbol)
        print(Tex().description)
        print(Tex().family)
        print(Tex().benchmark_unit)

    def test_convert(self):
        print(tex.convert(10, den))
        print(tex.convert(10, dtex))
        print(tex.convert(10, tex))
        print(tex.convert(10, Nm))


class TestDTex(TestCase):
    """
    测试DTex对象。
    """

    # ==============================================================
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

    # ==============================================================
    def test_dtex(self):
        print(DTex().name)
        print(DTex().symbol)
        print(DTex().description)
        print(DTex().family)
        print(DTex().benchmark_unit)

    def test_convert(self):
        print(dtex.convert(10, den))
        print(dtex.convert(10, dtex))
        print(dtex.convert(10, tex))
        print(dtex.convert(10, Nm))


class TestMetricCount(TestCase):
    """
    测试MetricCount对象。
    """

    # ==============================================================
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

    # ==============================================================
    def test_metric_count(self):
        print(MetricCount().name)
        print(MetricCount().symbol)
        print(MetricCount().description)
        print(MetricCount().family)
        print(MetricCount().benchmark_unit)

    def test_convert(self):
        print(Nm.convert(10, den))
        print(Nm.convert(10, dtex))
        print(Nm.convert(10, tex))
        print(Nm.convert(10, Nm))


if __name__ == '__main__':
    unittest.main()
