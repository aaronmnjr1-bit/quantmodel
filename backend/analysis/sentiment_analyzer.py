from __future__ import annotations

import re
from typing import Any


HAWKISH_KEYWORDS: list[str] = [
    "rate hike",
    "inflation concerns",
    "tighten",
    "tightening",
    "aggressive",
    "above target",
    "persistent inflation",
    "restrictive",
    "reduce balance sheet",
    "quantitative tightening",
    "qt",
    "overshoot",
    "upside risk",
    "strong labor market",
    "wage growth",
    "overheating",
    "raise rates",
    "higher for longer",
    "not yet done",
    "further hikes",
]

DOVISH_KEYWORDS: list[str] = [
    "rate cut",
    "easing",
    "accommodative",
    "below target",
    "support growth",
    "pause",
    "pivot",
    "hold rates",
    "looser policy",
    "quantitative easing",
    "qe",
    "downside risk",
    "soft landing",
    "slowing growth",
    "disinflation",
    "deflationary",
    "labor market softening",
    "forward guidance",
    "patient",
    "data dependent",
]

NEUTRAL_KEYWORDS: list[str] = [
    "monitor",
    "assess",
    "watch",
    "flexible",
    "balanced",
    "uncertainty",
]


class SentimentAnalyzer:
    """
    Analyzes central-bank speeches and statements for hawkish/dovish bias.
    Scores text from -100 (very dovish) to +100 (very hawkish).
    """

    def __init__(self) -> None:
        self._fed_speeches: list[dict[str, Any]] = []
        self._current_bias: float = 0.0

    def analyze_fed_speech(self, text: str) -> dict[str, Any]:
        return self.analyze_statement(text)

    def analyze_statement(self, text: str) -> dict[str, Any]:
        text_lower = text.lower()

        hawkish_hits = [kw for kw in HAWKISH_KEYWORDS if kw in text_lower]
        dovish_hits = [kw for kw in DOVISH_KEYWORDS if kw in text_lower]
        neutral_hits = [kw for kw in NEUTRAL_KEYWORDS if kw in text_lower]

        # Weighted scoring
        hawkish_score = len(hawkish_hits) * 10
        dovish_score = len(dovish_hits) * 10
        neutral_dampener = len(neutral_hits) * 3

        raw_score = hawkish_score - dovish_score - neutral_dampener
        clamped = max(-100, min(100, raw_score))

        if clamped >= 30:
            bias = "hawkish"
        elif clamped <= -30:
            bias = "dovish"
        elif clamped >= 10:
            bias = "slightly_hawkish"
        elif clamped <= -10:
            bias = "slightly_dovish"
        else:
            bias = "neutral"

        self._current_bias = clamped

        return {
            "score": clamped,
            "bias": bias,
            "hawkish_keywords": hawkish_hits,
            "dovish_keywords": dovish_hits,
            "neutral_keywords": neutral_hits,
            "hawkish_count": len(hawkish_hits),
            "dovish_count": len(dovish_hits),
            "word_count": len(text.split()),
        }

    def get_current_bias(self) -> dict[str, Any]:
        """Return current cached bias or a neutral default."""
        if self._current_bias >= 30:
            bias = "hawkish"
        elif self._current_bias <= -30:
            bias = "dovish"
        elif self._current_bias >= 10:
            bias = "slightly_hawkish"
        elif self._current_bias <= -10:
            bias = "slightly_dovish"
        else:
            bias = "neutral"

        return {
            "score": self._current_bias,
            "bias": bias,
            "source": "cached",
        }

    def batch_analyze(self, texts: list[str]) -> list[dict[str, Any]]:
        return [self.analyze_statement(t) for t in texts]
