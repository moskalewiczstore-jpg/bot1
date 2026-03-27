import os
from dotenv import load_dotenv

load_dotenv()

# Exchange settings
EXCHANGE_ID = os.getenv("EXCHANGE_ID", "binance")
API_KEY = os.getenv("API_KEY", "")
API_SECRET = os.getenv("API_SECRET", "")
USE_TESTNET = os.getenv("USE_TESTNET", "True").lower() == "true"

# Trading settings
SYMBOL = os.getenv("SYMBOL", "BTC/USDT")
TIMEFRAME = os.getenv("TIMEFRAME", "1h")
TRADE_AMOUNT_USDT = float(os.getenv("TRADE_AMOUNT_USDT", "10"))

# Strategy parameters
EMA_SHORT = int(os.getenv("EMA_SHORT", "9"))
EMA_LONG = int(os.getenv("EMA_LONG", "21"))
RSI_PERIOD = int(os.getenv("RSI_PERIOD", "14"))
RSI_OVERBOUGHT = float(os.getenv("RSI_OVERBOUGHT", "70"))
RSI_OVERSOLD = float(os.getenv("RSI_OVERSOLD", "30"))

# Risk management
MAX_POSITION_SIZE = float(os.getenv("MAX_POSITION_SIZE", "0.02"))  # 2% of balance
STOP_LOSS_PCT = float(os.getenv("STOP_LOSS_PCT", "0.02"))          # 2%
TAKE_PROFIT_PCT = float(os.getenv("TAKE_PROFIT_PCT", "0.04"))      # 4%

# Bot settings
LOOP_INTERVAL_SECONDS = int(os.getenv("LOOP_INTERVAL_SECONDS", "60"))
LOG_FILE = os.getenv("LOG_FILE", "trading.log")

# Telegram (optional)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
