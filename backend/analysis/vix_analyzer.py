from __future__ import annotations

import random
from typing import Any

import httpx
from loguru import logger


def _mock_vix() -> float:
    """Return a realistic VIX value for simulation."""
    return round(random.uniform(12.0, 35.0), 2)


class VIXAnalyzer:
    """
    Analyzes the CBOE VIX fear index.
    Fetches from Yahoo Finance; falls back to realistic mock data.
    """

    def __init__(self) -> None:
        self._current_vix: float = 18.5
        self._prev_vix: float = 17.2
        self._history: list[float] = []

    async def get_current_vix(self) -> float:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(
                    "https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX",
                    params={"interval": "1d", "range": "5d"},
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                data = resp.json()
                closes = (
                    data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
                )
                valid = [c for c in closes if c is not None]
                if valid:
                    self._prev_vix = self._current_vix
                    self._current_vix = round(valid[-1], 2)
        except Exception as exc:
            logger.debug(f"VIX fetch from Yahoo failed: {exc}. Using simulated value.")
            # Small random walk from current value
            change = random.uniform(-0.8, 0.8)
            self._prev_vix = self._current_vix
            self._current_vix = round(max(9.0, self._current_vix + change), 2)

        self._history.append(self._current_vix)
        if len(self._history) > 50:
            self._history.pop(0)

        return self._current_vix

    def analyze_regime(self, vix: float) -> dict[str, Any]:
        if vix < 15:
            regime = "low"
            description = "Complacency — risk-on environment"
            color = "green"
        elif vix < 20:
            regime = "normal"
            description = "Normal volatility"
            color = "yellow"
        elif vix < 30:
            regime = "elevated"
            description = "Elevated fear — caution advised"
            color = "orange"
        else:
            regime = "extreme"
            description = "Extreme fear / crisis conditions"
            color = "red"

        return {
            "regime": regime,
            "description": description,
            "color": color,
        }

    async def get_signal(self) -> dict[str, Any]:
        vix = await self.get_current_vix()
        regime_info = self.analyze_regime(vix)
        trend = self._calculate_trend()

        # Fear/greed signal
        if vix > 30:
            signal = "strong_buy"  # Extreme fear = contrarian buy
            fear_greed = "extreme_fear"
        elif vix > 20:
            signal = "buy"
            fear_greed = "fear"
        elif vix < 13:
            signal = "strong_sell"  # Extreme complacency = contrarian sell
            fear_greed = "extreme_greed"
        elif vix < 15:
            signal = "sell"
            fear_greed = "greed"
        else:
            signal = "neutral"
            fear_greed = "neutral"

        # Near-term sentiment prediction
        if trend == "rising" and vix > 20:
            prediction = "bearish"
        elif trend == "falling" and vix < 20:
            prediction = "bullish"
        else:
            prediction = "neutral"

        return {
            "value": vix,
            "prev_value": self._prev_vix,
            "change": round(vix - self._prev_vix, 2),
            "change_pct": round((vix - self._prev_vix) / max(self._prev_vix, 0.01) * 100, 2),
            "regime": regime_info["regime"],
            "regime_description": regime_info["description"],
            "regime_color": regime_info["color"],
            "trend": trend,
            "signal": signal,
            "fear_greed": fear_greed,
            "near_term_prediction": prediction,
            "history": self._history[-20:],
        }

    def _calculate_trend(self) -> str:
        if len(self._history) < 3:
            return "neutral"
        recent = self._history[-3:]
        if recent[-1] > recent[0]:
            return "rising"
        elif recent[-1] < recent[0]:
            return "falling"
        return "flat"
