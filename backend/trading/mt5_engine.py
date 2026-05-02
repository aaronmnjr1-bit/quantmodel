from __future__ import annotations

import asyncio
import random
import time
from typing import Any

from loguru import logger

SUPPORTED_SYMBOLS: list[str] = [
    "XAUUSD",   # Gold
    "NAS100",   # Nasdaq 100
    "US30",     # Dow Jones
    "GER40",    # German DAX
    "JP225",    # Nikkei 225
    "USDCAD",   # Canadian Dollar
]

_MT5_AVAILABLE = False
try:
    import MetaTrader5 as mt5
    _MT5_AVAILABLE = True
except ImportError:
    mt5 = None  # type: ignore

# Simulated in-memory position store for simulate mode
_SIM_POSITIONS: list[dict[str, Any]] = []
_SIM_TICKET_COUNTER = 1000


class MT5Engine:
    """
    MetaTrader 5 trading engine.
    Operates in simulate mode when MT5 is not installed or not connected.
    """

    def __init__(self) -> None:
        self._connected = False
        self._simulate = not _MT5_AVAILABLE

    def connect(self, login: int, password: str, server: str) -> bool:
        if self._simulate:
            logger.info("MT5 simulate mode active (MT5 not installed)")
            self._connected = True
            return True
        try:
            if not mt5.initialize(login=login, password=password, server=server):
                logger.error(f"MT5 initialize failed: {mt5.last_error()}")
                self._simulate = True
            else:
                self._connected = True
                logger.info("MT5 connected successfully")
        except Exception as exc:
            logger.warning(f"MT5 connect error: {exc}. Falling back to simulate mode.")
            self._simulate = True
            self._connected = True
        return self._connected

    def disconnect(self) -> None:
        if not self._simulate and _MT5_AVAILABLE:
            mt5.shutdown()
        self._connected = False

    async def get_account_info(self) -> dict[str, Any]:
        if self._simulate:
            return self._mock_account_info()
        try:
            info = mt5.account_info()
            if info is None:
                return self._mock_account_info()
            return {
                "balance": info.balance,
                "equity": info.equity,
                "margin": info.margin,
                "free_margin": info.margin_free,
                "profit": info.profit,
                "leverage": info.leverage,
                "currency": info.currency,
                "server": info.server,
            }
        except Exception:
            return self._mock_account_info()

    def _mock_account_info(self) -> dict[str, Any]:
        equity = 10000.0 + random.uniform(-200, 500)
        balance = 10000.0
        profit = equity - balance
        return {
            "balance": balance,
            "equity": round(equity, 2),
            "margin": round(random.uniform(200, 800), 2),
            "free_margin": round(equity - random.uniform(200, 800), 2),
            "profit": round(profit, 2),
            "leverage": 100,
            "currency": "USD",
            "server": "SimulationServer",
            "simulate": True,
        }

    async def get_positions(self) -> list[dict[str, Any]]:
        if self._simulate:
            return self._update_sim_positions()
        try:
            raw = mt5.positions_get()
            if raw is None:
                return []
            return [
                {
                    "ticket": p.ticket,
                    "symbol": p.symbol,
                    "direction": "buy" if p.type == 0 else "sell",
                    "volume": p.volume,
                    "entry_price": p.price_open,
                    "current_price": p.price_current,
                    "sl": p.sl,
                    "tp": p.tp,
                    "pnl": p.profit,
                    "comment": p.comment,
                }
                for p in raw
            ]
        except Exception:
            return self._update_sim_positions()

    def _update_sim_positions(self) -> list[dict[str, Any]]:
        for pos in _SIM_POSITIONS:
            if pos["direction"] == "buy":
                pos["current_price"] = round(
                    pos["entry_price"] * (1 + random.uniform(-0.003, 0.005)), 5
                )
            else:
                pos["current_price"] = round(
                    pos["entry_price"] * (1 - random.uniform(-0.003, 0.005)), 5
                )
            pos["pnl"] = round(
                (pos["current_price"] - pos["entry_price"])
                * (1 if pos["direction"] == "buy" else -1)
                * pos["volume"]
                * 100,
                2,
            )
        return list(_SIM_POSITIONS)

    async def get_symbol_info(self, symbol: str) -> dict[str, Any]:
        if self._simulate:
            return self._mock_symbol_info(symbol)
        try:
            tick = mt5.symbol_info_tick(symbol)
            info = mt5.symbol_info(symbol)
            if tick is None or info is None:
                return self._mock_symbol_info(symbol)
            return {
                "symbol": symbol,
                "bid": tick.bid,
                "ask": tick.ask,
                "spread": round(tick.ask - tick.bid, 5),
                "digits": info.digits,
                "volume_min": info.volume_min,
                "volume_step": info.volume_step,
                "contract_size": info.trade_contract_size,
            }
        except Exception:
            return self._mock_symbol_info(symbol)

    def _mock_symbol_info(self, symbol: str) -> dict[str, Any]:
        base_prices = {
            "XAUUSD": 2050.0,
            "NAS100": 17500.0,
            "US30": 38500.0,
            "GER40": 17200.0,
            "JP225": 38000.0,
            "USDCAD": 1.3600,
        }
        base = base_prices.get(symbol, 1.0)
        spread_pct = 0.0002
        bid = round(base * (1 - spread_pct / 2), 5)
        ask = round(base * (1 + spread_pct / 2), 5)
        return {
            "symbol": symbol,
            "bid": bid,
            "ask": ask,
            "spread": round(ask - bid, 5),
            "digits": 2 if base > 100 else 5,
            "volume_min": 0.01,
            "volume_step": 0.01,
            "contract_size": 100.0,
        }

    async def execute_trade(
        self,
        symbol: str,
        direction: str,
        volume: float,
        sl: float | None = None,
        tp: float | None = None,
        comment: str = "",
    ) -> dict[str, Any]:
        global _SIM_TICKET_COUNTER

        info = await self.get_symbol_info(symbol)

        if self._simulate:
            price = info["ask"] if direction == "buy" else info["bid"]
            ticket = _SIM_TICKET_COUNTER
            _SIM_TICKET_COUNTER += 1

            position = {
                "ticket": ticket,
                "symbol": symbol,
                "direction": direction,
                "volume": volume,
                "entry_price": price,
                "current_price": price,
                "sl": sl or round(price * (0.998 if direction == "buy" else 1.002), 5),
                "tp": tp or round(price * (1.004 if direction == "buy" else 0.996), 5),
                "pnl": 0.0,
                "comment": comment or "QuantModel",
            }
            _SIM_POSITIONS.append(position)
            logger.info(f"[SIM] Opened {direction} {volume} {symbol} @ {price} | ticket={ticket}")
            return {
                "success": True,
                "ticket": ticket,
                "symbol": symbol,
                "direction": direction,
                "volume": volume,
                "price": price,
                "simulate": True,
            }

        # Live MT5 execution
        try:
            price = mt5.symbol_info_tick(symbol)
            entry = price.ask if direction == "buy" else price.bid
            order_type = mt5.ORDER_TYPE_BUY if direction == "buy" else mt5.ORDER_TYPE_SELL

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": float(volume),
                "type": order_type,
                "price": entry,
                "sl": sl or 0.0,
                "tp": tp or 0.0,
                "deviation": 20,
                "magic": 202401,
                "comment": comment or "QuantModel",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return {"success": False, "error": result.comment, "retcode": result.retcode}

            return {
                "success": True,
                "ticket": result.order,
                "symbol": symbol,
                "direction": direction,
                "volume": volume,
                "price": result.price,
            }
        except Exception as exc:
            logger.error(f"MT5 execute_trade error: {exc}")
            return {"success": False, "error": str(exc)}

    async def close_position(self, ticket: int) -> dict[str, Any]:
        global _SIM_POSITIONS

        if self._simulate:
            before = len(_SIM_POSITIONS)
            _SIM_POSITIONS = [p for p in _SIM_POSITIONS if p["ticket"] != ticket]
            if len(_SIM_POSITIONS) < before:
                logger.info(f"[SIM] Closed position ticket={ticket}")
                return {"success": True, "ticket": ticket}
            return {"success": False, "error": "Position not found"}

        try:
            positions = mt5.positions_get(ticket=ticket)
            if not positions:
                return {"success": False, "error": "Position not found"}

            pos = positions[0]
            order_type = mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY
            price = (
                mt5.symbol_info_tick(pos.symbol).bid
                if pos.type == 0
                else mt5.symbol_info_tick(pos.symbol).ask
            )

            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": pos.symbol,
                "volume": pos.volume,
                "type": order_type,
                "position": ticket,
                "price": price,
                "deviation": 20,
                "magic": 202401,
                "comment": "QuantModel Close",
            }

            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                return {"success": False, "error": result.comment}

            return {"success": True, "ticket": ticket, "close_price": price}
        except Exception as exc:
            logger.error(f"MT5 close_position error: {exc}")
            return {"success": False, "error": str(exc)}
