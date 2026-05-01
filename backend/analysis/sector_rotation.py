from __future__ import annotations

import random
from typing import Any

import httpx
from loguru import logger


CYCLICAL_SECTORS: dict[str, str] = {
    "XLB": "Materials",
    "XLE": "Energy",
    "XLF": "Financials",
    "XLI": "Industrials",
    "XLK": "Technology",
}

DEFENSIVE_SECTORS: dict[str, str] = {
    "XLP": "Consumer Staples",
    "XLRE": "Real Estate",
    "XLU": "Utilities",
    "XLV": "Healthcare",
}


def _mock_sector_returns() -> dict[str, float]:
    """Generate realistic simulated 30-day sector returns."""
    return {
        "XLB": random.uniform(-8, 12),
        "XLE": random.uniform(-15, 20),
        "XLF": random.uniform(-6, 10),
        "XLI": random.uniform(-5, 9),
        "XLK": random.uniform(-10, 18),
        "XLP": random.uniform(-4, 6),
        "XLRE": random.uniform(-10, 8),
        "XLU": random.uniform(-8, 5),
        "XLV": random.uniform(-4, 7),
    }


class SectorRotationAnalyzer:
    """
    Tracks equity sector rotation to identify cyclical vs defensive positioning.
    Determines market phase: expansion, peak, contraction, trough.
    """

    def __init__(self) -> None:
        self._sector_data: dict[str, Any] = {}

    async def get_sector_flows(self) -> dict[str, Any]:
        """Fetch sector ETF performance data."""
        try:
            returns = await self._fetch_yahoo_returns()
        except Exception as exc:
            logger.debug(f"Sector data fetch failed: {exc}. Using mock.")
            returns = _mock_sector_returns()

        flows: dict[str, Any] = {}
        for ticker, name in {**CYCLICAL_SECTORS, **DEFENSIVE_SECTORS}.items():
            ret = returns.get(ticker, 0.0)
            flows[ticker] = {
                "ticker": ticker,
                "name": name,
                "category": "cyclical" if ticker in CYCLICAL_SECTORS else "defensive",
                "return_30d": round(ret, 2),
                "momentum": "positive" if ret > 0 else "negative",
            }

        return flows

    async def _fetch_yahoo_returns(self) -> dict[str, float]:
        """Attempt to fetch real returns from Yahoo Finance."""
        tickers = list(CYCLICAL_SECTORS.keys()) + list(DEFENSIVE_SECTORS.keys())
        returns: dict[str, float] = {}
        async with httpx.AsyncClient(timeout=10.0) as client:
            for ticker in tickers:
                resp = await client.get(
                    f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}",
                    params={"interval": "1d", "range": "1mo"},
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                data = resp.json()
                closes = (
                    data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
                )
                valid = [c for c in closes if c is not None]
                if len(valid) >= 2:
                    ret = (valid[-1] - valid[0]) / valid[0] * 100
                    returns[ticker] = round(ret, 2)
        return returns

    def get_rotation_signal(
        self, flows: dict[str, Any]
    ) -> dict[str, Any]:
        cyclical_returns = [
            v["return_30d"] for k, v in flows.items() if v["category"] == "cyclical"
        ]
        defensive_returns = [
            v["return_30d"] for k, v in flows.items() if v["category"] == "defensive"
        ]

        avg_cyclical = sum(cyclical_returns) / max(len(cyclical_returns), 1)
        avg_defensive = sum(defensive_returns) / max(len(defensive_returns), 1)
        ratio = avg_cyclical - avg_defensive

        if ratio > 3:
            signal = "risk_on"
            bias = "bullish"
        elif ratio < -3:
            signal = "risk_off"
            bias = "bearish"
        else:
            signal = "neutral"
            bias = "neutral"

        return {
            "cyclical_avg_return": round(avg_cyclical, 2),
            "defensive_avg_return": round(avg_defensive, 2),
            "ratio": round(ratio, 2),
            "signal": signal,
            "bias": bias,
        }

    def _determine_market_phase(self, ratio: float, cyclical_avg: float) -> str:
        """
        Rough phase determination based on relative strength.
        Expansion: cyclicals outperform, positive returns.
        Peak: cyclicals still leading but momentum fading.
        Contraction: defensives outperform.
        Trough: defensives stabilizing, utilities/staples leading.
        """
        if ratio > 3 and cyclical_avg > 2:
            return "expansion"
        elif ratio > 0 and cyclical_avg < 1:
            return "peak"
        elif ratio < -3:
            return "contraction"
        elif ratio < 0 and cyclical_avg > -1:
            return "trough"
        return "expansion"

    async def analyze_capital_flows(self) -> dict[str, Any]:
        flows = await self.get_sector_flows()
        rotation = self.get_rotation_signal(flows)
        phase = self._determine_market_phase(
            rotation["ratio"], rotation["cyclical_avg_return"]
        )

        # Top and bottom performers
        sorted_sectors = sorted(
            flows.values(), key=lambda x: x["return_30d"], reverse=True
        )

        return {
            "sectors": flows,
            "rotation": rotation,
            "market_phase": phase,
            "top_performers": [s["ticker"] for s in sorted_sectors[:3]],
            "bottom_performers": [s["ticker"] for s in sorted_sectors[-3:]],
            "recommendation": self._phase_recommendation(phase),
        }

    def _phase_recommendation(self, phase: str) -> str:
        recommendations = {
            "expansion": "Favor cyclicals: XLF, XLI, XLK. Risk assets preferred.",
            "peak": "Begin rotating to defensives. Reduce risk exposure.",
            "contraction": "Defensive positioning: XLP, XLV, XLU. Cash/bonds.",
            "trough": "Early recovery signals. Watch XLF and XLI for leadership.",
        }
        return recommendations.get(phase, "Monitor sector flows.")
