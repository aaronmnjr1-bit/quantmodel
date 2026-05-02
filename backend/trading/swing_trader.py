from __future__ import annotations

import uuid
import random
from typing import Any

import numpy as np
from loguru import logger

from trading.mt5_engine import MT5Engine, SUPPORTED_SYMBOLS


class SwingTrader:
    """
    Approval-based swing trading engine.
    Trades are queued and require manual approval before execution.
    Uses wider SL/TP than the scalper (ATR × 2.0 / ATR × 4.0).
    """

    # Class-level pending trade queue (shared across instances)
    _pending: dict[str, dict[str, Any]] = {}
    _executed: list[dict[str, Any]] = []

    def __init__(self) -> None:
        self._engine = MT5Engine()

    def queue_trade(
        self,
        symbol: str,
        direction: str,
        volume: float,
        entry: float,
        sl: float,
        tp: float,
        rationale: str = "",
    ) -> str:
        """Add a trade to the pending approval queue. Returns trade_id."""
        trade_id = str(uuid.uuid4())[:8]
        SwingTrader._pending[trade_id] = {
            "trade_id": trade_id,
            "symbol": symbol,
            "direction": direction,
            "volume": volume,
            "entry": entry,
            "sl": sl,
            "tp": tp,
            "rationale": rationale,
            "status": "pending",
            "rr_ratio": round(abs(tp - entry) / max(abs(sl - entry), 0.001), 2),
        }
        logger.info(f"Swing trade queued: {trade_id} | {symbol} {direction}")
        return trade_id

    def approve_trade(self, trade_id: str) -> bool:
        """Approve a pending trade — it will be executed asynchronously."""
        if trade_id not in SwingTrader._pending:
            return False
        SwingTrader._pending[trade_id]["status"] = "approved"
        logger.info(f"Swing trade approved: {trade_id}")
        return True

    def reject_trade(self, trade_id: str) -> bool:
        """Reject and remove a pending trade."""
        if trade_id not in SwingTrader._pending:
            return False
        SwingTrader._pending[trade_id]["status"] = "rejected"
        trade = SwingTrader._pending.pop(trade_id)
        SwingTrader._executed.append(trade)
        logger.info(f"Swing trade rejected: {trade_id}")
        return True

    def get_pending_trades(self) -> list[dict[str, Any]]:
        """Return all trades awaiting approval."""
        return [
            t for t in SwingTrader._pending.values() if t["status"] == "pending"
        ]

    async def execute_approved(self) -> list[dict[str, Any]]:
        """Execute all approved trades and remove them from the queue."""
        to_execute = [
            (tid, t)
            for tid, t in SwingTrader._pending.items()
            if t["status"] == "approved"
        ]
        results = []
        for trade_id, trade in to_execute:
            result = await self._engine.execute_trade(
                symbol=trade["symbol"],
                direction=trade["direction"],
                volume=trade["volume"],
                sl=trade["sl"],
                tp=trade["tp"],
                comment=f"Swing|{trade_id}",
            )
            trade["execution_result"] = result
            trade["status"] = "executed"
            SwingTrader._executed.append(trade)
            del SwingTrader._pending[trade_id]
            results.append(trade)
        return results

    def generate_swing_signals(
        self, account_balance: float = 10000.0, risk_pct: float = 1.0
    ) -> list[str]:
        """Generate swing trade candidates and add to pending queue."""
        queued_ids: list[str] = []
        for symbol in random.sample(SUPPORTED_SYMBOLS, min(3, len(SUPPORTED_SYMBOLS))):
            direction = random.choice(["buy", "sell"])
            base = {"XAUUSD": 2050, "NAS100": 17500, "US30": 38500,
                    "GER40": 17200, "JP225": 38000, "USDCAD": 1.36}.get(symbol, 1.0)

            atr = base * 0.005
            if direction == "buy":
                entry = round(base * 1.001, 2)
                sl = round(entry - atr * 2.0, 2)
                tp = round(entry + atr * 4.0, 2)
            else:
                entry = round(base * 0.999, 2)
                sl = round(entry + atr * 2.0, 2)
                tp = round(entry - atr * 4.0, 2)

            sl_dist = abs(entry - sl)
            risk_amt = account_balance * risk_pct / 100
            volume = round(risk_amt / max(sl_dist * 100, 0.01), 2)
            volume = max(0.01, min(volume, 5.0))

            rationale = f"Swing signal: {direction.upper()} {symbol} | R:R {abs(tp-entry)/max(abs(sl-entry),0.001):.1f}"
            tid = self.queue_trade(symbol, direction, volume, entry, sl, tp, rationale)
            queued_ids.append(tid)

        return queued_ids
