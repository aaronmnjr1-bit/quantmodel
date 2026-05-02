from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from loguru import logger


@dataclass
class RiskParameters:
    risk_pct: float = 1.0
    max_positions: int = 5
    daily_loss_limit: float = 3.0  # % of account balance
    mode: str = "scalp"  # scalp | swing

    def to_dict(self) -> dict[str, Any]:
        return {
            "risk_pct": self.risk_pct,
            "max_positions": self.max_positions,
            "daily_loss_limit": self.daily_loss_limit,
            "mode": self.mode,
        }


class RiskManager:
    """
    Manages position sizing, trade validation, and portfolio risk metrics.
    """

    def position_size(
        self,
        account_balance: float,
        risk_pct: float,
        sl_pips: float,
        pip_value: float = 10.0,
    ) -> float:
        """
        Calculate position size using fixed-fraction risk model.

        position_size = (account_balance × risk_pct / 100) / (sl_pips × pip_value)
        """
        if sl_pips <= 0 or pip_value <= 0:
            return 0.01  # Minimum lot size

        risk_amount = account_balance * risk_pct / 100
        raw = risk_amount / (sl_pips * pip_value)

        # Round to nearest 0.01 lot
        size = math.floor(raw * 100) / 100
        return max(0.01, min(size, 50.0))

    def check_max_positions(
        self, current_positions: int, max_positions: int
    ) -> bool:
        """Returns True if a new position can be opened."""
        return current_positions < max_positions

    def check_daily_loss_limit(
        self,
        daily_pnl: float,
        account_balance: float,
        daily_loss_limit_pct: float,
    ) -> bool:
        """Returns True if trading can continue (loss limit not breached)."""
        if account_balance <= 0:
            return False
        loss_pct = abs(min(daily_pnl, 0)) / account_balance * 100
        return loss_pct < daily_loss_limit_pct

    def calculate_var(
        self,
        positions: list[dict[str, Any]],
        confidence: float = 0.95,
    ) -> float:
        """
        Calculate 1-day Value at Risk at given confidence level.
        Uses parametric (variance-covariance) approach.
        """
        if not positions:
            return 0.0

        pnls = [p.get("pnl", 0.0) for p in positions]
        if len(pnls) < 2:
            return abs(pnls[0]) * (1 - confidence) if pnls else 0.0

        pnl_array = np.array(pnls, dtype=float)
        portfolio_mean = float(np.mean(pnl_array))
        portfolio_std = float(np.std(pnl_array))

        # z-score for confidence level
        z = {0.90: 1.282, 0.95: 1.645, 0.99: 2.326}.get(confidence, 1.645)
        var = portfolio_mean - z * portfolio_std
        return round(abs(var), 2)

    def validate_trade(
        self,
        trade_params: dict[str, Any],
        account_info: dict[str, Any],
        risk_params: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Validate a proposed trade against all risk rules.
        Returns dict with 'valid' bool and list of 'violations'.
        """
        violations: list[str] = []

        balance = account_info.get("balance", 0.0)
        equity = account_info.get("equity", balance)
        daily_pnl = account_info.get("profit", 0.0)

        max_pos = risk_params.get("max_positions", 5)
        daily_loss_pct = risk_params.get("daily_loss_limit", 3.0)
        risk_pct = risk_params.get("risk_pct", 1.0)

        # Check equity > 0
        if equity <= 0:
            violations.append("Equity is zero or negative.")

        # Check daily loss limit
        if not self.check_daily_loss_limit(daily_pnl, balance, daily_loss_pct):
            violations.append(
                f"Daily loss limit of {daily_loss_pct}% breached."
            )

        # Check volume
        volume = trade_params.get("volume", 0.0)
        if volume < 0.01:
            violations.append("Volume below minimum 0.01 lots.")

        if volume > 50.0:
            violations.append("Volume exceeds maximum 50 lots.")

        # Check symbol
        symbol = trade_params.get("symbol", "")
        if not symbol:
            violations.append("No symbol specified.")

        # Check SL is set
        sl = trade_params.get("sl")
        if sl is None or sl == 0:
            violations.append("Stop-loss is required for all trades.")

        # Risk per trade check
        if sl and trade_params.get("entry"):
            entry = trade_params["entry"]
            sl_distance = abs(entry - sl)
            risk_amount = sl_distance * volume * 100
            allowed_risk = balance * risk_pct / 100
            if risk_amount > allowed_risk * 2:  # Allow up to 2x with slippage
                violations.append(
                    f"Trade risk ${risk_amount:.2f} exceeds allowed ${allowed_risk:.2f}."
                )

        return {
            "valid": len(violations) == 0,
            "violations": violations,
            "trade_params": trade_params,
            "account_equity": equity,
        }
