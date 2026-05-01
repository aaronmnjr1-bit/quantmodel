from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/summary")
async def get_dashboard_summary(request: Request) -> dict[str, Any]:
    from trading.mt5_engine import MT5Engine
    from analysis.vix_analyzer import VIXAnalyzer
    from analysis.fedwatch import FedWatchAnalyzer
    from analysis.sector_rotation import SectorRotationAnalyzer

    bot_state = request.app.state.bot_state
    cot = request.app.state.cot_analyzer
    monitor = request.app.state.news_monitor

    engine = MT5Engine()
    account_info = await engine.get_account_info()
    positions = await engine.get_positions()

    vix_signal = await VIXAnalyzer().get_signal()
    cot_analysis = await cot.get_analysis()
    fedwatch = await FedWatchAnalyzer().get_market_positioning()
    sector = await SectorRotationAnalyzer().analyze_capital_flows()
    news_events = monitor.get_high_impact_events(limit=10)

    return {
        "bot": bot_state.to_dict(),
        "account": account_info,
        "positions": positions,
        "analysis": {
            "vix": vix_signal,
            "cot": cot_analysis,
            "fedwatch": fedwatch,
            "sector": sector,
        },
        "news": news_events,
    }


@router.get("/performance")
async def get_performance() -> dict[str, Any]:
    """Return mock performance metrics."""
    return {
        "total_trades": 47,
        "win_rate": 0.638,
        "profit_factor": 1.82,
        "sharpe_ratio": 1.34,
        "max_drawdown": 4.2,
        "avg_win": 120.5,
        "avg_loss": -66.3,
        "total_pnl": 3247.80,
    }
