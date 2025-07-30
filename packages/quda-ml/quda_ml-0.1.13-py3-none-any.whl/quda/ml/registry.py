# -*- coding: utf-8 -*-
"""
---------------------------------------------
Copyright (c) 2025 ZhangYundi
Licensed under the MIT License. 
Created on 2025/6/25 17:04
Email: yundi.xxii@outlook.com
Description: 注册获取数据的具体实现方法
---------------------------------------------
"""

from typing import Callable
import quda
import polars as pl


FUNC_SQL_LOCAL: Callable[[str, str], pl.LazyFrame] = lambda date, ds_path: quda.sql(
    f"select * from {ds_path} where date='{date}';")
