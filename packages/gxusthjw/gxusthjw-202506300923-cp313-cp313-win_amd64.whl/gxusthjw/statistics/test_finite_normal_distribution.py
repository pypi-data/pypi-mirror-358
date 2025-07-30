#!/usr/bin/env python3
# --*-- coding: utf-8 --*--
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        test_finite_normal_distribution.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试finite_normal_distribution.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/27     finish
# ------------------------------------------------------------------
# 导包 =============================================================
import math
import unittest

# noinspection PyUnresolvedReferences
from .finite_normal_distribution import (
    finite_norm_pdf,
    finite_norm_cdf_od,
    finite_norm_cdf,
    FiniteNormalDistribution,
    finite_norm,
)

# ==================================================================

class TestFiniteNormalDistribution(unittest.TestCase):
    """
    测试finite_normal_distribution.py。
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

    def test_finite_norm_pdf(self):
        """
        测试finite_norm_pdf
        """
        self.assertAlmostEqual(finite_norm_pdf(0.3, 0.5, 3, 0.2), 0, delta=1e-6)
        self.assertAlmostEqual(finite_norm_pdf(0.34, 0.5, 3, 0.2), 0.25515, delta=1e-6)
        self.assertAlmostEqual(finite_norm_pdf(0.38, 0.5, 3, 0.2), 1.4336, delta=1e-6)
        self.assertAlmostEqual(finite_norm_pdf(0.42, 0.5, 3, 0.2), 3.24135, delta=1e-6)
        self.assertAlmostEqual(finite_norm_pdf(0.46, 0.5, 3, 0.2), 4.8384, delta=1e-6)
        self.assertAlmostEqual(finite_norm_pdf(0.5, 0.5, 3, 0.2), 5.46875, delta=1e-6)
        self.assertAlmostEqual(finite_norm_pdf(0.54, 0.5, 3, 0.2), 4.8384, delta=1e-6)
        self.assertAlmostEqual(finite_norm_pdf(0.58, 0.5, 3, 0.2), 3.24135, delta=1e-6)
        self.assertAlmostEqual(finite_norm_pdf(0.62, 0.5, 3, 0.2), 1.4336, delta=1e-6)
        self.assertAlmostEqual(finite_norm_pdf(0.66, 0.5, 3, 0.2), 0.25515, delta=1e-6)
        self.assertAlmostEqual(finite_norm_pdf(0.7, 0.5, 3, 0.2), 0, delta=1e-6)

        self.assertEqual(finite_norm_pdf(0.8, 0.5, 3, 0.2), 0)
        self.assertEqual(finite_norm_pdf(0.6, -1, 3, 0.2), 0)
        self.assertEqual(finite_norm_pdf(0.6, -1, 3, -0.2), 0)
        self.assertEqual(finite_norm_pdf(0.66, 0.5, 0, 0.2), 2.5)

    def test_finite_norm_cdf_od(self):
        self.assertAlmostEqual(finite_norm_cdf_od(0.3, 0.5, 3, 0.2), 0, delta=1e-6)
        self.assertAlmostEqual(finite_norm_cdf_od(0.34, 0.5, 3, 0.2), -0.005832, delta=1e-6)
        self.assertAlmostEqual(finite_norm_cdf_od(0.38, 0.5, 3, 0.2), -0.024576, delta=1e-6)
        self.assertAlmostEqual(finite_norm_cdf_od(0.42, 0.5, 3, 0.2), -0.037044, delta=1e-6)
        self.assertAlmostEqual(finite_norm_cdf_od(0.46, 0.5, 3, 0.2), -0.027648, delta=1e-6)
        self.assertAlmostEqual(finite_norm_cdf_od(0.5, 0.5, 3, 0.2), 0, delta=1e-6)
        self.assertAlmostEqual(finite_norm_cdf_od(0.54, 0.5, 3, 0.2), 0.027648, delta=1e-6)
        self.assertAlmostEqual(finite_norm_cdf_od(0.58, 0.5, 3, 0.2), 0.037044, delta=1e-6)
        self.assertAlmostEqual(finite_norm_cdf_od(0.62, 0.5, 3, 0.2), 0.024576, delta=1e-6)
        self.assertAlmostEqual(finite_norm_cdf_od(0.66, 0.5, 3, 0.2), 0.005832, delta=1e-6)
        self.assertAlmostEqual(finite_norm_cdf_od(0.7, 0.5, 3, 0.2), 0, delta=1e-6)

    def test_finite_norm_cdf(self):
        self.assertAlmostEqual(finite_norm_cdf(0.3, 0.5, 3, 0.2), 0, delta=1e-6)
        self.assertAlmostEqual(finite_norm_cdf(0.34, 0.5, 3, 0.2), 0.002728, delta=1e-6)
        self.assertAlmostEqual(finite_norm_cdf(0.38, 0.5, 3, 0.2), 0.033344, delta=1e-6)
        self.assertAlmostEqual(finite_norm_cdf(0.42, 0.5, 3, 0.2), 0.126036, delta=1e-6)
        self.assertAlmostEqual(finite_norm_cdf(0.46, 0.5, 3, 0.2), 0.289792, delta=1e-6)
        self.assertAlmostEqual(finite_norm_cdf(0.5, 0.5, 3, 0.2), 0.5, delta=1e-6)
        self.assertAlmostEqual(finite_norm_cdf(0.54, 0.5, 3, 0.2), 0.710208, delta=1e-6)
        self.assertAlmostEqual(finite_norm_cdf(0.58, 0.5, 3, 0.2), 0.873964, delta=1e-6)
        self.assertAlmostEqual(finite_norm_cdf(0.62, 0.5, 3, 0.2), 0.966656, delta=1e-6)
        self.assertAlmostEqual(finite_norm_cdf(0.66, 0.5, 3, 0.2), 0.997272, delta=1e-6)
        self.assertAlmostEqual(finite_norm_cdf(0.7, 0.5, 3, 0.2), 1, delta=1e-6)

    def test_FiniteNormalDistribution(self):
        print(finite_norm(0, 0.8, math.sqrt(3)).rvs(size=10))
        print(type(finite_norm(0, 0.8, math.sqrt(3)).rvs()))
        print(finite_norm(0, 0.8, math.sqrt(3)).rvs().item())
        print(type(finite_norm(0, 0.8, math.sqrt(3)).rvs().item()))

if __name__ == '__main__':
    unittest.main()