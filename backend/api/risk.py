from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


class RiskParamsRequest(BaseModel):
    risk_pct: float = 1.0
    max_positions: int = 5
    daily_loss_limit: float = 3.0
    mode: str = "scalp"


@router.get("/params")
async def get_risk_params(request: Request) -> dict[str, Any]:
    bot_state = request.app.state.bot_state
    return bot_state.risk_params


@router.put("/params")
async def update_risk_params(
    request: Request, params: RiskParamsRequest
) -> dict[str, Any]:
    bot_state = request.app.state.bot_state
    bot_state.risk_params.update(params.model_dump())
    return {"status": "updated", "params": bot_state.risk_params}


@router.get("/var")
async def get_var(request: Request) -> dict[str, Any]:
    from trading.mt5_engine import MT5Engine
    from risk.risk_manager import RiskManager

    engine = MT5Engine()
    positions = await engine.get_positions()
    rm = RiskManager()
    var = rm.calculate_var(positions)
    return {"var_95": var, "positions_count": len(positions)}


@router.post("/validate")
async def validate_trade(
    request: Request, trade: dict[str, Any]
) -> dict[str, Any]:
    from trading.mt5_engine import MT5Engine
    from risk.risk_manager import RiskManager

    engine = MT5Engine()
    account_info = await engine.get_account_info()
    rm = RiskManager()
    bot_state = request.app.state.bot_state
    result = rm.validate_trade(trade, account_info, bot_state.risk_params)
    return result
