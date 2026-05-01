import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

client.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  },
)

export default client

// ── Typed API helpers ──────────────────────────────────────────────────────────

export const tradingApi = {
  startBot: (mode: string) =>
    client.post('/api/trading/start', { mode }),
  stopBot: () =>
    client.post('/api/trading/stop'),
  getStatus: () =>
    client.get('/api/trading/status'),
  getPositions: () =>
    client.get('/api/trading/positions'),
  closePosition: (ticket: number) =>
    client.delete(`/api/trading/positions/${ticket}`),
  getPendingTrades: () =>
    client.get('/api/trading/pending'),
  approveTrade: (tradeId: string) =>
    client.post(`/api/trading/approve/${tradeId}`),
  rejectTrade: (tradeId: string) =>
    client.delete(`/api/trading/pending/${tradeId}`),
}

export const analysisApi = {
  getCOT: () =>
    client.get('/api/analysis/cot'),
  getNews: (limit = 20) =>
    client.get(`/api/analysis/news?limit=${limit}`),
  getUpcomingEvents: () =>
    client.get('/api/analysis/upcoming-events'),
  getVIX: () =>
    client.get('/api/analysis/vix'),
  getFedWatch: () =>
    client.get('/api/analysis/fedwatch'),
  getSectorRotation: () =>
    client.get('/api/analysis/sector-rotation'),
  analyzeSentiment: (text: string) =>
    client.get(`/api/analysis/sentiment?text=${encodeURIComponent(text)}`),
}

export const riskApi = {
  getParams: () =>
    client.get('/api/risk/params'),
  updateParams: (params: object) =>
    client.put('/api/risk/params', params),
  getVaR: () =>
    client.get('/api/risk/var'),
}

export const dashboardApi = {
  getSummary: () =>
    client.get('/api/dashboard/summary'),
  getPerformance: () =>
    client.get('/api/dashboard/performance'),
}
