import { BarChart2, TrendingUp, Calendar, AlertTriangle } from 'lucide-react'
import type { VIXData, FedWatchData, COTData } from '../types'

interface Props {
  vix: VIXData | null
  fedwatch: FedWatchData | null
  cot: COTData | null
}

function VIXGauge({ vix }: { vix: VIXData }) {
  const max = 50
  const pct = Math.min((vix.value / max) * 100, 100)
  const barColor =
    vix.regime === 'low' ? '#00c853'
    : vix.regime === 'normal' ? '#ffab00'
    : vix.regime === 'elevated' ? '#ff6d00'
    : '#ff1744'

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs text-[#6b7280]">VIX — Fear Index</span>
        <span className="text-xl font-mono font-bold" style={{ color: barColor }}>
          {vix.value.toFixed(2)}
        </span>
      </div>
      <div className="w-full h-3 bg-[#1a1a1a] rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${pct}%`, background: barColor }}
        />
      </div>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase" style={{ color: barColor }}>
          {vix.regime} volatility
        </span>
        <span className={`text-xs font-mono ${vix.change >= 0 ? 'text-[#ff1744]' : 'text-[#00c853]'}`}>
          {vix.change >= 0 ? '▲' : '▼'} {Math.abs(vix.change).toFixed(2)} ({Math.abs(vix.change_pct).toFixed(1)}%)
        </span>
      </div>
      <p className="text-xs text-[#6b7280]">{vix.regime_description}</p>
    </div>
  )
}

function FedWatchBars({ fw }: { fw: FedWatchData }) {
  const bars = [
    { label: 'HIKE', pct: fw.hike_probability * 100, color: '#ff1744' },
    { label: 'HOLD', pct: fw.hold_probability * 100, color: '#ffab00' },
    { label: 'CUT', pct: fw.cut_probability * 100, color: '#00c853' },
  ]
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs text-[#6b7280]">Next Meeting</span>
        <span className="text-xs font-mono text-[#e0e0e0]">
          {fw.next_meeting?.date ?? '—'} ({fw.next_meeting?.days_away}d)
        </span>
      </div>
      {bars.map((b) => (
        <div key={b.label} className="flex items-center gap-2">
          <span className="text-xs font-mono text-[#6b7280] w-8">{b.label}</span>
          <div className="flex-1 h-2 bg-[#1a1a1a] rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{ width: `${b.pct.toFixed(0)}%`, background: b.color }}
            />
          </div>
          <span className="text-xs font-mono font-bold w-10 text-right" style={{ color: b.color }}>
            {b.pct.toFixed(0)}%
          </span>
        </div>
      ))}
      <div className="flex items-center justify-between pt-1">
        <span className="text-xs text-[#6b7280]">Market Expects</span>
        <span className={`text-xs font-bold uppercase px-2 py-0.5 rounded ${
          fw.market_expectation === 'cut' ? 'bg-[#00c853]/10 text-[#00c853]'
          : fw.market_expectation === 'hike' ? 'bg-[#ff1744]/10 text-[#ff1744]'
          : 'bg-[#ffab00]/10 text-[#ffab00]'
        }`}>
          {fw.market_expectation}
        </span>
      </div>
    </div>
  )
}

function COTBar({ label, value, total }: { label: string; value: number; total: number }) {
  const pct = total !== 0 ? Math.abs(value / total) * 100 : 50
  const isPositive = value > 0
  return (
    <div className="space-y-1">
      <div className="flex justify-between">
        <span className="text-xs text-[#6b7280]">{label}</span>
        <span className={`text-xs font-mono font-semibold ${isPositive ? 'text-[#00c853]' : 'text-[#ff1744]'}`}>
          {value > 0 ? '+' : ''}{value}K
        </span>
      </div>
      <div className="flex items-center gap-1 h-2">
        <div className="flex-1 h-full bg-[#1a1a1a] rounded-full overflow-hidden flex justify-end">
          {!isPositive && (
            <div
              className="h-full bg-[#ff1744] rounded-full"
              style={{ width: `${Math.min(pct, 100)}%` }}
            />
          )}
        </div>
        <div className="w-px h-full bg-[#2a2a2a]" />
        <div className="flex-1 h-full bg-[#1a1a1a] rounded-full overflow-hidden">
          {isPositive && (
            <div
              className="h-full bg-[#00c853] rounded-full"
              style={{ width: `${Math.min(pct, 100)}%` }}
            />
          )}
        </div>
      </div>
    </div>
  )
}

export default function FundamentalPanel({ vix, fedwatch, cot }: Props) {
  const mockVix: VIXData = {
    value: 18.5, prev_value: 17.2, change: 1.3, change_pct: 7.6,
    regime: 'normal', regime_description: 'Normal volatility',
    regime_color: 'yellow', trend: 'rising', signal: 'neutral',
    fear_greed: 'neutral', near_term_prediction: 'neutral', history: [],
  }

  const mockFw: FedWatchData = {
    next_meeting: { date: '2024-05-01', days_away: 60, probabilities: { hike_25bps: 0.08, hold: 0.57, cut_25bps: 0.30, cut_50bps: 0.05 }, expected_rate: 5.2, current_rate: 5.375 },
    meetings: [], market_expectation: 'hold',
    cut_probability: 0.35, hike_probability: 0.08, hold_probability: 0.57,
    alignment_score: -27, current_rate: 5.375, expected_end_of_year_rate: 5.0,
  }

  const v = vix ?? mockVix
  const fw = fedwatch ?? mockFw

  const goldCOT = cot?.data?.['Gold']
  const eurCOT = cot?.data?.['EUR']

  return (
    <div className="terminal-card h-full">
      <div className="terminal-card-header">
        <div className="flex items-center gap-2">
          <BarChart2 className="w-4 h-4 text-[#00e5ff]" />
          <span className="text-xs font-semibold text-[#e0e0e0] uppercase tracking-wider">
            Fundamental Analysis
          </span>
        </div>
      </div>

      <div className="p-4 space-y-5">
        {/* VIX */}
        <div>
          <VIXGauge vix={v} />
        </div>

        <div className="border-t border-[#1e1e1e]" />

        {/* FedWatch */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Calendar className="w-3.5 h-3.5 text-[#ffab00]" />
            <span className="text-xs font-semibold text-[#e0e0e0] uppercase tracking-wider">FedWatch</span>
            <span className="text-xs font-mono text-[#6b7280]">Rate {fw.current_rate.toFixed(2)}%</span>
          </div>
          <FedWatchBars fw={fw} />
        </div>

        <div className="border-t border-[#1e1e1e]" />

        {/* COT */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp className="w-3.5 h-3.5 text-[#2979ff]" />
            <span className="text-xs font-semibold text-[#e0e0e0] uppercase tracking-wider">COT Positioning</span>
          </div>
          <div className="space-y-3">
            {goldCOT && (
              <COTBar
                label="Gold — Large Specs"
                value={goldCOT.speculator_net}
                total={Math.max(Math.abs(goldCOT.speculator_net), 100)}
              />
            )}
            {eurCOT && (
              <COTBar
                label="EUR — Large Specs"
                value={eurCOT.speculator_net}
                total={Math.max(Math.abs(eurCOT.speculator_net), 100)}
              />
            )}
            {cot?.summary && (
              <div className="flex items-center justify-between pt-1">
                <span className="text-xs text-[#6b7280]">Market Bias</span>
                <span className={`text-xs font-bold uppercase px-2 py-0.5 rounded ${
                  cot.summary.market_bias === 'bullish'
                    ? 'bg-[#00c853]/10 text-[#00c853]'
                    : 'bg-[#ff1744]/10 text-[#ff1744]'
                }`}>
                  {cot.summary.market_bias}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
