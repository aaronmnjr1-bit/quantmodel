from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

from trading.trade_repository import TradeRepository

router = APIRouter()
_trade_repo = TradeRepository()


class TradeRequest(BaseModel):
    symbol: str
    direction: str  # buy | sell
    volume: float
    sl: float | None = None
    tp: float | None = None
    comment: str = ""


class BotModeRequest(BaseModel):
    mode: str  # scalp | swing


@router.post("/start")
async def start_bot(request: Request, mode_req: BotModeRequest) -> dict[str, Any]:
    bot_state = request.app.state.bot_state
    bot_state.start(mode_req.mode)
    return {"status": "started", "mode": bot_state.mode}


@router.post("/stop")
async def stop_bot(request: Request) -> dict[str, Any]:
    bot_state = request.app.state.bot_state
    bot_state.stop()
    return {"status": "stopped"}


@router.get("/status")
async def get_status(request: Request) -> dict[str, Any]:
    bot_state = request.app.state.bot_state
    return bot_state.to_dict()


@router.post("/trade")
async def execute_trade(request: Request, trade_req: TradeRequest) -> dict[str, Any]:
    from trading.mt5_engine import MT5Engine

    engine = MT5Engine()
    bot_state = request.app.state.bot_state
    try:
        result = await engine.execute_trade(
            symbol=trade_req.symbol,
            direction=trade_req.direction,
            volume=trade_req.volume,
            sl=trade_req.sl,
            tp=trade_req.tp,
            comment=trade_req.comment,
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Trade execution failed")

    if result.get("success"):
        await _trade_repo.save_trade(
            symbol=trade_req.symbol,
            direction=trade_req.direction,
            volume=trade_req.volume,
            entry_price=result.get("price"),
            sl=trade_req.sl,
            tp=trade_req.tp,
            ticket=result.get("ticket"),
            mode=bot_state.mode,
            comment=trade_req.comment,
            status="open",
        )
        bot_state.trades_today += 1

    return result


@router.get("/positions")
async def get_positions(request: Request) -> dict[str, Any]:
    from trading.mt5_engine import MT5Engine

    engine = MT5Engine()
    positions = await engine.get_positions()
    return {"positions": positions}


@router.delete("/positions/{ticket}")
async def close_position(ticket: int, request: Request) -> dict[str, Any]:
    from trading.mt5_engine import MT5Engine

    engine = MT5Engine()

    # Capture PnL from open position before closing
    positions = await engine.get_positions()
    pos_pnl = next(
        (p.get("pnl", 0.0) for p in positions if p.get("ticket") == ticket), 0.0
    )

    try:
        result = await engine.close_position(ticket)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to close position")

    if result.get("success"):
        await _trade_repo.close_trade(ticket, close_pnl=pos_pnl)

    return result


@router.get("/pending")
async def get_pending_trades(request: Request) -> dict[str, Any]:
    from trading.swing_trader import SwingTrader

    trader = SwingTrader()
    return {"pending": trader.get_pending_trades()}


@router.post("/approve/{trade_id}")
async def approve_trade(trade_id: str, request: Request) -> dict[str, Any]:
    from trading.swing_trader import SwingTrader

    trader = SwingTrader()
    result = trader.approve_trade(trade_id)
    if not result:
        raise HTTPException(status_code=404, detail="Trade not found")
    return {"status": "approved", "trade_id": trade_id}


@router.delete("/pending/{trade_id}")
async def reject_trade(trade_id: str, request: Request) -> dict[str, Any]:
    from trading.swing_trader import SwingTrader

    trader = SwingTrader()
    result = trader.reject_trade(trade_id)
    if not result:
        raise HTTPException(status_code=404, detail="Trade not found")
    return {"status": "rejected", "trade_id": trade_id}


@router.get("/history")
async def get_trade_history(
    limit: int = 100, symbol: str | None = None
) -> dict[str, Any]:
    trades = await _trade_repo.get_history(limit=limit, symbol=symbol)
    return {"trades": trades, "count": len(trades)}
