from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/cot")
async def get_cot_data(request: Request) -> dict[str, Any]:
    cot = request.app.state.cot_analyzer
    data = await cot.get_analysis()
    return data


@router.get("/news")
async def get_news(request: Request, limit: int = 20) -> dict[str, Any]:
    monitor = request.app.state.news_monitor
    events = monitor.get_high_impact_events(limit=limit)
    sentiment = await monitor.analyze_news_sentiment()
    return {"events": events, "sentiment": sentiment}


@router.get("/upcoming-events")
async def get_upcoming_events(request: Request) -> dict[str, Any]:
    monitor = request.app.state.news_monitor
    events = monitor.get_upcoming_events()
    return {"events": events}


@router.get("/vix")
async def get_vix(request: Request) -> dict[str, Any]:
    vix = request.app.state.vix_analyzer
    data = await vix.get_signal()
    return data


@router.get("/fedwatch")
async def get_fedwatch() -> dict[str, Any]:
    from analysis.fedwatch import FedWatchAnalyzer

    fw = FedWatchAnalyzer()
    return await fw.get_market_positioning()


@router.get("/sentiment")
async def get_sentiment(text: str = "") -> dict[str, Any]:
    from analysis.sentiment_analyzer import SentimentAnalyzer

    analyzer = SentimentAnalyzer()
    if text:
        result = analyzer.analyze_fed_speech(text)
    else:
        result = analyzer.get_current_bias()
    return result


@router.get("/sector-rotation")
async def get_sector_rotation() -> dict[str, Any]:
    from analysis.sector_rotation import SectorRotationAnalyzer

    analyzer = SectorRotationAnalyzer()
    return await analyzer.analyze_capital_flows()
