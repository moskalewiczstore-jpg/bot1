from logger import get_logger
from config import (
    MAX_POSITION_SIZE,
    STOP_LOSS_PCT,
    TAKE_PROFIT_PCT,
    TRADE_AMOUNT_USDT,
)

logger = get_logger("risk_manager")


class RiskManager:
    def __init__(self) -> None:
        self.stop_loss_pct = STOP_LOSS_PCT
        self.take_profit_pct = TAKE_PROFIT_PCT
        self.max_position_size = MAX_POSITION_SIZE

    def position_size(self, balance_usdt: float, price: float) -> float:
        """Return the amount of base currency to trade, respecting risk limits."""
        max_by_risk = balance_usdt * self.max_position_size / price
        requested = TRADE_AMOUNT_USDT / price
        amount = min(max_by_risk, requested)
        if amount <= 0:
            logger.warning("Calculated position size is zero or negative.")
            return 0.0
        logger.debug(
            "Position size: %.6f (price=%.2f, balance=%.2f USDT)", amount, price, balance_usdt
        )
        return amount

    def stop_loss_price(self, entry_price: float, side: str) -> float:
        if side == "buy":
            return entry_price * (1 - self.stop_loss_pct)
        return entry_price * (1 + self.stop_loss_pct)

    def take_profit_price(self, entry_price: float, side: str) -> float:
        if side == "buy":
            return entry_price * (1 + self.take_profit_pct)
        return entry_price * (1 - self.take_profit_pct)

    def check_stop_loss(self, entry_price: float, current_price: float, side: str) -> bool:
        sl = self.stop_loss_price(entry_price, side)
        if side == "buy" and current_price <= sl:
            logger.info(
                "Stop-loss triggered: current=%.2f <= sl=%.2f", current_price, sl
            )
            return True
        if side == "sell" and current_price >= sl:
            logger.info(
                "Stop-loss triggered: current=%.2f >= sl=%.2f", current_price, sl
            )
            return True
        return False

    def check_take_profit(self, entry_price: float, current_price: float, side: str) -> bool:
        tp = self.take_profit_price(entry_price, side)
        if side == "buy" and current_price >= tp:
            logger.info(
                "Take-profit triggered: current=%.2f >= tp=%.2f", current_price, tp
            )
            return True
        if side == "sell" and current_price <= tp:
            logger.info(
                "Take-profit triggered: current=%.2f <= tp=%.2f", current_price, tp
            )
            return True
        return False
