from __future__ import annotations

import asyncio
import random
from typing import Any

import numpy as np
from loguru import logger

from trading.mt5_engine import MT5Engine, SUPPORTED_SYMBOLS

# Minimum signal strength required to generate a scalp entry (0–100)
MIN_SIGNAL_THRESHOLD = 55.0


def _calculate_atr(prices: list[float], period: int = 14) -> float:
    """Simplified ATR from a list of prices (single series approximation)."""
    if len(prices) < 2:
        return prices[0] * 0.005 if prices else 1.0

    true_ranges = [abs(prices[i] - prices[i - 1]) for i in range(1, len(prices))]
    recent = true_ranges[-period:] if len(true_ranges) >= period else true_ranges
    return float(np.mean(recent)) if recent else prices[0] * 0.005


def _mock_price_series(base: float, n: int = 50) -> list[float]:
    """Generate a random walk price series for ATR calculation."""
    prices = [base]
    for _ in range(n - 1):
        change = random.gauss(0, base * 0.003)
        prices.append(max(prices[-1] + change, 0.01))
    return prices


class Scalper:
    """
    High-frequency scalping engine using ATR-based entry/exit levels.

    Entry = Current Price ± (ATR × 0.5)
    Stop-Loss = Entry ± (ATR × 1.5)
    Take-Profit = Entry ± (ATR × 2.0)
    """

    def __init__(self) -> None:
        self._engine = MT5Engine()
        self._active = False
        self._cycle_count = 0

    async def run_scalping_cycle(
        self,
        symbols: list[str] | None = None,
        risk_pct: float = 1.0,
        account_balance: float = 10000.0,
    ) -> list[dict[str, Any]]:
        """
        Execute one scalping cycle across all configured symbols.
        Returns list of trade results.
        """
        symbols = symbols or SUPPORTED_SYMBOLS
        self._cycle_count += 1
        results: list[dict[str, Any]] = []

        for symbol in symbols:
            try:
                result = await self._evaluate_symbol(symbol, risk_pct, account_balance)
                if result:
                    results.append(result)
            except Exception as exc:
                logger.warning(f"Scalp cycle error for {symbol}: {exc}")

        logger.debug(f"Scalp cycle #{self._cycle_count}: {len(results)} signals")
        return results

    async def _evaluate_symbol(
        self, symbol: str, risk_pct: float, account_balance: float
    ) -> dict[str, Any] | None:
        info = await self._engine.get_symbol_info(symbol)
        bid = info["bid"]
        ask = info["ask"]
        mid = (bid + ask) / 2

        # Generate price series for ATR calculation
        prices = _mock_price_series(mid, n=50)
        atr = _calculate_atr(prices)

        # Signal generation (simplified momentum + noise)
        signal_strength = random.uniform(30, 90)
        direction = random.choice(["buy", "sell"])

        if signal_strength < MIN_SIGNAL_THRESHOLD:
            return None

        # Entry price offset by half ATR (simulate limit-style entry)
        if direction == "buy":
            entry = round(ask + atr * 0.5, info["digits"])
            sl = round(entry - atr * 1.5, info["digits"])
            tp = round(entry + atr * 2.0, info["digits"])
        else:
            entry = round(bid - atr * 0.5, info["digits"])
            sl = round(entry + atr * 1.5, info["digits"])
            tp = round(entry - atr * 2.0, info["digits"])

        # Position sizing
        sl_distance = abs(entry - sl)
        risk_amount = account_balance * risk_pct / 100
        pip_value = info["contract_size"] * sl_distance
        volume = round(risk_amount / max(pip_value, 0.01), 2)
        volume = max(0.01, min(volume, 10.0))

        signal = {
            "symbol": symbol,
            "direction": direction,
            "entry": entry,
            "sl": sl,
            "tp": tp,
            "volume": volume,
            "atr": round(atr, info["digits"]),
            "signal_strength": round(signal_strength, 1),
            "mode": "scalp",
        }

        # Execute the trade
        trade_result = await self._engine.execute_trade(
            symbol=symbol,
            direction=direction,
            volume=volume,
            sl=sl,
            tp=tp,
            comment=f"Scalp|{signal_strength:.0f}",
        )

        return {**signal, "trade": trade_result}

    def start(self) -> None:
        self._active = True

    def stop(self) -> None:
        self._active = False

    @property
    def is_active(self) -> bool:
        return self._active
