#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        test_fitting_statistics.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试fitting_statistics.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/27     finish
# -----------------------------------------------------------------
# 导包 =============================================================
import os
import unittest

import numpy as np

from lmfit.models import (
    ExponentialModel, GaussianModel
)


from .fitting_statistics import (
    FittingStatistics,
    rsquared,
    chisqr,
    aic,
    bic,
    redchi,
    chisqr_p
)


# 定义 =============================================================

class TestFittingStatistics(unittest.TestCase):
    """
    测试fitting_statistics.py
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
    # noinspection DuplicatedCode,PyTestUnpassedFixture
    def test_statistics(self):
        """
        测试统计量。
        """
        # <examples/doc_nistgauss2.py>
        this_file = os.path.abspath(os.path.dirname(__file__))
        this_path, _ = os.path.split(this_file)
        test_file = os.path.join(this_file, 'test_data/fitting_statistics/NIST_Gauss2.dat')
        print(this_file)
        print(this_path)
        print(test_file)
        dat = np.loadtxt(test_file)
        x = dat[:, 1]
        y = dat[:, 0]

        exp_mod = ExponentialModel(prefix='exp_')
        gauss1 = GaussianModel(prefix='g1_')
        gauss2 = GaussianModel(prefix='g2_')

        def index_of(arrval, value):
            """Return index of array *at or below* value."""
            if value < min(arrval):
                return 0
            return max(np.where(arrval <= value)[0])

        ix1 = index_of(x, 75)
        ix2 = index_of(x, 135)
        ix3 = index_of(x, 175)

        pars1 = exp_mod.guess(y[:ix1], x=x[:ix1])
        pars2 = gauss1.guess(y[ix1:ix2], x=x[ix1:ix2])
        pars3 = gauss2.guess(y[ix2:ix3], x=x[ix2:ix3])

        pars = pars1 + pars2 + pars3
        mod = gauss1 + gauss2 + exp_mod

        out = mod.fit(y, pars, x=x)

        print(out.fit_report(min_correl=0.5))

        # -------------------------------------------------------
        fs = FittingStatistics(y, out.best_fit, out.nvarys, x)

        self.assertEqual(fs.rsquared, out.rsquared)
        self.assertEqual(fs.rsquared, rsquared(y, out.best_fit))
        print("fs.rsquared={},out.rsquared={},rsquared = {}".format(
            fs.rsquared, out.rsquared, rsquared(y, out.best_fit)))

        self.assertEqual(fs.chisqr, out.chisqr)
        self.assertEqual(fs.chisqr, chisqr(y, out.best_fit))
        print("fs.chisqr={},out.chisqr={},chisqr={}".format(
            fs.chisqr, out.chisqr, chisqr(y, out.best_fit)))
        print(f"chisqr_p={chisqr_p(y, out.best_fit, out.nvarys)}")

        self.assertEqual(fs.aic, out.aic)
        self.assertEqual(fs.aic, aic(y, out.best_fit, out.nvarys))
        print("fs.aic={},out.aic={},aic={}".format(
            fs.aic, out.aic, aic(y, out.best_fit, out.nvarys)))

        self.assertEqual(fs.bic, out.bic)
        self.assertEqual(fs.bic, bic(y, out.best_fit, out.nvarys))
        print("fs.bic={},out.bic={},bic={}".format(
            fs.bic, out.bic, bic(y, out.best_fit, out.nvarys)))

        self.assertEqual(fs.redchi, out.redchi)
        self.assertEqual(fs.redchi, redchi(y, out.best_fit, out.nvarys))
        print("fs.redchi={},out.redchi={},redchi={}".format(
            fs.redchi, out.redchi, redchi(y, out.best_fit, out.nvarys)))
        # -------------------------------------------------------

    def test_exceptions(self):
        y_ture = np.array([1, 2, 3, 4, 5])
        y_pred = np.array([1, 2, 3, 4, 5, 6])
        x = np.array([1, 2, 3, 4, 5])
        x_r = np.array([1, 2, 3, 4, 5, 6])
        nvars_fitted = 3
        nvars_fitted_r = 7

        with self.assertRaises(ValueError) as context:
            rsquared(y_ture, y_pred)
        print(context.exception)
        self.assertEqual("y_true and y_pred must have the same shape,"
                         "but got y_true.shape = (5,), y_pred.shape = (6,).",
                         str(context.exception))

        with self.assertRaises(ValueError) as context:
            chisqr(y_ture, y_pred)
        print(context.exception)
        self.assertEqual("y_true and y_pred must have the same shape,"
                         "but got y_true.shape = (5,), y_pred.shape = (6,).",
                         str(context.exception))

        with self.assertRaises(ValueError) as context:
            chisqr_p(y_ture, y_pred, nvars_fitted)
        print(context.exception)
        self.assertEqual("y_true and y_pred must have the same shape,"
                         "but got y_true.shape = (5,), y_pred.shape = (6,).",
                         str(context.exception))

        with self.assertRaises(ValueError) as context:
            redchi(y_ture, y_pred, nvars_fitted)
        print(context.exception)
        self.assertEqual("y_true and y_pred must have the same shape,"
                         "but got y_true.shape = (5,), y_pred.shape = (6,).",
                         str(context.exception))

        with self.assertRaises(ValueError) as context:
            aic(y_ture, y_pred, nvars_fitted)
        print(context.exception)
        self.assertEqual("y_true and y_pred must have the same shape,"
                         "but got y_true.shape = (5,), y_pred.shape = (6,).",
                         str(context.exception))

        with self.assertRaises(ValueError) as context:
            bic(y_ture, y_pred, nvars_fitted)
        print(context.exception)
        self.assertEqual("y_true and y_pred must have the same shape,"
                         "but got y_true.shape = (5,), y_pred.shape = (6,).",
                         str(context.exception))

        with self.assertRaises(ValueError) as context:
            FittingStatistics(y_ture, y_pred, nvars_fitted)
        print(context.exception)
        self.assertEqual("y_true and y_pred must have the same shape,"
                         "but got y_true.shape = (5,), y_pred.shape = (6,).",
                         str(context.exception))

        chisqr_p(y_ture, y_ture, nvars_fitted_r)

        with self.assertRaises(ValueError) as context:
            redchi(y_ture, y_ture, nvars_fitted_r)
        print(context.exception)
        self.assertEqual("Expected nvars_fitted < 5, but got nvars_fitted = 7.",
                         str(context.exception))

        with self.assertRaises(ValueError) as context:
            aic(y_ture, y_ture, nvars_fitted_r)
        print(context.exception)
        self.assertEqual("Expected nvars_fitted < 5, but got nvars_fitted = 7.",
                         str(context.exception))

        with self.assertRaises(ValueError) as context:
            bic(y_ture, y_ture, nvars_fitted_r)
        print(context.exception)
        self.assertEqual("Expected nvars_fitted < 5, but got nvars_fitted = 7.",
                         str(context.exception))

        with self.assertRaises(ValueError) as context:
            FittingStatistics(y_ture, y_ture, nvars_fitted_r)
        print(context.exception)
        self.assertEqual("Expected nvars_fitted < 5, but got nvars_fitted = 7.",
                         str(context.exception))

        FittingStatistics(y_ture, y_ture, nvars_fitted, x)
        with self.assertRaises(ValueError) as context:
            FittingStatistics(y_ture, y_ture, nvars_fitted, x_r)
        print(context.exception)
        self.assertEqual("x and y_true must have the same shape,"
                         "but got y_true.shape = (5,), x.shape = (6,).",
                         str(context.exception))


if __name__ == '__main__':
    unittest.main()
