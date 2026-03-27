import ccxt
import pandas as pd
from typing import Optional
from logger import get_logger
from config import (
    EXCHANGE_ID,
    API_KEY,
    API_SECRET,
    USE_TESTNET,
    SYMBOL,
    TIMEFRAME,
)

logger = get_logger("exchange_client")


class ExchangeClient:
    def __init__(self) -> None:
        exchange_class = getattr(ccxt, EXCHANGE_ID)
        self.exchange: ccxt.Exchange = exchange_class(
            {
                "apiKey": API_KEY,
                "secret": API_SECRET,
                "enableRateLimit": True,
            }
        )

        if USE_TESTNET:
            if "test" in self.exchange.urls:
                self.exchange.set_sandbox_mode(True)
                logger.info("Running in TESTNET mode.")
            else:
                logger.warning(
                    "Exchange '%s' does not support testnet. Running in live mode.",
                    EXCHANGE_ID,
                )
        else:
            logger.info("Running in LIVE mode.")

    def fetch_ohlcv(self, limit: int = 200) -> Optional[pd.DataFrame]:
        try:
            raw = self.exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=limit)
            df = pd.DataFrame(
                raw, columns=["timestamp", "open", "high", "low", "close", "volume"]
            )
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df = df.set_index("timestamp")
            return df
        except Exception as exc:
            logger.error("Failed to fetch OHLCV data: %s", exc)
            return None

    def fetch_balance(self) -> dict:
        try:
            balance = self.exchange.fetch_balance()
            return balance.get("total", {})
        except Exception as exc:
            logger.error("Failed to fetch balance: %s", exc)
            return {}

    def place_market_order(self, side: str, amount: float) -> Optional[dict]:
        try:
            order = self.exchange.create_market_order(SYMBOL, side, amount)
            logger.info("Order placed: %s %s %.6f @ market", side.upper(), SYMBOL, amount)
            return order
        except Exception as exc:
            logger.error("Failed to place order (%s %.6f): %s", side, amount, exc)
            return None

    def fetch_ticker(self) -> Optional[dict]:
        try:
            return self.exchange.fetch_ticker(SYMBOL)
        except Exception as exc:
            logger.error("Failed to fetch ticker: %s", exc)
            return None
