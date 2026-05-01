from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import String, Float, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from database import Base


class TradeDirection(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"


class TradeStatus(str, enum.Enum):
    PENDING = "pending"
    OPEN = "open"
    CLOSED = "closed"
    REJECTED = "rejected"


class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticket: Mapped[Optional[int]] = mapped_column(nullable=True)
    symbol: Mapped[str] = mapped_column(String(20))
    direction: Mapped[TradeDirection] = mapped_column(SAEnum(TradeDirection))
    volume: Mapped[float] = mapped_column(Float)
    entry_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    current_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sl: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    tp: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pnl: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[TradeStatus] = mapped_column(SAEnum(TradeStatus), default=TradeStatus.PENDING)
    mode: Mapped[str] = mapped_column(String(10), default="scalp")
    comment: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    opened_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    closed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "ticket": self.ticket,
            "symbol": self.symbol,
            "direction": self.direction.value if self.direction else None,
            "volume": self.volume,
            "entry_price": self.entry_price,
            "current_price": self.current_price,
            "sl": self.sl,
            "tp": self.tp,
            "pnl": self.pnl,
            "status": self.status.value if self.status else None,
            "mode": self.mode,
            "comment": self.comment,
            "opened_at": self.opened_at.isoformat() if self.opened_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
