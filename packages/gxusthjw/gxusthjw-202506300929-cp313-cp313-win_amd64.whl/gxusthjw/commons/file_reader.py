#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        file_reader.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“读取文件”相关的函数和类。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/03     finish
# ------------------------------------------------------------------
# 导包 ==============================================================
from typing import (
    Union, Optional, Sequence, Literal, Tuple, Mapping, Any, Dict, List
)
from pathlib import Path
from itertools import islice
import pandas as pd
import numpy as np

from .file_info import (
    encoding_of,
    FileInfo,
)

from .data_table import (
    DataTable
)

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Define functions and classes associated with `Read file`.
"""

__all__ = [
    'read_txt',
    'read_text',
    '_read_text_df',
    '_safe_cast_series',
    '_read_text_list',
]


# 定义 ==============================================================

def read_txt(file: Union[str, FileInfo],
             sep: Optional[str] = None,
             skiprows: int = 0,
             cols: Optional[Mapping[int, Optional[str]]] = None,
             res_type: Optional[Literal["list", "dict", "ndarrays", "dataframe", "datatable"]] = None,
             encoding: Optional[str] = None) -> \
        Union[dict, list, pd.DataFrame, DataTable]:
    """
    读取文本文件中的数据。

        基于TextIOWrapper对象的readline方法。

        读取数据时，如果未指定列名，则以`col_i`代替。

    :param file: 数据文件的FileInfo对象或完整路径。
    :type file: Union[str, FileInfo]
    :param sep: 数据间的分隔符，如果为None，则以空白符为分割符。
    :param skiprows: 跳过的行数，默认为0。
    :param cols: 指定要读取的列。
    :param res_type: 返回值形式，可指定的值分别为：

                     1. 如果为忽略大小写的”dict“，则返回字典对象，其中值为numpy.ndarray，
                        键名与cols指定的相同。

                     2. 如果为忽略大小写的”list“，则返回list对象，其中每列为list对象,
                        列的顺序与cols指定的顺序相同。

                     3. 如果为忽略大小写的”ndarrays“，则返回list对象，其中每列为numpy.ndarray,
                        列的顺序与cols指定的顺序相同。

                    4.  如果为忽略大小写的”dataframe“，则返回pandas.DataFrame对象，
                        列名与cols指定的相同。

                     5. 其他值，均返回DataTable对象。

    :param encoding: 文件编码，如果文件编码未知，则利用chardet尝试解析，
                      如果未能解析出文件的编码，则以“GBK”读取文件。
    :return: 读取到的值。
    """
    if isinstance(file, FileInfo):
        if encoding is None:
            encoding = file.encoding
        file = file.full_path

    # 尝试解析文件的编码。
    if encoding is None:
        encoding = encoding_of(file)

    # 如果文件编码还是未知，则使用“GBK”。
    if encoding is None:
        encoding = "GBK"

    # 用于存储读取到的数据,每列数由独立的list对象保存，
    # 每列数据均有一个名字，作为字典的键。
    data_dict: Dict[str, List] = {}

    # 要读取数据的列号（列号从0开始）和对应的列名。
    index_col_name_dict: Dict[int, Optional[str]] = {}

    # confirm_on_read表示读取时确定，
    # 用于指示data_dict和index_col_name_dict的构建时机。
    confirm_on_read = False
    if (cols is None) or (len(cols) == 0):
        confirm_on_read = True
    else:
        for col_index in cols.keys():
            col_name = cols[col_index]
            if col_name is not None:
                data_dict["{}".format(col_name)] = list()
            else:
                col_name = "col_{}".format(col_index)
                data_dict[col_name] = list()
            index_col_name_dict[col_index] = col_name

    with open(file, mode='r', encoding=encoding) as f:
        # 跳过指定的行数。
        skiprows = int(skiprows)
        while skiprows != 0:
            f.readline()
            skiprows -= 1
        # 开始读取数据。
        for line in f:

            # 这里的判断是为了防止空行。
            if line.isspace():
                continue

            # 如果不是空行，则将其分割。
            value_str_array = line.strip().split(sep)
            # print(value_str_array)

            # 如果没有指定要读取的列，则读取所有列，列名为：‘col_i’,其中i为列号。
            if confirm_on_read:
                cols_index = range(len(value_str_array))
                # print(cols_index)
                for index in cols_index:
                    col_name = "col_{}".format(index)
                    index_col_name_dict[index] = col_name
                    data_dict[col_name] = list()
                confirm_on_read = False

            # 如果len(value_str_array) <= max(col_index)，则可能抛出异常。
            # 但考虑到效率问题，这里不做检查。
            for col_index in index_col_name_dict.keys():
                # print(value_str_array[col_index])
                value_str = value_str_array[col_index].strip()
                value = float(value_str.strip()) if value_str.strip() else None
                data_dict[index_col_name_dict[col_index]].append(value)

        # 返回读取到的结果。
        if isinstance(res_type, str) and res_type.lower() == "dict":
            return data_dict
        elif isinstance(res_type, str) and res_type.lower() == "list":
            res_list = list()
            for col_index in index_col_name_dict.keys():
                res_list.append(data_dict[index_col_name_dict[col_index]])
            return res_list
        elif isinstance(res_type, str) and res_type.lower() == "ndarrays":
            res_list = list()
            for col_index in index_col_name_dict.keys():
                res_list.append(np.array(data_dict[index_col_name_dict[col_index]], copy=True))
            return res_list
        elif isinstance(res_type, str) and res_type.lower() == "dataframe":
            return pd.DataFrame(data_dict)
        else:
            res_list = list()
            for col_index in index_col_name_dict.keys():
                res_list.append(data_dict[index_col_name_dict[col_index]])
            return DataTable(*res_list, col_names=index_col_name_dict)


# ==============================================================
def read_text(
        file: Union[str, Path, FileInfo],
        sep: Optional[str] = None,
        skiprows: int = 0,
        usecols: Optional[Sequence[int]] = None,
        names: Optional[Mapping[int, str]] = None,
        types: Optional[Mapping[int, Union[int, float, str, object]]] = None,
        res_type: Optional[Literal["list", "dict", "ndarrays", "dataframe", "datatable"]] = None,
        encoding: Optional[str] = None
):
    """
    读取文本文件并解析为指定的数据结构。

    :param file: 文件路径或文件信息。
    :param sep: 列分隔符，默认为任意空白字符。
    :param skiprows: 跳过的行数。
    :param usecols: 使用的列索引列表，如果指定，则只读取这些列。
    :param names: 列名映射，用于指定列的名称。
    :param types: 列类型映射，用于指定每列的数据类型。
    :param res_type: 返回值类型，支持多种数据结构。

                    1. 如果为忽略大小写的”dict“，则返回字典对象，其中值为numpy.ndarray，
                        键名与names指定的相同。

                     2. 如果为忽略大小写的”list“，则返回list对象，其中每列为list对象,
                        列的顺序与names指定的顺序相同。

                     3. 如果为忽略大小写的”ndarrays“，则返回list对象，其中每列为numpy.ndarray,
                        列的顺序与names指定的顺序相同。

                    4.  如果为忽略大小写的”dataframe“，则返回pandas.DataFrame对象，
                        列名与names指定的相同。

                     5. 其他值，均返回DataTable对象。

    :param encoding: 文件编码方式。
    :return: 根据 res_type 参数返回对应的数据结构。
    """
    # 读取文本到数据框
    df = _read_text_df(file, sep=sep, skiprows=skiprows, names=names, types=types, encoding=encoding)

    # 筛选指定的列
    if usecols:
        valid_indices = set(range(len(df.columns)))
        for col_index in usecols:
            if col_index not in valid_indices:
                raise ValueError(f"Column index {col_index} is out of range. "
                                 f"Valid column indices are: {valid_indices}")
        df = df.iloc[:, usecols]

    # 根据 res_type 参数的不同，将数据框转换为相应的数据结构
    if isinstance(res_type, str) and res_type.lower() == "dict":
        return df.to_dict(orient='list')
    elif isinstance(res_type, str) and res_type.lower() == "list":
        result_dict = df.to_dict(orient='list')
        return list(result_dict.values())
    elif isinstance(res_type, str) and res_type.lower() == "ndarrays":
        return [np.array(df[col]) for col in df.columns]
    elif isinstance(res_type, str) and res_type.lower() == "dataframe":
        return df
    else:
        dt = DataTable()
        dt.update(df)
        return dt


def _read_text_df(
        file: Union[str, Path, FileInfo],
        sep: Optional[str] = None,
        skiprows: int = 0,
        names: Optional[Mapping[int, str]] = None,
        types: Optional[Mapping[int, Any]] = None,
        encoding: Optional[str] = None
):
    """
    读取文本文件并解析为DataFrame。

    :param file: 文件路径或文件信息对象。
    :param sep: 列分隔符，默认为任意空白字符。
    :param skiprows: 跳过的行数，默认为0。
    :param names: 列名映射，键为列索引，值为列名。
    :param types: 类型映射，键为列索引，值为目标数据类型。
    :param encoding: 文件编码方式。
    :return: 解析后的DataFrame。
    """
    # 读取文本数据，获取结果列表和最大列数
    res_list, max_col_count = _read_text_list(file, sep, skiprows, encoding)

    # 自动列名生成
    columns = [f"col_{i}" for i in range(max_col_count)]
    if names:
        for col_index, name in names.items():
            if col_index < max_col_count:
                columns[col_index] = name

    # 补充缺失的列数据
    for row in res_list:
        row.extend([''] * (max_col_count - len(row)))

    # 转换为 DataFrame
    df = pd.DataFrame(res_list, columns=columns)

    # 类型转换（可选）
    if types:
        for col_index, dtype in types.items():
            if col_index < max_col_count:
                col_name = columns[col_index]
                try:
                    df[col_name] = _safe_cast_series(df[col_name], dtype)
                except ValueError as e:
                    raise ValueError(f"Failed to convert column '{col_name}' "
                                     f"to type {dtype}: {e}") from e
    return df


def _safe_cast_series(series, dtype):
    """
    安全地将 pandas.Series 转换为目标 dtype 类型。
    如果转换失败，则使用 NaN 或空值替代。

    :param series: pandas.Series
    :param dtype: 目标数据类型 (str, int, float, np.number, np.dtype 等)
    :return: 转换后的 Series
    """
    # 将 dtype 统一处理为 numpy dtype
    try:
        target_dtype = np.dtype(dtype)
    except TypeError:
        raise ValueError(f"Unsupported dtype: {dtype}")

    # 处理数值类型（包括 int、float、np.int32、np.float64 等）
    if np.issubdtype(target_dtype, np.number):
        converted = pd.to_numeric(series, errors='coerce')
        return converted.astype(target_dtype)

    # 处理字符串类型
    elif target_dtype == np.str_ or str(target_dtype) in ['string', 'str']:
        return series.astype(str)

    # 处理 object 类型
    elif target_dtype == np.object_:
        return series.astype(object)

    # 其他类型尝试直接转换
    else:
        try:
            return series.astype(target_dtype)
        except Exception as e:
            raise ValueError(f"Failed to cast series to dtype '{dtype}': {e}")


def _read_text_list(
        file: Union[str, Path, FileInfo],
        sep: Optional[str] = None,
        skiprows: int = 0,
        encoding: Optional[str] = None
) -> Tuple[list, int]:
    """
    从文本文件中读取数据并按指定分隔符分割成二维列表，同时返回每行最大列数。

    :param file: 文件路径或 FileInfo 对象
    :param sep: 分隔符，默认为任意空白字符
    :param skiprows: 需要跳过的行数
    :param encoding: 文件编码，若为 None 则尝试自动识别，默认使用 GBK
    :return: 一个元组，包含：
                         1. 二维列表，每一项为一行分割后的字符串列表
                         2. 每行的最大列数
    """
    if isinstance(file, FileInfo):
        file = file.full_path
    else:
        file = Path(file)

    if not file.is_file():
        raise ValueError(f"The provided path '{file}' is not a valid file.")

    # 尝试解析文件的编码。
    if encoding is None:
        encoding = encoding_of(file)

    # 如果文件编码还是未知，则使用“GBK”。
    if encoding is None:
        encoding = "GBK"

    res_list = []
    res_max_count = 0

    try:
        with open(file, mode='r', encoding=encoding) as f:
            # 跳过指定行数
            for _ in islice(f, skiprows):
                pass

            # 开始读取数据
            for line in f:
                if line.isspace():
                    continue

                # 如果不是空行，则将其分割。
                value_str_array = line.strip().split(sep)
                res_max_count = max(res_max_count, len(value_str_array))
                res_list.append([v.strip() for v in value_str_array])

    except (IOError, OSError) as e:
        raise RuntimeError(f"Failed to read file '{file}': {e}") from e

    return res_list, res_max_count
# ==============================================================
