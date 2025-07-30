#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ----------------------------------------------------------------
# File Name:        __init__.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      gxusthjw.commons包的__init__.py。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2025/06/27     revise
# ----------------------------------------------------------------
# 导包 ==============================================================
from .arrays import (
    is_sorted_ascending_np,
    is_sorted_descending_np,
    is_sorted_np,
    is_sorted,
    is_sorted_ascending,
    is_sorted_descending,
    reverse,
    is_equals_of,
    Ordering,
    sort,
    find_closest_index,
    find_crossing_index,
    find_index_range,
)

from .benchmarks import (
    benchmark,
)

from .data_2d import (
    Data2d
)

from .data_2d_region import (
    Data2dRegion,
)

from .data_analyzer import (
    DataAnalyzer,
)

from .data_logger import (
    DataLogger,
)

from .data_table import (
    DataTable
)

from .data_xy import (
    DataXY
)

from .dataframes import (
    create_df_from_dict,
    create_df_from_item,
    merge_df,
    merge_dfs,
    update_df,
    updates_df,
)

from .dicts import (
    dict_to_str,
)

from .file_info import (
    encoding_of,
    FileInfo,
    info_of,
    module_info_of,
)

from .file_object import (
    FileObject,
)

from .file_path import (
    sep_file_path,
    join_file_path,
    list_files_and_folders,
    print_files_and_folders,
    list_files_with_suffix,
    get_root_path,
    get_project_path,
    get_this_path,

)

from .file_reader import (
    read_txt,
    read_text,
)

from .folder_operator import (
    folder_cleanup,
    folder_create
)

from .function_object import (
    FunctionObject
)

from .normalizer import (
    normalize,
    z_score,
    decimal_scaling
)

from .path_object import (
    PathObject,
)

from .paths import (
    UniquePathGenerationError,
    gen_unique_path,
)

from .specimen import (
    Specimen,
)

from .tests import (
    run_tests,
)

from .typings import (
    Number,
    NumberSequence,
    Numbers,
    Numeric,
    NumberNDArray,
    is_number,
    is_number_sequence,
    is_numbers,
    is_numeric,
    is_number_ndarray,
    is_number_1darray,
    to_number_1darray,
    is_scalar,
)

from .unique_object import (
    UniqueIdentifierObject,
    unique_string,
    random_string,
    date_string,
)

# 声明 ==============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Assembling the common classes and functions 
from the `gxusthjw` python package.
"""

__all__ = [
    # ----------------------------------------------------------
    'is_sorted_ascending_np',
    'is_sorted_descending_np',
    'is_sorted_np',
    'is_sorted',
    'is_sorted_ascending',
    'is_sorted_descending',
    'reverse',
    'is_equals_of',
    'Ordering',
    'sort',
    'find_closest_index',
    'find_crossing_index',
    'find_index_range',
    # ----------------------------------------------------------
    'benchmark',
    # ----------------------------------------------------------
    'Data2d',
    # ----------------------------------------------------------
    'Data2dRegion',
    # ----------------------------------------------------------
    'DataAnalyzer',
    # ----------------------------------------------------------
    'DataLogger',
    # ----------------------------------------------------------
    'DataTable',
    # ----------------------------------------------------------
    'DataXY',
    # ----------------------------------------------------------
    'create_df_from_dict',
    'create_df_from_item',
    'merge_df',
    'merge_dfs',
    'update_df',
    'updates_df',
    # ----------------------------------------------------------
    'dict_to_str',
    # ----------------------------------------------------------
    'encoding_of',
    'FileInfo',
    'info_of',
    'module_info_of',
    # ----------------------------------------------------------
    'FileObject',
    # ----------------------------------------------------------
    'sep_file_path',
    'join_file_path',
    'list_files_and_folders',
    'print_files_and_folders',
    'list_files_with_suffix',
    'get_root_path',
    'get_project_path',
    'get_this_path',
    # ----------------------------------------------------------
    'read_txt',
    'read_text',
    # ----------------------------------------------------------
    'folder_cleanup',
    'folder_create',
    # ----------------------------------------------------------
    'FunctionObject',
    # ----------------------------------------------------------
    'normalize',
    'z_score',
    'decimal_scaling',
    # ----------------------------------------------------------
    'PathObject',
    # ----------------------------------------------------------
    'UniquePathGenerationError',
    'gen_unique_path',
    # ----------------------------------------------------------
    'Specimen',
    # ----------------------------------------------------------
    'run_tests',
    # ----------------------------------------------------------
    'Number',
    'is_number',
    'NumberSequence',
    'is_number_sequence',
    'Numbers',
    'is_numbers',
    'Numeric',
    'is_numeric',
    'NumberNDArray',
    'is_number_ndarray',
    'is_number_1darray',
    'to_number_1darray',
    'is_scalar',
    # ----------------------------------------------------------
    'random_string',
    'unique_string',
    'date_string',
    'UniqueIdentifierObject',
    # ----------------------------------------------------------
]
# 定义 ==============================================================
