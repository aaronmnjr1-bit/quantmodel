from __future__ import annotations

import datetime
from dataclasses import dataclass, field, asdict
from typing import Any

from config import settings


@dataclass
class BotState:
    """Global mutable state for the trading bot."""

    running: bool = False
    mode: str = "scalp"  # scalp | swing
    fundamental_enabled: bool = True
    started_at: datetime.datetime | None = None
    stopped_at: datetime.datetime | None = None
    risk_params: dict[str, Any] = field(default_factory=lambda: {
        "risk_pct": settings.DEFAULT_RISK_PCT,
        "max_positions": settings.DEFAULT_MAX_POSITIONS,
        "daily_loss_limit": settings.DEFAULT_DAILY_LOSS_LIMIT,
        "mode": settings.DEFAULT_TRADING_MODE,
    })
    trades_today: int = 0
    daily_pnl: float = 0.0
    status_message: str = "Idle"

    def start(self, mode: str = "scalp") -> None:
        self.running = True
        self.mode = mode
        self.started_at = datetime.datetime.now(datetime.timezone.utc)
        self.status_message = f"Running ({mode.upper()})"

    def stop(self) -> None:
        self.running = False
        self.stopped_at = datetime.datetime.now(datetime.timezone.utc)
        self.status_message = "Stopped"

    def to_dict(self) -> dict[str, Any]:
        return {
            "running": self.running,
            "mode": self.mode,
            "fundamental_enabled": self.fundamental_enabled,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "stopped_at": self.stopped_at.isoformat() if self.stopped_at else None,
            "risk_params": self.risk_params,
            "trades_today": self.trades_today,
            "daily_pnl": self.daily_pnl,
            "status_message": self.status_message,
        }
