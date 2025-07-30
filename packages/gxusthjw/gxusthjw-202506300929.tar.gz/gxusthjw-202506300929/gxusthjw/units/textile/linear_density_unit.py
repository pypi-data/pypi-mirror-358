#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from __future__ import absolute_import, print_function, division
# ------------------------------------------------------------------
# File Name:        linear_density_unit.py
# Author:           Jiwei Huang
# Version:          0.0.1
# Created:          2012/01/01
# Description:      定义“表征`线密度`”的单位。
# History:
#        <author>        <version>        <time>        <desc>
#       Jiwei Huang        0.0.1         2012/01/01     create
#       Jiwei Huang        0.0.1         2023/10/02     revise
#       Jiwei Huang        0.0.1         2024/09/12     revise
# ------------------------------------------------------------------
# 导包 ==============================================================
import abc
import threading
from typing import override
from ..base_unit import Unit

# 声明 ============================================================
__version__ = "0.0.1"

__author__ = "Jiwei Huang"

__doc__ = """
Defining the classes that represents `linear density`.
"""

__all__ = [
    'LinearDensityUnit',
    'WeightBasedLinearDensityUnit',
    'LengthBasedLinearDensityUnit',
    'DTex',
    'dtex',
    'Denier',
    'den',
    'Tex',
    'tex',
    'MetricCount',
    'Nm',
]

# 定义 ===============================================================
# 可识别的Denier字符串。
_recognizable_denier_unit_str = ["d", "D", "Den", "DEN", "den", "Denier",
                                 "denier", "DENIER"]

# 可识别的Tex字符串。
_recognizable_tex_unit_str = ["tex", "Tex", "TEX"]

# 可识别的DTex字符串。
_recognizable_dtex_unit_str = ["dtex", "Dtex", "dTex", "DTex", "DTEX"]

# 可识别的MetricCount字符串。
_recognizable_metric_count_unit_str = ["Nm", "metriccount", "Metriccount",
                                       "metricCount", "MetricCount",
                                       "METRICCOUNT"]


class LinearDensityUnit(Unit, abc.ABC):
    """
    类`LinearDensityUnit`表征”线密度“。
    """

    @override
    @property
    def family(self) -> str:
        """
        计量单位所隶属的单位族。

        每个计量单位均隶属于某一单位族，例如：

            “米”、“分米”、“厘米”等都隶属于”长度单位“；

            "克“、”毫克“、”微克“等都隶属于”重量单位”；

            ”小时“、"秒"、”分“等都隶属于”时间单位”。

        同族的单位间可相互转换，非同族的单位间不可相互转换，
        强制执行非同族单位间的转换将出发`ValueError`类型的异常。

        线密度单位的单位族为："LinearDensityUnit"

        :return: 计量单位所隶属的单位族。
        :rtype: `str`
        """
        return "LinearDensityUnit"

    @override
    @property
    def benchmark_unit(self):
        """
        计量单位所属单位族的基准单位。

        每个计量单位族，有且只有一个基准单位（Benchmark unit），

        例如：

            ”长度单位”的基准单位为”米“。

            ”重量单位”的基准单位为”克“。

        线密度单位的基准单位为：`Tex`

        :return: 计量单位所属单位族的基准单位。
        :rtype: `LinearDensityUnit`
        """
        return Tex()

    @staticmethod
    def from_string(unit_str: str):
        """
        从字符串构建”线密度“对象。

            对于单位”特克斯“，可以识别的字符串为："tex","Tex","TEX"。

            对于单位”分特克斯“，可以识别的字符串为："dtex","Dtex", "dTex","DTex","DTEX"

            对于单位”旦尼尔“，可以识别的字符串为："d","D", "Den","DEN", "den","Denier","denier","DENIER"

            对于单位”公制指数“，可以识别的字符串为："Nm","metriccount","Metriccount","metricCount","MetricCount","METRICCOUNT"

        :param unit_str: 线密度字符串。
        :return: LinearDensityUnit对象。
        """
        if unit_str.strip() in _recognizable_denier_unit_str:
            return Denier()
        elif unit_str.strip() in _recognizable_tex_unit_str:
            return Tex()
        elif unit_str.strip() in _recognizable_dtex_unit_str:
            return DTex()
        elif unit_str.strip() in _recognizable_metric_count_unit_str:
            return MetricCount()
        else:
            raise ValueError("Unrecognized parameter value for %s" % unit_str)


class WeightBasedLinearDensityUnit(LinearDensityUnit, abc.ABC):
    """
    类`WeightBasedLinearDensityUnit`表征”定重制线密度“。
    """
    # 空类
    pass


class LengthBasedLinearDensityUnit(LinearDensityUnit, abc.ABC):
    """
    类`LengthBasedLinearDensityUnit`表征”定长制线密度“。
    """
    # 空类
    pass


# noinspection DuplicatedCode
class Denier(LengthBasedLinearDensityUnit):
    """
    类`Denier`表征”旦尼尔“。
    """

    # 单例模式实现 ================================================
    # 单例锁
    _instance_lock = threading.Lock()
    # 单例实例
    _instance = None

    def __init__(self):
        """
        初始化方法。
        """
        pass

    def __new__(cls, *args, **kwargs):
        """
        构造方法：实现单例模式。
        """
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    # ===========================================================
    @override
    @property
    def name(self) -> str:
        """
        计量单位的名字。

        约定：所有计量单位的名字均应与其类的名字相同。

        :return: 计量单位的名字。
        :rtype: `str`
        """
        return "Denier"

    @override
    @property
    def symbol(self) -> str:
        """
        计量单位的符号（一般为计量单位名称的简写）。

        :return: 计量单位的符号（一般为计量单位名称的简写）。
        :rtype: `str`
        """
        return "D"

    @override
    @property
    def description(self) -> str:
        """
        计量单位的描述信息，用于对计量单位的含义进行说明。

        :return: 计量单位的描述信息，用于对计量单位的含义进行说明。
        :rtype: `str`
        """
        return "1 gram per 9000 meters."

    @override
    @property
    def cfactor(self) -> float:
        """
        此单位至其所隶属单位族的基准单位间的转换因子，例如：

        （1）长度单位的基准单位为”米“，而 1 厘米 = 0.01 米，则 ”厘米“的转换因子即为0.01。

        （2）重量单位的基准单位为“克”，而 1 千克 = 1000 克，则“千克”的转换因子即为1000.0。

        由此定义可知：1 此单位 = cfactor 基准单位。

        :return:转换因子（此单位与其基准单位间）。
        :rtype: `float`
        """
        return 1.0 / 9.0

    @override
    @property
    def rcfactor(self) -> float:
        """
        此单位至其所隶属单位族的基准单位间的逆转换因子，例如：

        （1）长度单位的基准单位为”米“，而 1 米 = 100 厘米，则 ”厘米“的逆转换因子即为100。

        （2）重量单位的基准单位为“克”，而 1 克 = 0.001 千克，则“千克”的逆转换因子即为0.001。

        由此定义可知：1 基准单位 = rcfactor 此单位。

        :return: 逆转换因子（此单位与其基准单位间）。
        :rtype: `float`
        """
        return 9.0

    @override
    @property
    def is_exact_cfactor(self) -> bool:
        """
        判断此单位至其单位族的基准单位之间的转换是否精确，
        换言之，用于表征cfactor的值是否为精确值。

        如果是精确的，则返回True，否则返回False。

        :return: 如果此单位至其单位族的基准单位之间的转换是精确的，则返回True，否则返回False。
        """
        return False

    @override
    @property
    def is_exact_rcfactor(self) -> bool:
        """
        判断此单位至其单位族的基准单位之间的逆转换是否精确，
        换言之，用于表征rcfactor的值是否为精确值。

        如果是精确的，则返回True，否则返回False。

        :return: 如果此单位至其单位族的基准单位之间的逆转换是精确的，则返回True，否则返回False。
        """
        return True

    def __eq__(self, other) -> bool:
        """
        重载运算符：比较与另一个对象的相等性。

        :param other: 另一个对象。
        :return: 相等返回True，否则返回False。
        :rtype: `bool`
        """
        if self is other:
            return True
        elif not isinstance(other, Denier):
            return False
        else:
            return self.name == other.name and \
                self.symbol == other.symbol and \
                self.description == other.description and \
                self.family == other.family

    def __ne__(self, other) -> bool:
        """
        重载运算符：比较与另一个对象的不相等性。

        :param other: 另一个对象。
        :return: 不相等返回True，否则返回False。
        :rtype: `bool`
        """
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """
        重载方法：仿照Java，计算对象的hash码。

        :return: hash码。
        :rtype: `int`
        """
        return hash((self.name, self.symbol, self.description, self.family))

    @staticmethod
    def from_string(unit_str: str):
        """
        根据字符串构建Denier对象。

        :param unit_str: 线密度字符串。
        :return: Denier对象。
        """
        if unit_str in _recognizable_denier_unit_str:
            return Denier()
        raise ValueError("Unrecognized parameter value for %s" % unit_str)


# 唯一实例。
den = Denier()


# noinspection DuplicatedCode
class Tex(LengthBasedLinearDensityUnit):
    """
    类`Tex`表征”特克斯“。
    """

    # 单例模式实现 ================================================
    # 单例锁
    _instance_lock = threading.Lock()
    # 单例实例
    _instance = None

    def __init__(self):
        """
        初始化方法。
        """
        pass

    def __new__(cls, *args, **kwargs):
        """
        构造方法：实现单例模式。
        """
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    # ===========================================================
    @override
    @property
    def name(self) -> str:
        """
        计量单位的名字。

        约定：所有计量单位的名字均应与其类的名字相同。

        :return: 计量单位的名字。
        :rtype: `str`
        """
        return "Tex"

    @override
    @property
    def symbol(self) -> str:
        """
        计量单位的符号（一般为计量单位名称的简写）。

        :return: 计量单位的符号（一般为计量单位名称的简写）。
        :rtype: `str`
        """
        return "tex"

    @override
    @property
    def description(self) -> str:
        """
        计量单位的描述信息，用于对计量单位的含义进行说明。

        :return: 计量单位的描述信息，用于对计量单位的含义进行说明。
        :rtype: `str`
        """
        return "1 gram per 1000 meters."

    @override
    @property
    def cfactor(self) -> float:
        """
        此单位至其所隶属单位族的基准单位间的转换因子，例如：

        （1）长度单位的基准单位为”米“，而 1 厘米 = 0.01 米，则 ”厘米“的转换因子即为0.01。

        （2）重量单位的基准单位为“克”，而 1 千克 = 1000 克，则“千克”的转换因子即为1000.0。

        由此定义可知：1 此单位 = cfactor 基准单位。

        :return:转换因子（此单位与其基准单位间）。
        :rtype: `float`
        """
        return 1.0

    @override
    @property
    def rcfactor(self) -> float:
        """
        此单位至其所隶属单位族的基准单位间的逆转换因子，例如：

        （1）长度单位的基准单位为”米“，而 1 米 = 100 厘米，则 ”厘米“的逆转换因子即为100。

        （2）重量单位的基准单位为“克”，而 1 克 = 0.001 千克，则“千克”的逆转换因子即为0.001。

        由此定义可知：1 基准单位 = rcfactor 此单位。

        :return: 逆转换因子（此单位与其基准单位间）。
        :rtype: `float`
        """
        return 1.0

    @override
    @property
    def is_exact_cfactor(self) -> bool:
        """
        判断此单位至其单位族的基准单位之间的转换是否精确，
        换言之，用于表征cfactor的值是否为精确值。

        如果是精确的，则返回True，否则返回False。

        :return: 如果此单位至其单位族的基准单位之间的转换是精确的，则返回True，否则返回False。
        """
        return True

    @override
    @property
    def is_exact_rcfactor(self) -> bool:
        """
        判断此单位至其单位族的基准单位之间的逆转换是否精确，
        换言之，用于表征rcfactor的值是否为精确值。

        如果是精确的，则返回True，否则返回False。

        :return: 如果此单位至其单位族的基准单位之间的逆转换是精确的，则返回True，否则返回False。
        """
        return True

    def __eq__(self, other) -> bool:
        """
        重载运算符：比较与另一个对象的相等性。

        :param other: 另一个对象。
        :return: 相等返回True，否则返回False。
        :rtype: `bool`
        """
        if self is other:
            return True
        elif not isinstance(other, Tex):
            return False
        else:
            return self.name == other.name and \
                self.symbol == other.symbol and \
                self.description == other.description and \
                self.family == other.family

    def __ne__(self, other) -> bool:
        """
        重载运算符：比较与另一个对象的不相等性。

        :param other: 另一个对象。
        :return: 不相等返回True，否则返回False。
        :rtype: `bool`
        """
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """
        重载方法：仿照Java，计算对象的hash码。

        :return: hash码。
        :rtype: `int`
        """
        return hash((self.name, self.symbol, self.description, self.family))

    @staticmethod
    def from_string(unit_str: str):
        """
        根据字符串构建Tex对象。

        :param unit_str: 线密度字符串。
        :return: Tex对象。
        """
        if unit_str in _recognizable_tex_unit_str:
            return Tex()
        raise ValueError("Unrecognized parameter value for %s" % unit_str)


# 唯一实例。
tex = Tex()


# noinspection DuplicatedCode
class DTex(LengthBasedLinearDensityUnit):
    """
    类`DTex`表征”分特克斯“。
    """

    # 单例模式实现 ================================================
    # 单例锁
    _instance_lock = threading.Lock()
    # 单例实例
    _instance = None

    def __init__(self):
        """
        初始化方法。
        """
        pass

    def __new__(cls, *args, **kwargs):
        """
        构造方法：实现单例模式。
        """
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    # ===========================================================
    @override
    @property
    def name(self) -> str:
        """
        计量单位的名字。

        约定：所有计量单位的名字均应与其类的名字相同。

        :return: 计量单位的名字。
        :rtype: `str`
        """
        return "DTex"

    @override
    @property
    def symbol(self) -> str:
        """
        计量单位的符号（一般为计量单位名称的简写）。

        :return: 计量单位的符号（一般为计量单位名称的简写）。
        :rtype: `str`
        """
        return "dtex"

    @override
    @property
    def description(self) -> str:
        """
        计量单位的描述信息，用于对计量单位的含义进行说明。

        :return: 计量单位的描述信息，用于对计量单位的含义进行说明。
        :rtype: `str`
        """
        return "1 gram per 10000 meters."

    @override
    @property
    def cfactor(self) -> float:
        """
        此单位至其所隶属单位族的基准单位间的转换因子，例如：

        （1）长度单位的基准单位为”米“，而 1 厘米 = 0.01 米，则 ”厘米“的转换因子即为0.01。

        （2）重量单位的基准单位为“克”，而 1 千克 = 1000 克，则“千克”的转换因子即为1000.0。

        由此定义可知：1 此单位 = cfactor 基准单位。

        :return:转换因子（此单位与其基准单位间）。
        :rtype: `float`
        """
        return 0.1

    @override
    @property
    def rcfactor(self) -> float:
        """
        此单位至其所隶属单位族的基准单位间的逆转换因子，例如：

        （1）长度单位的基准单位为”米“，而 1 米 = 100 厘米，则 ”厘米“的逆转换因子即为100。

        （2）重量单位的基准单位为“克”，而 1 克 = 0.001 千克，则“千克”的逆转换因子即为0.001。

        由此定义可知：1 基准单位 = rcfactor 此单位。

        :return: 逆转换因子（此单位与其基准单位间）。
        :rtype: `float`
        """
        return 10.0

    @override
    @property
    def is_exact_cfactor(self) -> bool:
        """
        判断此单位至其单位族的基准单位之间的转换是否精确，
        换言之，用于表征cfactor的值是否为精确值。

        如果是精确的，则返回True，否则返回False。

        :return: 如果此单位至其单位族的基准单位之间的转换是精确的，则返回True，否则返回False。
        """
        return True

    @override
    @property
    def is_exact_rcfactor(self) -> bool:
        """
        判断此单位至其单位族的基准单位之间的逆转换是否精确，
        换言之，用于表征rcfactor的值是否为精确值。

        如果是精确的，则返回True，否则返回False。

        :return: 如果此单位至其单位族的基准单位之间的逆转换是精确的，则返回True，否则返回False。
        """
        return True

    def __eq__(self, other) -> bool:
        """
        重载运算符：比较与另一个对象的相等性。

        :param other: 另一个对象。
        :return: 相等返回True，否则返回False。
        :rtype: `bool`
        """
        if self is other:
            return True
        elif not isinstance(other, DTex):
            return False
        else:
            return self.name == other.name and \
                self.symbol == other.symbol and \
                self.description == other.description and \
                self.family == other.family

    def __ne__(self, other) -> bool:
        """
        重载运算符：比较与另一个对象的不相等性。

        :param other: 另一个对象。
        :return: 不相等返回True，否则返回False。
        :rtype: `bool`
        """
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """
        重载方法：仿照Java，计算对象的hash码。

        :return: hash码。
        :rtype: `int`
        """
        return hash((self.name, self.symbol, self.description, self.family))

    @staticmethod
    def from_string(unit_str: str):
        """
        根据字符串构建DTex对象。

        :param unit_str: 线密度字符串。
        :return: DTex对象。
        """
        if unit_str in _recognizable_dtex_unit_str:
            return DTex()
        raise ValueError("Unrecognized parameter value for %s" % unit_str)


# 唯一实例。
dtex = DTex()


# noinspection DuplicatedCode
class MetricCount(WeightBasedLinearDensityUnit):
    """
    类`MetricCount`表征”公制支数“。
    """

    # 单例模式实现 ================================================
    # 单例锁
    _instance_lock = threading.Lock()
    # 单例实例
    _instance = None

    def __init__(self):
        """
        初始化方法。
        """
        pass

    def __new__(cls, *args, **kwargs):
        """
        构造方法：实现单例模式。
        """
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    # ===========================================================
    @override
    @property
    def name(self) -> str:
        """
        计量单位的名字。

        约定：所有计量单位的名字均应与其类的名字相同。

        :return: 计量单位的名字。
        :rtype: `str`
        """
        return "MetricCount"

    @override
    @property
    def symbol(self) -> str:
        """
        计量单位的符号（一般为计量单位名称的简写）。

        :return: 计量单位的符号（一般为计量单位名称的简写）。
        :rtype: `str`
        """
        return "Nm"

    @override
    @property
    def description(self) -> str:
        """
        计量单位的描述信息，用于对计量单位的含义进行说明。

        :return: 计量单位的描述信息，用于对计量单位的含义进行说明。
        :rtype: `str`
        """
        return "1 meter per 1 gram."

    @override
    @property
    def cfactor(self) -> float:
        """
        此单位至其所隶属单位族的基准单位间的转换因子，例如：

        （1）长度单位的基准单位为”米“，而 1 厘米 = 0.01 米，则 ”厘米“的转换因子即为0.01。

        （2）重量单位的基准单位为“克”，而 1 千克 = 1000 克，则“千克”的转换因子即为1000.0。

        由此定义可知：1 此单位 = cfactor 基准单位。

        :return:转换因子（此单位与其基准单位间）。
        :rtype: `float`
        """
        return 1000.0

    @override
    @property
    def rcfactor(self) -> float:
        """
        此单位至其所隶属单位族的基准单位间的逆转换因子，例如：

        （1）长度单位的基准单位为”米“，而 1 米 = 100 厘米，则 ”厘米“的逆转换因子即为100。

        （2）重量单位的基准单位为“克”，而 1 克 = 0.001 千克，则“千克”的逆转换因子即为0.001。

        由此定义可知：1 基准单位 = rcfactor 此单位。

        :return: 逆转换因子（此单位与其基准单位间）。
        :rtype: `float`
        """
        return 1000.0

    @override
    @property
    def is_exact_cfactor(self) -> bool:
        """
        判断此单位至其单位族的基准单位之间的转换是否精确，
        换言之，用于表征cfactor的值是否为精确值。

        如果是精确的，则返回True，否则返回False。

        :return: 如果此单位至其单位族的基准单位之间的转换是精确的，则返回True，否则返回False。
        """
        return True

    @override
    @property
    def is_exact_rcfactor(self) -> bool:
        """
        判断此单位至其单位族的基准单位之间的逆转换是否精确，
        换言之，用于表征rcfactor的值是否为精确值。

        如果是精确的，则返回True，否则返回False。

        :return: 如果此单位至其单位族的基准单位之间的逆转换是精确的，则返回True，否则返回False。
        """
        return True

    def convert_to_benchmark(self, value: float) -> float:
        """
        将带有此单位的值转换为带有基准单位的值。

        :param value: 带有此单位的值。
        :type value: `float`
        :return: 带有基准单位的值。
        :rtype: `float`
        """
        return self.cfactor / value

    def convert_from_benchmark(self, value: float) -> float:
        """
        将带有基准单位的值转换为带有此单位的值。

        :param value: 带有基准单位的值。
        :type value: `float`
        :return: 带有此单位的值。
        :rtype: `float`
        """
        return self.rcfactor / value

    def __eq__(self, other) -> bool:
        """
        重载运算符：比较与另一个对象的相等性。

        :param other: 另一个对象。
        :return: 相等返回True，否则返回False。
        :rtype: `bool`
        """
        if self is other:
            return True
        elif not isinstance(other, MetricCount):
            return False
        else:
            return self.name == other.name and \
                self.symbol == other.symbol and \
                self.description == other.description and \
                self.family == other.family

    def __ne__(self, other) -> bool:
        """
        重载运算符：比较与另一个对象的不相等性。

        :param other: 另一个对象。
        :return: 不相等返回True，否则返回False。
        :rtype: `bool`
        """
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """
        重载方法：仿照Java，计算对象的hash码。

        :return: hash码。
        :rtype: `int`
        """
        return hash((self.name, self.symbol, self.description, self.family))

    @staticmethod
    def from_string(unit_str: str):
        """
        根据字符串构建MetricCount对象。

        :param unit_str: 线密度字符串。
        :return: MetricCount对象。
        """
        if unit_str in _recognizable_metric_count_unit_str:
            return MetricCount()
        raise ValueError("Unrecognized parameter value for %s" % unit_str)


# 唯一实例。
Nm = MetricCount()
# ============================================================================
