from __future__ import annotations

import datetime
from typing import Optional

from sqlalchemy import String, Float, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    analysis_type: Mapped[str] = mapped_column(String(50))  # cot, vix, news, fedwatch, sector
    symbol: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    signal: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # bullish/bearish/neutral
    strength: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    raw_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "analysis_type": self.analysis_type,
            "symbol": self.symbol,
            "signal": self.signal,
            "strength": self.strength,
            "raw_data": self.raw_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
