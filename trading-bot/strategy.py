import pandas as pd
import numpy as np
from typing import Literal, Optional
from logger import get_logger
from config import EMA_SHORT, EMA_LONG, RSI_PERIOD, RSI_OVERBOUGHT, RSI_OVERSOLD

logger = get_logger("strategy")

Signal = Literal["BUY", "SELL", "HOLD"]


def _ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def _rsi(series: pd.Series, period: int) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ema_short"] = _ema(df["close"], EMA_SHORT)
    df["ema_long"] = _ema(df["close"], EMA_LONG)
    df["rsi"] = _rsi(df["close"], RSI_PERIOD)
    return df


def get_signal(df: pd.DataFrame) -> Signal:
    if len(df) < max(EMA_LONG, RSI_PERIOD) + 1:
        logger.warning("Not enough candles to compute signal. Got %d rows.", len(df))
        return "HOLD"

    df = compute_indicators(df)
    last = df.iloc[-1]
    prev = df.iloc[-2]

    ema_cross_up = prev["ema_short"] < prev["ema_long"] and last["ema_short"] > last["ema_long"]
    ema_cross_down = prev["ema_short"] > prev["ema_long"] and last["ema_short"] < last["ema_long"]

    rsi_value: float = last["rsi"]

    logger.debug(
        "EMA short=%.4f, EMA long=%.4f, RSI=%.2f",
        last["ema_short"],
        last["ema_long"],
        rsi_value,
    )

    if ema_cross_up and rsi_value < RSI_OVERBOUGHT:
        logger.info("Signal: BUY (EMA crossover up, RSI=%.2f)", rsi_value)
        return "BUY"

    if ema_cross_down and rsi_value > RSI_OVERSOLD:
        logger.info("Signal: SELL (EMA crossover down, RSI=%.2f)", rsi_value)
        return "SELL"

    return "HOLD"
