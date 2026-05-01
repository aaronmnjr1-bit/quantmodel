from __future__ import annotations

import asyncio
import datetime
import random
from typing import Any

import requests
from bs4 import BeautifulSoup
from loguru import logger


FOREX_FACTORY_URL = "https://www.forexfactory.com/calendar"

_MOCK_EVENTS: list[dict[str, Any]] = [
    {
        "id": "ff_001",
        "time": "08:30",
        "currency": "USD",
        "event": "Non-Farm Payrolls",
        "impact": "high",
        "forecast": "185K",
        "previous": "175K",
        "actual": "210K",
        "deviation": 25,
        "sentiment_score": 35,
        "upcoming": False,
    },
    {
        "id": "ff_002",
        "time": "10:00",
        "currency": "USD",
        "event": "ISM Manufacturing PMI",
        "impact": "high",
        "forecast": "49.5",
        "previous": "48.7",
        "actual": "50.3",
        "deviation": 0.8,
        "sentiment_score": 15,
        "upcoming": False,
    },
    {
        "id": "ff_003",
        "time": "14:00",
        "currency": "EUR",
        "event": "ECB Interest Rate Decision",
        "impact": "high",
        "forecast": "4.50%",
        "previous": "4.50%",
        "actual": None,
        "deviation": None,
        "sentiment_score": 0,
        "upcoming": True,
    },
    {
        "id": "ff_004",
        "time": "12:30",
        "currency": "USD",
        "event": "CPI m/m",
        "impact": "high",
        "forecast": "0.2%",
        "previous": "0.3%",
        "actual": "0.4%",
        "deviation": 0.2,
        "sentiment_score": 30,
        "upcoming": False,
    },
    {
        "id": "ff_005",
        "time": "09:45",
        "currency": "USD",
        "event": "Chicago PMI",
        "impact": "medium",
        "forecast": "46.0",
        "previous": "44.0",
        "actual": "44.9",
        "deviation": -1.1,
        "sentiment_score": -12,
        "upcoming": False,
    },
    {
        "id": "ff_006",
        "time": "15:30",
        "currency": "GBP",
        "event": "BOE Governor Bailey Speaks",
        "impact": "high",
        "forecast": None,
        "previous": None,
        "actual": None,
        "deviation": None,
        "sentiment_score": 0,
        "upcoming": True,
    },
    {
        "id": "ff_007",
        "time": "13:30",
        "currency": "USD",
        "event": "Initial Jobless Claims",
        "impact": "medium",
        "forecast": "218K",
        "previous": "215K",
        "actual": "207K",
        "deviation": -11,
        "sentiment_score": 20,
        "upcoming": False,
    },
]


class NewsMonitor:
    """
    Monitors economic news calendar from ForexFactory.
    Falls back to realistic mock data when scraping is unavailable.
    """

    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = list(_MOCK_EVENTS)
        self._last_refresh: float = 0.0

    async def refresh(self) -> None:
        """Attempt to scrape ForexFactory; fallback to mock."""
        try:
            scraped = await asyncio.get_event_loop().run_in_executor(
                None, self._scrape_forexfactory
            )
            if scraped:
                self._events = scraped
                logger.info(f"News monitor refreshed: {len(scraped)} events")
            else:
                self._events = list(_MOCK_EVENTS)
        except Exception as exc:
            logger.warning(f"News scrape failed, using mock data: {exc}")
            self._events = list(_MOCK_EVENTS)

    def _scrape_forexfactory(self) -> list[dict[str, Any]]:
        """Scrape ForexFactory calendar page."""
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        resp = requests.get(FOREX_FACTORY_URL, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        rows = soup.select("tr.calendar__row")
        events: list[dict[str, Any]] = []

        current_time = ""
        for row in rows:
            time_el = row.select_one(".calendar__time")
            if time_el and time_el.text.strip():
                current_time = time_el.text.strip()

            currency_el = row.select_one(".calendar__currency")
            event_el = row.select_one(".calendar__event")
            impact_el = row.select_one(".calendar__impact span")
            forecast_el = row.select_one(".calendar__forecast")
            actual_el = row.select_one(".calendar__actual")
            previous_el = row.select_one(".calendar__previous")

            if not event_el:
                continue

            impact_class = ""
            if impact_el:
                classes = impact_el.get("class", [])
                if "icon--ff-impact-red" in classes:
                    impact_class = "high"
                elif "icon--ff-impact-ora" in classes:
                    impact_class = "medium"
                else:
                    impact_class = "low"

            forecast = forecast_el.text.strip() if forecast_el else ""
            actual = actual_el.text.strip() if actual_el else ""
            previous = previous_el.text.strip() if previous_el else ""

            deviation = self._calculate_deviation(actual, forecast)
            sentiment = self._score_deviation(deviation, impact_class)

            events.append({
                "id": f"ff_{len(events):04d}",
                "time": current_time,
                "currency": currency_el.text.strip() if currency_el else "",
                "event": event_el.text.strip(),
                "impact": impact_class,
                "forecast": forecast,
                "previous": previous,
                "actual": actual if actual else None,
                "deviation": deviation,
                "sentiment_score": sentiment,
                "upcoming": not bool(actual),
            })

        return events

    def _calculate_deviation(
        self, actual: str, forecast: str
    ) -> float | None:
        try:
            a = float(actual.replace("%", "").replace("K", "").replace("M", ""))
            f = float(forecast.replace("%", "").replace("K", "").replace("M", ""))
            return round(a - f, 3)
        except (ValueError, AttributeError):
            return None

    def _score_deviation(
        self, deviation: float | None, impact: str
    ) -> int:
        if deviation is None:
            return 0
        weight = {"high": 3, "medium": 1.5, "low": 0.5}.get(impact, 1)
        raw = deviation * weight * 10
        return int(max(-100, min(100, raw)))

    def get_upcoming_events(self) -> list[dict[str, Any]]:
        return [e for e in self._events if e.get("upcoming", False)]

    def get_high_impact_events(self, limit: int = 20) -> list[dict[str, Any]]:
        high = [e for e in self._events if e.get("impact") == "high"]
        return high[:limit]

    async def analyze_news_sentiment(self) -> dict[str, Any]:
        scored = [e for e in self._events if e.get("sentiment_score") is not None]
        if not scored:
            return {"overall": 0, "bias": "neutral", "event_count": 0}

        total = sum(e["sentiment_score"] for e in scored)
        avg = total / len(scored)
        bias = "hawkish" if avg > 15 else "dovish" if avg < -15 else "neutral"

        return {
            "overall": round(avg, 1),
            "bias": bias,
            "event_count": len(scored),
            "positive_events": len([e for e in scored if e["sentiment_score"] > 0]),
            "negative_events": len([e for e in scored if e["sentiment_score"] < 0]),
        }
