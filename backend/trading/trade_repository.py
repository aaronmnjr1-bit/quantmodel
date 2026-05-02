from __future__ import annotations

import datetime
from typing import Any

from loguru import logger
from sqlalchemy import select, func

from database import AsyncSessionLocal
from models.trade import Trade, TradeDirection, TradeStatus


class TradeRepository:
    """Async repository for persisting and querying trade records."""

    async def save_trade(
        self,
        symbol: str,
        direction: str,
        volume: float,
        entry_price: float | None,
        sl: float | None,
        tp: float | None,
        ticket: int | None,
        mode: str = "scalp",
        comment: str = "",
        status: str = "open",
    ) -> Trade | None:
        """Persist a new trade record and return the saved instance."""
        try:
            async with AsyncSessionLocal() as session:
                trade = Trade(
                    ticket=ticket,
                    symbol=symbol,
                    direction=TradeDirection(direction),
                    volume=volume,
                    entry_price=entry_price,
                    sl=sl,
                    tp=tp,
                    pnl=0.0,
                    status=TradeStatus(status),
                    mode=mode,
                    comment=comment,
                    opened_at=datetime.datetime.now(datetime.timezone.utc),
                )
                session.add(trade)
                await session.commit()
                await session.refresh(trade)
                return trade
        except Exception as exc:
            logger.warning(f"Failed to persist trade: {exc}")
            return None

    async def close_trade(
        self, ticket: int, close_pnl: float = 0.0
    ) -> bool:
        """Mark a trade as closed and record final PnL."""
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(Trade).where(Trade.ticket == ticket)
                )
                trade = result.scalar_one_or_none()
                if trade is None:
                    return False
                trade.status = TradeStatus.CLOSED
                trade.pnl = close_pnl
                trade.closed_at = datetime.datetime.now(datetime.timezone.utc)
                await session.commit()
                return True
        except Exception as exc:
            logger.warning(f"Failed to close trade {ticket}: {exc}")
            return False

    async def get_history(
        self,
        limit: int = 100,
        symbol: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return recent trade history ordered by opened_at desc."""
        try:
            async with AsyncSessionLocal() as session:
                stmt = select(Trade).order_by(Trade.opened_at.desc()).limit(limit)
                if symbol:
                    stmt = stmt.where(Trade.symbol == symbol)
                result = await session.execute(stmt)
                return [t.to_dict() for t in result.scalars().all()]
        except Exception as exc:
            logger.warning(f"Failed to fetch trade history: {exc}")
            return []

    async def get_performance_stats(self) -> dict[str, Any]:
        """Calculate aggregate performance statistics from closed trades."""
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(Trade).where(Trade.status == TradeStatus.CLOSED)
                )
                closed = result.scalars().all()

                if not closed:
                    return _empty_performance()

                total = len(closed)
                wins = [t for t in closed if t.pnl > 0]
                losses = [t for t in closed if t.pnl <= 0]
                win_rate = len(wins) / total if total else 0.0

                total_pnl = sum(t.pnl for t in closed)
                gross_profit = sum(t.pnl for t in wins)
                gross_loss = abs(sum(t.pnl for t in losses))
                profit_factor = gross_profit / gross_loss if gross_loss else float("inf")

                avg_win = gross_profit / len(wins) if wins else 0.0
                avg_loss = -(gross_loss / len(losses)) if losses else 0.0

                # Peak-to-trough drawdown using running cumulative PnL
                pnls = sorted(closed, key=lambda t: t.opened_at or datetime.datetime.min)
                cumulative = 0.0
                peak = 0.0
                max_dd = 0.0
                for t in pnls:
                    cumulative += t.pnl
                    if cumulative > peak:
                        peak = cumulative
                    dd = (peak - cumulative) / max(abs(peak), 1) * 100
                    if dd > max_dd:
                        max_dd = dd

                # Sharpe-like ratio (mean / std of PnLs, annualised roughly)
                import numpy as np
                pnl_arr = [t.pnl for t in closed]
                sharpe = (
                    float(np.mean(pnl_arr)) / max(float(np.std(pnl_arr)), 0.01)
                    if len(pnl_arr) > 1
                    else 0.0
                )

                return {
                    "total_trades": total,
                    "win_rate": round(win_rate, 3),
                    "profit_factor": round(profit_factor, 2),
                    "sharpe_ratio": round(sharpe, 2),
                    "max_drawdown": round(max_dd, 2),
                    "avg_win": round(avg_win, 2),
                    "avg_loss": round(avg_loss, 2),
                    "total_pnl": round(total_pnl, 2),
                }
        except Exception as exc:
            logger.warning(f"Performance stats error: {exc}")
            return _empty_performance()


def _empty_performance() -> dict[str, Any]:
    return {
        "total_trades": 0,
        "win_rate": 0.0,
        "profit_factor": 0.0,
        "sharpe_ratio": 0.0,
        "max_drawdown": 0.0,
        "avg_win": 0.0,
        "avg_loss": 0.0,
        "total_pnl": 0.0,
    }
