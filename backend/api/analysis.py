from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Request

router = APIRouter()

_VIX_TTL = 60        # 1 minute
_NEWS_TTL = 300      # 5 minutes
_COT_TTL = 3600      # 1 hour
_FEDWATCH_TTL = 1800 # 30 minutes
_SECTOR_TTL = 600    # 10 minutes


@router.get("/cot")
async def get_cot_data(request: Request) -> dict[str, Any]:
    cache = request.app.state.cache
    cached = await cache.get("analysis:cot")
    if cached:
        return cached
    cot = request.app.state.cot_analyzer
    data = await cot.get_analysis()
    await cache.set("analysis:cot", data, ttl=_COT_TTL)
    return data


@router.get("/news")
async def get_news(request: Request, limit: int = 20) -> dict[str, Any]:
    cache = request.app.state.cache
    cache_key = f"analysis:news:{limit}"
    cached = await cache.get(cache_key)
    if cached:
        return cached
    monitor = request.app.state.news_monitor
    events = monitor.get_high_impact_events(limit=limit)
    sentiment = await monitor.analyze_news_sentiment()
    data = {"events": events, "sentiment": sentiment}
    await cache.set(cache_key, data, ttl=_NEWS_TTL)
    return data


@router.get("/upcoming-events")
async def get_upcoming_events(request: Request) -> dict[str, Any]:
    monitor = request.app.state.news_monitor
    events = monitor.get_upcoming_events()
    return {"events": events}


@router.get("/vix")
async def get_vix(request: Request) -> dict[str, Any]:
    cache = request.app.state.cache
    cached = await cache.get("analysis:vix")
    if cached:
        return cached
    vix = request.app.state.vix_analyzer
    data = await vix.get_signal()
    await cache.set("analysis:vix", data, ttl=_VIX_TTL)
    return data


@router.get("/fedwatch")
async def get_fedwatch(request: Request) -> dict[str, Any]:
    cache = request.app.state.cache
    cached = await cache.get("analysis:fedwatch")
    if cached:
        return cached
    from analysis.fedwatch import FedWatchAnalyzer

    fw = FedWatchAnalyzer()
    data = await fw.get_market_positioning()
    await cache.set("analysis:fedwatch", data, ttl=_FEDWATCH_TTL)
    return data


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
async def get_sector_rotation(request: Request) -> dict[str, Any]:
    cache = request.app.state.cache
    cached = await cache.get("analysis:sector")
    if cached:
        return cached
    from analysis.sector_rotation import SectorRotationAnalyzer

    analyzer = SectorRotationAnalyzer()
    data = await analyzer.analyze_capital_flows()
    await cache.set("analysis:sector", data, ttl=_SECTOR_TTL)
    return data
