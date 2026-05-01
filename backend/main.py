from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from config import settings
from core.websocket_manager import WebSocketManager
from core.bot_state import BotState
from api.trading import router as trading_router
from api.analysis import router as analysis_router
from api.risk import router as risk_router
from api.dashboard import router as dashboard_router
from analysis.news_monitor import NewsMonitor
from analysis.vix_analyzer import VIXAnalyzer
from analysis.cot_analyzer import COTAnalyzer

ws_manager = WebSocketManager()
bot_state = BotState()
news_monitor = NewsMonitor()
vix_analyzer = VIXAnalyzer()
cot_analyzer = COTAnalyzer()


async def _broadcast_loop() -> None:
    """Push real-time state updates to all connected WebSocket clients."""
    while True:
        try:
            vix_data = await vix_analyzer.get_signal()
            payload = {
                "type": "state_update",
                "bot": bot_state.to_dict(),
                "vix": vix_data,
                "timestamp": asyncio.get_event_loop().time(),
            }
            await ws_manager.broadcast(payload)
        except Exception as exc:
            logger.warning(f"Broadcast loop error: {exc}")
        await asyncio.sleep(1.5)


async def _news_loop() -> None:
    """Periodically refresh news / economic calendar."""
    while True:
        try:
            await news_monitor.refresh()
        except Exception as exc:
            logger.warning(f"News refresh error: {exc}")
        await asyncio.sleep(settings.SCRAPE_INTERVAL_SECONDS)


async def _cot_loop() -> None:
    """Periodically refresh COT report data (weekly cadence)."""
    while True:
        try:
            await cot_analyzer.refresh()
        except Exception as exc:
            logger.warning(f"COT refresh error: {exc}")
        await asyncio.sleep(3600)  # once per hour is sufficient


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting QuantModel backend…")
    tasks = [
        asyncio.create_task(_broadcast_loop()),
        asyncio.create_task(_news_loop()),
        asyncio.create_task(_cot_loop()),
    ]
    app.state.ws_manager = ws_manager
    app.state.bot_state = bot_state
    app.state.news_monitor = news_monitor
    app.state.vix_analyzer = vix_analyzer
    app.state.cot_analyzer = cot_analyzer
    yield
    for task in tasks:
        task.cancel()
    logger.info("QuantModel backend shut down.")


app = FastAPI(
    title="QuantModel API",
    description="Algorithmic trading bot — fundamental + quant",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trading_router, prefix="/api/trading", tags=["trading"])
app.include_router(analysis_router, prefix="/api/analysis", tags=["analysis"])
app.include_router(risk_router, prefix="/api/risk", tags=["risk"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "version": "1.0.0"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await ws_manager.handle_client_message(websocket, data)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
