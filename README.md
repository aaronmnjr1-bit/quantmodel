# QuantModel — Algorithmic Trading Bot

A full-stack, production-grade algorithmic trading bot combining fundamental macro analysis with quantitative execution strategies across Gold, US indices, German DAX, and Japanese index futures.

---

## Architecture

```
quantmodel/
├── backend/            # Python FastAPI
│   ├── analysis/       # COT, news, sentiment, FedWatch, VIX, sector rotation
│   ├── api/            # REST endpoints
│   ├── core/           # WebSocket manager, bot state
│   ├── models/         # SQLAlchemy ORM models
│   ├── risk/           # Risk management engine
│   └── trading/        # MT5 engine, scalper, swing trader
├── frontend/           # React + TypeScript + Vite
│   └── src/
│       ├── api/        # Axios client
│       ├── components/ # UI panels
│       ├── hooks/      # useWebSocket, useBot
│       └── types/      # TypeScript interfaces
├── docker-compose.yml
└── .env.example
```

---

## Features

### Fundamental Analysis
- **COT/CFTC Reports** — commercial vs non-commercial positioning, crowding detection
- **Economic News** — ForexFactory scraping, impact classification, actual vs forecast deviation
- **Speech/Sentiment** — hawkish/dovish keyword scoring for Fed communications
- **FedWatch** — CME rate hike/cut probability tracking
- **VIX Regime** — fear/greed classification (low/normal/elevated/extreme)
- **Sector Rotation** — cyclical vs defensive relative strength, market phase detection

### Trading Engine
- **MT5 Integration** — MetaTrader 5 API with graceful simulate mode
- **Scalping Mode** — ATR-based high-frequency entries (SL = 1.5×ATR, TP = 2.0×ATR)
- **Swing Mode** — approval-based execution with pending trade queue
- **Supported Instruments** — XAUUSD, NAS100, US30, GER40, JP225, USDCAD

### Risk Management
- Kelly/fixed-fraction position sizing
- Daily loss limit enforcement
- Value at Risk (VaR 95%)
- Maximum concurrent positions

### Infrastructure
- FastAPI + uvicorn async backend
- React/TypeScript Bloomberg-terminal UI
- WebSocket real-time data (1–2 s updates)
- PostgreSQL historical storage
- Redis real-time cache
- Docker Compose orchestration

---

## Quick Start

### Prerequisites
- Docker >= 24 and Docker Compose v2
- (Optional) MetaTrader 5 terminal for live trading

### 1. Clone and configure
```bash
git clone https://github.com/aaronmnjr1-bit/quantmodel.git
cd quantmodel
cp .env.example .env
# Edit .env with your credentials
```

### 2. Start with Docker Compose
```bash
docker-compose up --build
```

Services:
| Service   | URL                        |
|-----------|----------------------------|
| Frontend  | http://localhost:3000       |
| Backend   | http://localhost:8000       |
| API Docs  | http://localhost:8000/docs  |
| Postgres  | localhost:5432              |
| Redis     | localhost:6379              |

### 3. Development (without Docker)

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

---

## Environment Variables

See `.env.example` for all required variables.

Key variables:
- `MT5_LOGIN`, `MT5_PASSWORD`, `MT5_SERVER` — MetaTrader 5 credentials
- `DATABASE_URL` — PostgreSQL connection string
- `REDIS_URL` — Redis connection string
- `SECRET_KEY` — JWT signing key

---

## Trading Modes

| Mode   | Entry Trigger    | SL       | TP       | Hold Time |
|--------|-----------------|----------|----------|-----------|
| Scalp  | ATR crossover   | 1.5xATR  | 2.0xATR  | Minutes   |
| Swing  | Manual approval | 2.0xATR  | 4.0xATR  | Hours-Days|

---

## Disclaimer

This software is for **educational and research purposes only**. Trading financial instruments carries significant risk of loss. Past performance is not indicative of future results. Always test in a demo account before deploying real capital.
