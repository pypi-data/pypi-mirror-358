#!/usr/bin/env python3
# --*-- coding: utf-8 --*--
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        bruker_nmr.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义用于处理bruker的NMR数据的函数和类。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/16     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import os.path
import nmrglue as ng
import nmrglue.fileio.fileiobase

# 定义 ============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defines functions and classes for processing Bruker NMR data.
"""

__all__ = [
    'read_bruker',
    'read_pdata_bruker',
    'ppm_intensity_bruker',
    'NmrBruker'
]


# ==================================================================

def read_bruker(data_base_path=".", data_folder="1",
                bin_file=None, acqus_files=None, pprog_file=None,
                shape=None, cplex=None, big=None, isfloat=None,
                read_pulseprogram=True, read_acqus=True,
                procs_files=None, read_procs=True):
    """
    读取指定路径下的Bruker NMR数据文件。

        该函数是对nmrglue.read函数的封装。

    :param data_base_path: Bruker NMR 数据文件所在文件夹的父路径。
    :param data_folder: Bruker NMR 数据文件所在的文件夹。
    :param bin_file: str, optional，二进制文件在目录中的文件名。若为 None，则使用标准文件。
    :param acqus_files: list, optional，目录中 acqus 参数文件的文件名列表。若为 None，则使用标准文件。
    :param pprog_file: str, optional，脉冲程序文件在目录中的文件名。若为 None，则使用标准文件。
    :param shape: tuple, optional，结果数据的形状（维度）。若为 None，则根据谱图参数自动推测形状。
    :param cplex: bool, optional，若为 True，表示直接维度是复数；False 表示不是复数。
                  若为 None，则根据谱图参数推测正交检测状态。
    :param big: bool or None, optional，二进制文件的字节序（endianness）。
                True 表示大端序（big-endian），False 表示小端序（little-endian），
                None 表示从 acqus 文件中自动判断。
    :param isfloat: bool or None, optional，二进制文件的数据类型。
                 True 表示 float64，False 表示 int32。
                 若为 None，则从 acqus 文件中自动判断数据类型。
    :param read_pulseprogram: bool, optional，若为 True，则读取脉冲程序；
                              若为 False，则跳过读取。
    :param read_acqus: bool, optional，若为 True，则读取 acqus 文件；若为 False，则跳过读取。
    :param procs_files: list, optional，目录中 procs 参数文件的文件名列表。若为 None，则使用标准文件。
    :param read_procs: bool, optional，若为 True，则读取 procs 文件；若为 False，则跳过读取。
    :return: (dic,data)
            dic: dict，一个字典，包含从 Bruker 文件中读取的所有参数（如采集参数、仪器设置等）。
            data : ndarray，一个 NumPy 的 n 维数组，保存了读取的 NMR 实验数据。
    """
    return ng.bruker.read(
        dir=os.path.join(data_base_path, data_folder),
        bin_file=bin_file, acqus_files=acqus_files,
        pprog_file=pprog_file, shape=shape, cplex=cplex,
        big=big, isfloat=isfloat, read_pulseprogram=read_pulseprogram,
        read_acqus=read_acqus, procs_files=procs_files,
        read_procs=read_procs
    )


def read_pdata_bruker(data_base_path=".", pdata_folder="1\\pdata\\1",
                      bin_files=None, procs_files=None, read_procs=True,
                      acqus_files=None, read_acqus=True, scale_data=True,
                      shape=None, submatrix_shape=None, all_components=False,
                      big=None, isfloat=None):
    """
    读取指定路径下的预处理过的Bruker NMR数据文件。

        pdata表示预处理过的Bruker NMR数据文件。

        在 TopSpin 和其他程序中，这些数据通常通过除以 2 ** -NC_proc 进行缩放，
        其中 NC_proc 定义在 procs 文件中。
        要实现这种缩放，可以将 scale_data 参数设为 True。

    :param data_base_path: Bruker NMR 数据文件所在文件夹的父路径。
    :param pdata_folder: pdata所在的文件夹路径。
    :param bin_files: list of str, optional，目录中的二进制文件名列表。若为 None，则使用标准文件名。
    :param procs_files: list, optional，目录中 procs 参数文件的文件名列表。若为 None，则使用标准文件名。
    :param read_procs: bool, optional，若为 True，则读取 procs 文件；若为 False，则跳过读取。
    :param acqus_files:list, optional，目录中 acqus 参数文件的文件名列表。若为 None，则使用标准文件名。
    :param read_acqus: bool, optional，若为 True，则读取 acqus 文件；若为 False，则跳过读取。
    :param scale_data: bool, optional，若为 True（默认值），则根据 procs 文件中定义的参数对数据进行缩放。
                                      通常应启用此选项。若为 False，则返回原始文件中的数据。
    :param shape: tuple, optional，返回数据的形状（维度）。若为 None，则从 procs 文件中推测数据形状。
    :param submatrix_shape: tuple, optional，用于多维数据（如二维、三维）的子矩阵形状。
                                若为 None，则从 procs 文件的元数据中推测形状。
    :param all_components:bool，若为 True，则返回所有四象限分量（quadrature components）组成的列表；
                                若为 False，则只返回实数部分（如 1r、2rr、3rrr 等）。
    :param big: bool or None, optional，表示二进制文件的字节序（endianness）。True 表示大端序（big-endian），
                             False 表示小端序（little-endian），None 表示从 procs 文件中自动判断。
    :param isfloat:bool or None, optional，二进制文件的数据类型。
                        True 表示 float64，False 表示 int32。
                        若为 None，则从 procs 文件中自动判断数据类型。
    :return: (dict,data)
            1. dict,包含 Bruker 参数的字典。
            2. ndarray 或 list, NMR 数据数组。如果 all_components 为 True，则返回一个包含每个象限分量的数组列表。
    """
    return ng.bruker.read_pdata(
        dir=os.path.join(data_base_path, pdata_folder),
        bin_files=bin_files, procs_files=procs_files,
        read_procs=read_procs, acqus_files=acqus_files,
        read_acqus=read_acqus, scale_data=scale_data,
        shape=shape, submatrix_shape=submatrix_shape,
        all_components=all_components,
        big=big, isfloat=isfloat
    )


def ppm_intensity_bruker(data_base_path=".", pdata_folder="1\\pdata\\1",
                         bin_files=None, procs_files=None, read_procs=True,
                         acqus_files=None, read_acqus=True, scale_data=True,
                         shape=None, submatrix_shape=None, all_components=False,
                         big=None, isfloat=None):
    """
    读取指定路径下的预处理过的Bruker NMR数据文件，并返回(ppm,intensity)数据。

    :param data_base_path: Bruker NMR 数据文件所在文件夹的父路径。
    :param pdata_folder: pdata所在的文件夹路径。
    :param bin_files: list of str, optional，目录中的二进制文件名列表。若为 None，则使用标准文件名。
    :param procs_files: list, optional，目录中 procs 参数文件的文件名列表。若为 None，则使用标准文件名。
    :param read_procs: bool, optional，若为 True，则读取 procs 文件；若为 False，则跳过读取。
    :param acqus_files:list, optional，目录中 acqus 参数文件的文件名列表。若为 None，则使用标准文件名。
    :param read_acqus: bool, optional，若为 True，则读取 acqus 文件；若为 False，则跳过读取。
    :param scale_data: bool, optional，若为 True（默认值），则根据 procs 文件中定义的参数对数据进行缩放。
                                      通常应启用此选项。若为 False，则返回原始文件中的数据。
    :param shape: tuple, optional，返回数据的形状（维度）。若为 None，则从 procs 文件中推测数据形状。
    :param submatrix_shape: tuple, optional，用于多维数据（如二维、三维）的子矩阵形状。
                                若为 None，则从 procs 文件的元数据中推测形状。
    :param all_components:bool，若为 True，则返回所有四象限分量（quadrature components）组成的列表；
                                若为 False，则只返回实数部分（如 1r、2rr、3rrr 等）。
    :param big: bool or None, optional，表示二进制文件的字节序（endianness）。True 表示大端序（big-endian），
                             False 表示小端序（little-endian），None 表示从 procs 文件中自动判断。
    :param isfloat:bool or None, optional，二进制文件的数据类型。
                        True 表示 float64，False 表示 int32。
                        若为 None，则从 procs 文件中自动判断数据类型。
    :return: (ppm,intensity)
            1. NMR的ppm数据。
            2. NMR的intensity数据。
    """
    dic, data = read_pdata_bruker(
        data_base_path=data_base_path, pdata_folder=pdata_folder,
        bin_files=bin_files, procs_files=procs_files,
        read_procs=read_procs, acqus_files=acqus_files,
        read_acqus=read_acqus, scale_data=scale_data,
        shape=shape, submatrix_shape=submatrix_shape,
        all_components=all_components,
        big=big, isfloat=isfloat
    )
    udic = ng.bruker.guess_udic(dic, data)
    uc = ng.fileio.fileiobase.uc_from_udic(udic)
    ppm_scale = uc.ppm_scale()
    return ppm_scale, data


class NmrBruker(object):
    """
    类`NmrBruker`表征`Bruker NMR数据文件`。
    """

    def __init__(self, data_base_path=".", data_folder="1", pdata_folder="1\\pdata\\1"):
        """

        :param data_base_path: Bruker NMR 数据文件所在文件夹的父路径。
        :param data_folder: Bruker NMR 数据文件所在的文件夹。
        :param pdata_folder: pdata所在的文件夹路径。
        """
        self.__data_base_path = data_base_path
        self.__data_path = os.path.join(self.__data_base_path, data_folder)
        self.__pdata_path = os.path.join(self.__data_base_path, pdata_folder)

    @property
    def data_base_path(self):
        """
        获取Bruker NMR 数据文件所在文件夹的父路径。

        :return: Bruker NMR 数据文件所在文件夹的父路径。
        """
        return self.__data_base_path

    @property
    def data_path(self):
        """
        获取Bruker NMR 数据文件所在的文件夹。

        :return: Bruker NMR 数据文件所在的文件夹。
        """
        return self.__data_path

    @property
    def pdata_path(self):
        """
        获取pdata所在的文件夹路径。

        :return: pdata所在的文件夹路径。
        """
        return self.__pdata_path

    def read_data(self, bin_file=None, acqus_files=None, pprog_file=None,
                  shape=None, cplex=None, big=None, isfloat=None,
                  read_pulseprogram=True, read_acqus=True,
                  procs_files=None, read_procs=True):
        """
        读取指定路径下的Bruker NMR数据文件。

            该函数是对nmrglue.read函数的封装。

        :param bin_file: str, optional，二进制文件在目录中的文件名。若为 None，则使用标准文件。
        :param acqus_files: list, optional，目录中 acqus 参数文件的文件名列表。若为 None，则使用标准文件。
        :param pprog_file: str, optional，脉冲程序文件在目录中的文件名。若为 None，则使用标准文件。
        :param shape: tuple, optional，结果数据的形状（维度）。若为 None，则根据谱图参数自动推测形状。
        :param cplex: bool, optional，若为 True，表示直接维度是复数；False 表示不是复数。
                      若为 None，则根据谱图参数推测正交检测状态。
        :param big: bool or None, optional，二进制文件的字节序（endianness）。
                    True 表示大端序（big-endian），False 表示小端序（little-endian），
                    None 表示从 acqus 文件中自动判断。
        :param isfloat: bool or None, optional，二进制文件的数据类型。
                     True 表示 float64，False 表示 int32。
                     若为 None，则从 acqus 文件中自动判断数据类型。
        :param read_pulseprogram: bool, optional，若为 True，则读取脉冲程序；
                                  若为 False，则跳过读取。
        :param read_acqus: bool, optional，若为 True，则读取 acqus 文件；若为 False，则跳过读取。
        :param procs_files: list, optional，目录中 procs 参数文件的文件名列表。若为 None，则使用标准文件。
        :param read_procs: bool, optional，若为 True，则读取 procs 文件；若为 False，则跳过读取。
        :return: (dic,data)
                dic: dict，一个字典，包含从 Bruker 文件中读取的所有参数（如采集参数、仪器设置等）。
                data : ndarray，一个 NumPy 的 n 维数组，保存了读取的 NMR 实验数据。
        """
        return ng.bruker.read(
            self.data_path,
            bin_file=bin_file, acqus_files=acqus_files,
            pprog_file=pprog_file, shape=shape, cplex=cplex,
            big=big, isfloat=isfloat,
            read_pulseprogram=read_pulseprogram,
            read_acqus=read_acqus, procs_files=procs_files,
            read_procs=read_procs
        )

    def read_pdata(self, bin_files=None, procs_files=None, read_procs=True,
                   acqus_files=None, read_acqus=True, scale_data=True,
                   shape=None, submatrix_shape=None, all_components=False,
                   big=None, isfloat=None):
        """
        读取指定路径下的预处理过的Bruker NMR数据文件。

            pdata表示预处理过的Bruker NMR数据文件。

            在 TopSpin 和其他程序中，这些数据通常通过除以 2 ** -NC_proc 进行缩放，
            其中 NC_proc 定义在 procs 文件中。
            要实现这种缩放，可以将 scale_data 参数设为 True。

        :param bin_files: list of str, optional，目录中的二进制文件名列表。若为 None，则使用标准文件名。
        :param procs_files: list, optional，目录中 procs 参数文件的文件名列表。若为 None，则使用标准文件名。
        :param read_procs: bool, optional，若为 True，则读取 procs 文件；若为 False，则跳过读取。
        :param acqus_files:list, optional，目录中 acqus 参数文件的文件名列表。若为 None，则使用标准文件名。
        :param read_acqus: bool, optional，若为 True，则读取 acqus 文件；若为 False，则跳过读取。
        :param scale_data: bool, optional，若为 True（默认值），则根据 procs 文件中定义的参数对数据进行缩放。
                                          通常应启用此选项。若为 False，则返回原始文件中的数据。
        :param shape: tuple, optional，返回数据的形状（维度）。若为 None，则从 procs 文件中推测数据形状。
        :param submatrix_shape: tuple, optional，用于多维数据（如二维、三维）的子矩阵形状。
                                    若为 None，则从 procs 文件的元数据中推测形状。
        :param all_components:bool，若为 True，则返回所有四象限分量（quadrature components）组成的列表；
                                    若为 False，则只返回实数部分（如 1r、2rr、3rrr 等）。
        :param big: bool or None, optional，表示二进制文件的字节序（endianness）。True 表示大端序（big-endian），
                                 False 表示小端序（little-endian），None 表示从 procs 文件中自动判断。
        :param isfloat:bool or None, optional，二进制文件的数据类型。
                            True 表示 float64，False 表示 int32。
                            若为 None，则从 procs 文件中自动判断数据类型。
        :return: (dict,data)
                1. dict,包含 Bruker 参数的字典。
                2. ndarray 或 list, NMR 数据数组。如果 all_components 为 True，则返回一个包含每个象限分量的数组列表。
        """
        return ng.bruker.read_pdata(
            self.pdata_path,
            bin_files=bin_files, procs_files=procs_files,
            read_procs=read_procs, acqus_files=acqus_files,
            read_acqus=read_acqus, scale_data=scale_data,
            shape=shape, submatrix_shape=submatrix_shape,
            all_components=all_components,
            big=big, isfloat=isfloat
        )

    def ppm_intensity(self, bin_files=None, procs_files=None, read_procs=True,
                      acqus_files=None, read_acqus=True, scale_data=True,
                      shape=None, submatrix_shape=None, all_components=False,
                      big=None, isfloat=None):
        """
        读取指定路径下的预处理过的Bruker NMR数据文件，并返回(ppm,intensity)数据。

        :param bin_files: list of str, optional，目录中的二进制文件名列表。若为 None，则使用标准文件名。
        :param procs_files: list, optional，目录中 procs 参数文件的文件名列表。若为 None，则使用标准文件名。
        :param read_procs: bool, optional，若为 True，则读取 procs 文件；若为 False，则跳过读取。
        :param acqus_files:list, optional，目录中 acqus 参数文件的文件名列表。若为 None，则使用标准文件名。
        :param read_acqus: bool, optional，若为 True，则读取 acqus 文件；若为 False，则跳过读取。
        :param scale_data: bool, optional，若为 True（默认值），则根据 procs 文件中定义的参数对数据进行缩放。
                                          通常应启用此选项。若为 False，则返回原始文件中的数据。
        :param shape: tuple, optional，返回数据的形状（维度）。若为 None，则从 procs 文件中推测数据形状。
        :param submatrix_shape: tuple, optional，用于多维数据（如二维、三维）的子矩阵形状。
                                    若为 None，则从 procs 文件的元数据中推测形状。
        :param all_components:bool，若为 True，则返回所有四象限分量（quadrature components）组成的列表；
                                    若为 False，则只返回实数部分（如 1r、2rr、3rrr 等）。
        :param big: bool or None, optional，表示二进制文件的字节序（endianness）。True 表示大端序（big-endian），
                                 False 表示小端序（little-endian），None 表示从 procs 文件中自动判断。
        :param isfloat:bool or None, optional，二进制文件的数据类型。
                            True 表示 float64，False 表示 int32。
                            若为 None，则从 procs 文件中自动判断数据类型。
        :return: (ppm,intensity)
                1. NMR的ppm数据。
                2. NMR的intensity数据。
        """
        # From pre-proceed data.
        dic, data = ng.bruker.read_pdata(
            self.pdata_path,
            bin_files=bin_files, procs_files=procs_files,
            read_procs=read_procs, acqus_files=acqus_files,
            read_acqus=read_acqus, scale_data=scale_data,
            shape=shape, submatrix_shape=submatrix_shape,
            all_components=all_components,
            big=big, isfloat=isfloat
        )
        udic = ng.bruker.guess_udic(dic, data)
        uc = ng.fileio.fileiobase.uc_from_udic(udic)
        ppm_scale = uc.ppm_scale()
        return ppm_scale, data
# ==================================================================
