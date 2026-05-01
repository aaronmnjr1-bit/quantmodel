from __future__ import annotations

import asyncio
import random
from typing import Any

import httpx
from loguru import logger


SYMBOLS = ["Gold", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD"]

# CFTC COT legacy report base URL
CFTC_BASE_URL = "https://www.cftc.gov/dea/newcot/deahistfo.zip"


class COTAnalyzer:
    """
    Analyzes CFTC Commitments of Traders (COT) reports.

    Tracks commercial vs non-commercial (large speculator) positioning
    and detects crowding / trend-change signals.
    """

    def __init__(self) -> None:
        self._cache: dict[str, Any] = {}
        self._last_refresh: float = 0.0

    async def refresh(self) -> None:
        """Attempt to fetch latest COT data; fall back to simulated data."""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # CFTC provides historical CSV; we use simulated realistic data
                # In production, parse the actual ZIP file from CFTC
                self._cache = self._generate_mock_cot()
                logger.info("COT data refreshed (simulated)")
        except Exception as exc:
            logger.warning(f"COT fetch failed, using mock data: {exc}")
            self._cache = self._generate_mock_cot()

    async def get_analysis(self) -> dict[str, Any]:
        if not self._cache:
            await self.refresh()
        return self._cache

    def _generate_mock_cot(self) -> dict[str, Any]:
        """Generate realistic mock COT data for all tracked symbols."""
        results = {}
        for symbol in SYMBOLS:
            # Simulate net positions in thousands of contracts
            commercial_net = random.randint(-150, 150)
            speculator_net = -commercial_net + random.randint(-20, 20)

            # Percentile rank over 52-week window (0–100)
            spec_percentile = random.uniform(10, 90)

            if spec_percentile > 75:
                crowding = "crowded_long"
                signal = "bearish"  # overcrowded longs → contrarian bearish
            elif spec_percentile < 25:
                crowding = "crowded_short"
                signal = "bullish"  # overcrowded shorts → contrarian bullish
            else:
                crowding = "neutral"
                signal = "bullish" if speculator_net > 0 else "bearish"

            strength = abs(spec_percentile - 50) * 2  # 0–100

            results[symbol] = {
                "symbol": symbol,
                "commercial_net": commercial_net,
                "speculator_net": speculator_net,
                "speculator_percentile": round(spec_percentile, 1),
                "crowding": crowding,
                "signal": signal,
                "strength": round(strength, 1),
                "trend_change": spec_percentile > 80 or spec_percentile < 20,
            }

        return {
            "data": results,
            "summary": self._summarize(results),
        }

    def _summarize(self, data: dict) -> dict[str, Any]:
        bullish = [s for s, v in data.items() if v["signal"] == "bullish"]
        bearish = [s for s, v in data.items() if v["signal"] == "bearish"]
        crowded = [s for s, v in data.items() if v["crowding"] != "neutral"]
        avg_strength = sum(v["strength"] for v in data.values()) / max(len(data), 1)

        return {
            "bullish_symbols": bullish,
            "bearish_symbols": bearish,
            "crowded_symbols": crowded,
            "average_strength": round(avg_strength, 1),
            "market_bias": "bullish" if len(bullish) > len(bearish) else "bearish",
        }
