from __future__ import annotations

import datetime
import random
from typing import Any


# Upcoming FOMC meeting dates (approximate)
_MEETING_DATES: list[str] = [
    "2024-03-20",
    "2024-05-01",
    "2024-06-12",
    "2024-07-31",
    "2024-09-18",
    "2024-11-07",
    "2024-12-18",
    "2025-01-29",
    "2025-03-19",
    "2025-05-07",
]


def _generate_mock_probabilities() -> list[dict[str, Any]]:
    """
    Generate realistic FedWatch-style probability distributions
    for each upcoming FOMC meeting.
    """
    meetings = []
    # Current baseline rate (simulated at 5.25–5.50%)
    current_rate = 5.375  # midpoint of 5.25–5.50% target range

    for i, date_str in enumerate(_MEETING_DATES):
        meeting_date = datetime.date.fromisoformat(date_str)
        days_away = (meeting_date - datetime.date.today()).days

        if days_away < 0:
            continue  # Skip past meetings

        # As we get further out, uncertainty grows
        volatility = min(0.4 + i * 0.06, 0.80)

        # Drift toward expected path: gentle easing cycle
        cut_25_prob = min(0.15 + i * 0.07 + random.uniform(-0.05, 0.05), 0.65)
        cut_50_prob = max(0.0, (i - 2) * 0.04 + random.uniform(0, 0.05))
        hike_25_prob = max(0.0, 0.08 - i * 0.01 + random.uniform(-0.02, 0.02))
        hold_prob = max(0.05, 1.0 - cut_25_prob - cut_50_prob - hike_25_prob)

        # Normalize
        total = cut_25_prob + cut_50_prob + hike_25_prob + hold_prob
        cut_25_prob = round(cut_25_prob / total, 3)
        cut_50_prob = round(cut_50_prob / total, 3)
        hike_25_prob = round(hike_25_prob / total, 3)
        hold_prob = round(1.0 - cut_25_prob - cut_50_prob - hike_25_prob, 3)

        expected_rate = (
            current_rate
            - cut_25_prob * 0.25
            - cut_50_prob * 0.50
            + hike_25_prob * 0.25
        )

        meetings.append({
            "date": date_str,
            "days_away": days_away,
            "probabilities": {
                "hike_25bps": hike_25_prob,
                "hold": hold_prob,
                "cut_25bps": cut_25_prob,
                "cut_50bps": cut_50_prob,
            },
            "expected_rate": round(expected_rate, 3),
            "current_rate": current_rate,
        })

    return meetings


class FedWatchAnalyzer:
    """
    Tracks CME FedWatch rate probability data.
    Uses realistic mock data; replace with live CME API in production.
    """

    def __init__(self) -> None:
        self._data: list[dict[str, Any]] = []

    async def get_probabilities(self) -> list[dict[str, Any]]:
        if not self._data:
            self._data = _generate_mock_probabilities()
        return self._data

    async def get_market_positioning(self) -> dict[str, Any]:
        probs = await self.get_probabilities()
        if not probs:
            return {"error": "No data available"}

        # Nearest meeting
        next_meeting = probs[0]
        next_probs = next_meeting["probabilities"]

        total_cut_prob = next_probs["cut_25bps"] + next_probs["cut_50bps"]
        total_hike_prob = next_probs["hike_25bps"]
        hold_prob = next_probs["hold"]

        if total_cut_prob > 0.5:
            market_expectation = "cut"
        elif total_hike_prob > 0.3:
            market_expectation = "hike"
        else:
            market_expectation = "hold"

        alignment_score = await self.get_alignment_score()

        return {
            "next_meeting": next_meeting,
            "meetings": probs[:6],
            "market_expectation": market_expectation,
            "cut_probability": round(total_cut_prob, 3),
            "hike_probability": round(total_hike_prob, 3),
            "hold_probability": round(hold_prob, 3),
            "alignment_score": alignment_score,
            "current_rate": 5.375,
            "expected_end_of_year_rate": round(
                5.375 - sum(
                    m["probabilities"]["cut_25bps"] * 0.25
                    + m["probabilities"]["cut_50bps"] * 0.50
                    for m in probs
                ),
                3,
            ),
        }

    async def get_alignment_score(self) -> float:
        """
        Score from -100 (strong cut pricing) to +100 (strong hike pricing).
        """
        probs = await self.get_probabilities()
        if not probs:
            return 0.0

        next_probs = probs[0]["probabilities"]
        cut_prob = next_probs["cut_25bps"] + next_probs["cut_50bps"]
        hike_prob = next_probs["hike_25bps"]

        score = (hike_prob - cut_prob) * 100
        return round(max(-100, min(100, score)), 1)
