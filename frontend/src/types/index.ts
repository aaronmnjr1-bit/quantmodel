export interface BotStatus {
  running: boolean
  mode: 'scalp' | 'swing'
  fundamental_enabled: boolean
  started_at: string | null
  stopped_at: string | null
  risk_params: RiskParams
  trades_today: number
  daily_pnl: number
  status_message: string
}

export interface Position {
  ticket: number
  symbol: string
  direction: 'buy' | 'sell'
  volume: number
  entry_price: number
  current_price: number
  sl: number | null
  tp: number | null
  pnl: number
  comment: string
}

export interface Trade {
  id: number
  ticket: number | null
  symbol: string
  direction: 'buy' | 'sell'
  volume: number
  entry_price: number | null
  sl: number | null
  tp: number | null
  pnl: number
  status: 'pending' | 'open' | 'closed' | 'rejected'
  mode: string
  opened_at: string | null
  closed_at: string | null
}

export interface RiskParams {
  risk_pct: number
  max_positions: number
  daily_loss_limit: number
  mode: string
}

export interface NewsEvent {
  id: string
  time: string
  currency: string
  event: string
  impact: 'high' | 'medium' | 'low'
  forecast: string | null
  previous: string | null
  actual: string | null
  deviation: number | null
  sentiment_score: number
  upcoming: boolean
}

export interface COTData {
  data: Record<string, COTSymbolData>
  summary: COTSummary
}

export interface COTSymbolData {
  symbol: string
  commercial_net: number
  speculator_net: number
  speculator_percentile: number
  crowding: 'crowded_long' | 'crowded_short' | 'neutral'
  signal: 'bullish' | 'bearish' | 'neutral'
  strength: number
  trend_change: boolean
}

export interface COTSummary {
  bullish_symbols: string[]
  bearish_symbols: string[]
  crowded_symbols: string[]
  average_strength: number
  market_bias: string
}

export interface VIXData {
  value: number
  prev_value: number
  change: number
  change_pct: number
  regime: 'low' | 'normal' | 'elevated' | 'extreme'
  regime_description: string
  regime_color: string
  trend: 'rising' | 'falling' | 'flat' | 'neutral'
  signal: string
  fear_greed: string
  near_term_prediction: string
  history: number[]
}

export interface FedWatchData {
  next_meeting: FedMeeting
  meetings: FedMeeting[]
  market_expectation: 'cut' | 'hold' | 'hike'
  cut_probability: number
  hike_probability: number
  hold_probability: number
  alignment_score: number
  current_rate: number
  expected_end_of_year_rate: number
}

export interface FedMeeting {
  date: string
  days_away: number
  probabilities: {
    hike_25bps: number
    hold: number
    cut_25bps: number
    cut_50bps: number
  }
  expected_rate: number
  current_rate: number
}

export interface SectorData {
  sectors: Record<string, SectorInfo>
  rotation: SectorRotation
  market_phase: 'expansion' | 'peak' | 'contraction' | 'trough'
  top_performers: string[]
  bottom_performers: string[]
  recommendation: string
}

export interface SectorInfo {
  ticker: string
  name: string
  category: 'cyclical' | 'defensive'
  return_30d: number
  momentum: 'positive' | 'negative'
}

export interface SectorRotation {
  cyclical_avg_return: number
  defensive_avg_return: number
  ratio: number
  signal: 'risk_on' | 'risk_off' | 'neutral'
  bias: 'bullish' | 'bearish' | 'neutral'
}

export interface AccountInfo {
  balance: number
  equity: number
  margin: number
  free_margin: number
  profit: number
  leverage: number
  currency: string
  server: string
  simulate?: boolean
}

export interface DashboardData {
  bot: BotStatus
  account: AccountInfo
  positions: Position[]
  analysis: {
    vix: VIXData
    cot: COTData
    fedwatch: FedWatchData
    sector: SectorData
  }
  news: NewsEvent[]
}

export type WebSocketMessage =
  | { type: 'state_update'; bot: BotStatus; vix: VIXData; timestamp: number }
  | { type: 'pong' }
