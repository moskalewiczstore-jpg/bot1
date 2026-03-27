import time
import sys
from dataclasses import dataclass
from logger import get_logger
from config import LOOP_INTERVAL_SECONDS, SYMBOL, USE_TESTNET
from exchange_client import ExchangeClient
from strategy import get_signal
from risk_manager import RiskManager

logger = get_logger("main")


@dataclass
class Position:
    side: str          # 'buy' or 'sell'
    entry_price: float
    amount: float


def send_telegram(message: str) -> None:
    """Send a notification via Telegram (optional)."""
    from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        import urllib.request
        import urllib.parse

        url = (
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            f"?chat_id={TELEGRAM_CHAT_ID}&text={urllib.parse.quote(message)}"
        )
        urllib.request.urlopen(url, timeout=10)  # noqa: S310
    except Exception as exc:
        logger.warning("Telegram notification failed: %s", exc)


class TradingBot:
    def __init__(self) -> None:
        self.client = ExchangeClient()
        self.risk_manager = RiskManager()
        self.position: Position | None = None

    def _get_usdt_balance(self) -> float:
        balance = self.client.fetch_balance()
        return float(balance.get("USDT", 0.0))

    def _get_current_price(self) -> float | None:
        ticker = self.client.fetch_ticker()
        if ticker is None:
            return None
        return float(ticker.get("last", 0.0))

    def _close_position(self, reason: str) -> None:
        if self.position is None:
            return
        close_side = "sell" if self.position.side == "buy" else "buy"
        logger.info(
            "Closing position (%s) via %s order. Reason: %s",
            self.position.side,
            close_side,
            reason,
        )
        order = self.client.place_market_order(close_side, self.position.amount)
        if order:
            msg = f"Position closed ({reason}): {close_side.upper()} {SYMBOL} {self.position.amount:.6f}"
            send_telegram(msg)
        self.position = None

    def step(self) -> None:
        df = self.client.fetch_ohlcv()
        if df is None or df.empty:
            logger.warning("No OHLCV data received; skipping this iteration.")
            return

        current_price = self._get_current_price()
        if current_price is None or current_price <= 0:
            logger.warning("Invalid current price; skipping this iteration.")
            return

        # Check stop-loss / take-profit on open position
        if self.position is not None:
            side = self.position.side
            entry = self.position.entry_price

            if self.risk_manager.check_stop_loss(entry, current_price, side):
                self._close_position("stop-loss")
                return

            if self.risk_manager.check_take_profit(entry, current_price, side):
                self._close_position("take-profit")
                return

        signal = get_signal(df)

        if signal == "HOLD":
            logger.debug("Signal: HOLD — no action.")
            return

        # If we already have an open position, skip new entries
        if self.position is not None:
            logger.debug("Already in a position; ignoring signal '%s'.", signal)
            return

        usdt_balance = self._get_usdt_balance()
        amount = self.risk_manager.position_size(usdt_balance, current_price)

        if amount <= 0:
            logger.warning("Position size is zero; skipping trade.")
            return

        order_side = "buy" if signal == "BUY" else "sell"
        order = self.client.place_market_order(order_side, amount)

        if order:
            self.position = Position(
                side=order_side,
                entry_price=current_price,
                amount=amount,
            )
            msg = (
                f"Order executed: {order_side.upper()} {SYMBOL} "
                f"{amount:.6f} @ ~{current_price:.2f}"
            )
            logger.info(msg)
            send_telegram(msg)

    def run(self) -> None:
        mode = "TESTNET" if USE_TESTNET else "LIVE"
        logger.info("Trading bot started. Symbol=%s, Mode=%s", SYMBOL, mode)
        send_telegram(f"Trading bot started. Symbol={SYMBOL}, Mode={mode}")

        try:
            while True:
                try:
                    self.step()
                except Exception as exc:
                    logger.error("Unexpected error in main loop: %s", exc, exc_info=True)
                logger.debug("Sleeping %d seconds...", LOOP_INTERVAL_SECONDS)
                time.sleep(LOOP_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user.")
            send_telegram("Trading bot stopped by user.")
            sys.exit(0)


if __name__ == "__main__":
    bot = TradingBot()
    bot.run()
