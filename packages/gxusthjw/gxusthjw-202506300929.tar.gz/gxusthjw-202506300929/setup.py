#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        setup.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      gxusthjw包的setup.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/05/08     revise
# ----------------------------------------------------------------
# 编译与打包命令 ====================================================
# 编译扩展模块。
# python setup.py build_ext --inplace
# 打包
# python setup.py sdist bdist_wheel
# python setup.py clean --all
# 发布命令 ========================================================
# python -m twine upload --repository pypi dist/*
# 或
# python -m twine upload --repository testpypi dist/*
# =================================================================
# 导包 =============================================================
import os
import datetime
import numpy as np
from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize


# 定义 ============================================================


# 定义扩展模块
def get_extensions(package_name="gxusthjw"):
    """
    根据包名获取该包下所有的 .pyx 文件，并生成对应的 Extension 对象列表。

    参数:
    package_name (str): 包的名称，默认为 "gxusthjw"。

    返回:
    list: 包含 Extension 对象的列表，每个 Extension 对象代表一个 .pyx 文件。
    """
    # 将包名中的点替换为操作系统特定的路径分隔符，以获取包的目录路径
    package_dir = package_name.replace('.', os.sep)

    # 遍历包目录下的所有文件，筛选出 .pyx 文件，生成 .pyx 文件列表
    pyx_files = [os.path.join(root, f) for root, _, files in os.walk(package_dir)
                 for f in files if f.endswith(".pyx")]

    extensions = []
    for pyx_file in pyx_files:
        # 将 .pyx 文件路径转换为模块名
        module_name = pyx_file.replace(os.sep, ".").replace(".pyx", "")

        # 创建 Extension 对象，将模块名和 .pyx 文件路径传入
        extensions.append(
            Extension(
                module_name,
                [pyx_file],
                include_dirs=[np.get_include()]
            )
        )

    # 返回 Extension 对象列表
    return extensions


# ------------------------------------------------------------------
version = datetime.datetime.now().strftime("%Y%m%d%H%M")
with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="gxusthjw",
    version=version,
    author="gxusthjw",
    author_email="jiweihuang@vip.163.com",
    description="the python packages of gxusthjw.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://codeup.aliyun.com/67ee2f12c4c3142d59ce9a51/Pythons/gxusthjw-packages",
    packages=find_packages(),
    ext_modules=cythonize(get_extensions()),
    # extra_compile_args=['-fopenmp'],
    # extra_link_args=['-fopenmp', '-lopenblas'],
    install_requires=[
        'setuptools',
        'pytest',
        'cython',
        'chardet',
        'openpyxl',
        'numpy',
        'scipy',
        'sympy',
        'pandas',
        'matplotlib',
        'statsmodels',
        'lmfit',
        'pybaselines',
        'ampdLib',
        'pyopencl',
        'pyopengl',
        'pyopengl-accelerate',
        'nmrglue',
        'pyFAI',
    ],
    classifiers=[
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
# ------------------------------------------------------------------
