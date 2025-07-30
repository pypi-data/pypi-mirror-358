import os
from typing import Literal
import pandas as pd

from polygon.rest import RESTClient

client = RESTClient(api_key=os.getenv("POLYGON_API_KEY"))


def get_current_datetime_price(symbol: str) -> tuple[pd.Timestamp, float]:
    """
    获取当前时间和价格

    Args:
        symbol (str): 交易对

    Returns:
        tuple[pd.Timestamp, float]: 当前时间戳和价格
    """
    current_datetime = pd.Timestamp.now(tz="UTC")
    current_price = client.get_last_trade(symbol).price
    return current_datetime, current_price


def get_kline_dataframe(symbol: str, freq: Literal["1m", "5m", "15m", "1d"], lookback: int) -> pd.DataFrame:
    """
    获取K线数据

    Args:
        symbol (str): 交易对
        freq (Literal["1m", "5m", "15m", "1d"]): 数据频率
        lookback (int): 回溯周期，单位为分钟
    Returns:
        pd.DataFrame: 包含K线数据的DataFrame
    """
    freq_map = {
        "1m": (1, "minute"),
        "3m": (3, "minute"),
        "5m": (5, "minute"),
        "15m": (15, "minute"),
        "30m": (30, "minute"),
        "45m": (45, "minute"),
        "1h": (1, "hour"),
        "2h": (2, "hour"),
        "4h": (4, "hour"),
        "6h": (6, "hour"),
        "12h": (12, "hour"),
        "1d": (1, "day"),
        "5d": (5, "day"),
        "1w": (1, "week"),
        "15d": (15, "day"),
        "30d": (30, "day"),
        "1mo": (1, "month"),
    }
    if freq not in freq_map:
        raise ValueError(f"Unsupported frequency: {freq}, supported frequencies are {list(freq_map.keys())}")

    multiplier, time_span = freq_map[freq]

    # 获取K线数据
    bars = client.get_aggs(
        ticker=symbol,
        multiplier=multiplier,
        timespan=time_span,
        limit=lookback,
        raw=False,
    )

    # 转换为DataFrame
    df = pd.DataFrame(
        [
            {
                "datetime": bar.timestamp,
                "open": bar.open,
                "high": bar.high,
                "low": bar.low,
                "close": bar.close,
                "volume": bar.volume,
            }
            for bar in bars
        ]
    )

    df["date"] = pd.to_datetime(df["datetime"], unit="ms", utc=True)
    df["datetime"] = pd.to_datetime(df["datetime"], unit="ms", utc=True)
    df["datetime"] = df["datetime"].dt.tz_convert("UTC")  # 确保时间戳是UTC时区
    df.set_index("datetime", inplace=True)
    return df


def fetch_data(symbol: str, freq: Literal["1m", "5m", "15m", "1d"], lookback: int):
    """
    获取K线数据

    Args:
        symbol (str): 交易对
        freq (Literal["1m", "5m", "15m", "1d"]): 数据频率
        lookback (int): 回溯周期，单位为分钟
    """
    current_datetime, current_price = get_current_datetime_price(symbol)
    df: pd.DataFrame = get_kline_dataframe(symbol, freq, lookback + 64)  # 获取更长时间的数据以便计算指标
    return current_datetime, current_price, df

from polygon.rest import RESTClient

client = RESTClient(api_key=os.getenv("POLYGON_API_KEY"))


def get_current_datetime_price(symbol: str) -> tuple[pd.Timestamp, float]:
    """
    获取当前时间和价格

    Args:
        symbol (str): 交易对

    Returns:
        tuple[pd.Timestamp, float]: 当前时间戳和价格
    """
    current_datetime = pd.Timestamp.now(tz="UTC")
    current_price = client.get_last_trade(symbol).price
    return current_datetime, current_price


def get_kline_dataframe(symbol: str, freq: Literal["1m", "5m", "15m", "1d"], lookback: int) -> pd.DataFrame:
    """
    获取K线数据

    Args:
        symbol (str): 交易对
        freq (Literal["1m", "5m", "15m", "1d"]): 数据频率
        lookback (int): 回溯周期，单位为分钟
    Returns:
        pd.DataFrame: 包含K线数据的DataFrame
    """
    freq_map = {
        "1m": (1, "minute"),
        "3m": (3, "minute"),
        "5m": (5, "minute"),
        "15m": (15, "minute"),
        "30m": (30, "minute"),
        "45m": (45, "minute"),
        "1h": (1, "hour"),
        "2h": (2, "hour"),
        "4h": (4, "hour"),
        "6h": (6, "hour"),
        "12h": (12, "hour"),
        "1d": (1, "day"),
        "5d": (5, "day"),
        "1w": (1, "week"),
        "15d": (15, "day"),
        "30d": (30, "day"),
        "1mo": (1, "month"),
    }
    if freq not in freq_map:
        raise ValueError(f"Unsupported frequency: {freq}, supported frequencies are {list(freq_map.keys())}")

    multiplier, time_span = freq_map[freq]

    # 获取K线数据
    bars = client.get_aggs(
        ticker=symbol,
        multiplier=multiplier,
        timespan=time_span,
        limit=lookback,
        raw=False,
    )

    # 转换为DataFrame
    df = pd.DataFrame(
        [
            {
                "datetime": bar.timestamp,
                "open": bar.open,
                "high": bar.high,
                "low": bar.low,
                "close": bar.close,
                "volume": bar.volume,
            }
            for bar in bars
        ]
    )

    df["date"] = pd.to_datetime(df["datetime"], unit="ms", utc=True)
    df["datetime"] = pd.to_datetime(df["datetime"], unit="ms", utc=True)
    df["datetime"] = df["datetime"].dt.tz_convert("UTC")  # 确保时间戳是UTC时区
    df.set_index("datetime", inplace=True)
    return df


def fetch_data(symbol: str, freq: Literal["1m", "5m", "15m", "1d"], lookback: int):
    """
    获取K线数据

    Args:
        symbol (str): 交易对
        freq (Literal["1m", "5m", "15m", "1d"]): 数据频率
        lookback (int): 回溯周期，单位为分钟
    """
    current_datetime, current_price = get_current_datetime_price(symbol)
    df: pd.DataFrame = get_kline_dataframe(symbol, freq, lookback + 64)  # 获取更长时间的数据以便计算指标
    return current_datetime, current_price, df
