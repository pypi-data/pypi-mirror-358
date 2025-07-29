# -*- coding: utf-8 -*-
"""
---------------------------------------------
Copyright (c) 2025 ZhangYundi
Licensed under the MIT License.
Created on 2025/6/25 15:05
Email: yundi.xxii@outlook.com
Description:
---------------------------------------------
"""

from collections.abc import Sequence

def get_timedelta_names(columns: Sequence[str], ) -> list[str]:
    """
    Return a list of column names that can be successfully parsed into <pandas>.Timedelta object.

    Parameters
    ----------
    columns: Sequence[str]
        A Sequence of strings representing column names to be evaluated for Timedelta

    Returns
    -------
    list[str]

    Examples
    --------
    >>> get_timedelta_names(['1s', '2min', 'invalid', '3H'])
    ['1s', '2min', '3H']

    """
    from pandas import Timedelta
    def _is_valid_timedelta(s: str) -> bool:
        try:
            Timedelta(s)
            return True
        except ValueError:
            return False

    return [col for col in columns if _is_valid_timedelta(col)]


def extract_feature_names(columns: Sequence[str], ) -> list[str]:
    """
    Extract a list of valid feature column names by excluding index-like(date/time/asset)、price-like(price)、time-like columns.
    Parameters
    ----------
    columns: Sequence[str]
        A sequence of strings representing all available column names.

    Returns
    -------
    list[str]

    Examples
    --------
    >>> extract_feature_names(['date', 'time', 'asset', 'open', 'high', '1s', 'volume', 'price'])
    ['open', 'high', 'volume']

    """
    return_cols = get_timedelta_names(columns)
    exclude = {"date", "time", "asset", 'price', *return_cols}
    return [col for col in columns if col not in exclude]