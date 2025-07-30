#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        benchmark_deriv_gl.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      测试deriv_gl模块中函数或类的性能。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/10     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import timeit
import numpy as np
from deriv_gl import (
    deriv_gl, deriv_gl_0, deriv_gl_1
)


# 定义 ==============================================================
def benchmark_deriv(func, data_y, deriv_order, num_runs=100):
    """
    对指定的导数函数进行性能基准测试。

    :param func: 要测试的导数函数。
    :param data_y: 原始数据数组。
    :param deriv_order: 导数阶数。
    :param num_runs: 运行次数。
    :return: 平均运行时间（秒）。
    """
    elapsed_time = timeit.timeit(lambda: func(data_y, deriv_order), number=num_runs)
    return elapsed_time / num_runs


def main():
    # 设置测试参数
    data_size = 1000  # 数据长度
    deriv_orders = [0.5, 1.0, 1.5, 100, 145, 200, 300]  # 测试不同的导数阶数
    num_runs = 300  # 每个测试运行的次数

    # 生成随机测试数据
    data_y = np.random.rand(data_size)

    print(f"{'Order':>8} | {'deriv_gl_0 (s)':>15} | {'deriv_gl_1 (s)':>15} | {'Ratio':>15}")
    print("-" * 65)

    for order in deriv_orders:
        time = benchmark_deriv(deriv_gl, data_y, order, num_runs)
        time_0 = benchmark_deriv(deriv_gl_0, data_y, order, num_runs)
        time_1 = benchmark_deriv(deriv_gl_1, data_y, order, num_runs)

        print(f"   {order:>8.2f} | {time_0:>15.6f} | {time_1:>15.6f} | {time_0 / time_1:>15.6f}")
        print(f" = {order:>8.2f} | {time:>15.6f} | {time_1:>15.6f} | {time / time_1:>15.6f}")


# 主函数 =============================================================
if __name__ == '__main__':
    main()
