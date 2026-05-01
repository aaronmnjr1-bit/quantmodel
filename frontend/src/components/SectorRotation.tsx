import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { RefreshCw, ArrowUpRight, ArrowDownRight } from 'lucide-react'
import type { SectorData } from '../types'

interface Props {
  sector: SectorData | null
}

const PHASE_COLORS: Record<string, string> = {
  expansion: '#00c853',
  peak: '#ffab00',
  contraction: '#ff1744',
  trough: '#2979ff',
}

const PHASE_DESCRIPTIONS: Record<string, string> = {
  expansion: 'Cyclicals outperforming — Risk assets favored',
  peak: 'Momentum fading — Begin rotating to defensives',
  contraction: 'Defensives outperforming — Risk-off',
  trough: 'Early recovery signals — Watch financials',
}

const MOCK_SECTOR: SectorData = {
  sectors: {
    XLB: { ticker: 'XLB', name: 'Materials', category: 'cyclical', return_30d: 3.2, momentum: 'positive' },
    XLE: { ticker: 'XLE', name: 'Energy', category: 'cyclical', return_30d: 7.8, momentum: 'positive' },
    XLF: { ticker: 'XLF', name: 'Financials', category: 'cyclical', return_30d: 2.1, momentum: 'positive' },
    XLI: { ticker: 'XLI', name: 'Industrials', category: 'cyclical', return_30d: 4.5, momentum: 'positive' },
    XLK: { ticker: 'XLK', name: 'Technology', category: 'cyclical', return_30d: 8.3, momentum: 'positive' },
    XLP: { ticker: 'XLP', name: 'Cons. Staples', category: 'defensive', return_30d: 0.8, momentum: 'positive' },
    XLRE: { ticker: 'XLRE', name: 'Real Estate', category: 'defensive', return_30d: -2.1, momentum: 'negative' },
    XLU: { ticker: 'XLU', name: 'Utilities', category: 'defensive', return_30d: -1.5, momentum: 'negative' },
    XLV: { ticker: 'XLV', name: 'Healthcare', category: 'defensive', return_30d: 1.2, momentum: 'positive' },
  },
  rotation: { cyclical_avg_return: 5.2, defensive_avg_return: -0.4, ratio: 5.6, signal: 'risk_on', bias: 'bullish' },
  market_phase: 'expansion',
  top_performers: ['XLK', 'XLE', 'XLI'],
  bottom_performers: ['XLRE', 'XLU', 'XLP'],
  recommendation: 'Favor cyclicals: XLF, XLI, XLK. Risk assets preferred.',
}

export default function SectorRotation({ sector }: Props) {
  const data = sector ?? MOCK_SECTOR
  const phase = data.market_phase
  const phaseColor = PHASE_COLORS[phase] ?? '#6b7280'

  const chartData = Object.values(data.sectors).map((s) => ({
    name: s.ticker,
    value: s.return_30d,
    category: s.category,
  }))

  return (
    <div className="terminal-card">
      <div className="terminal-card-header">
        <div className="flex items-center gap-2">
          <RefreshCw className="w-4 h-4 text-[#ffab00]" />
          <span className="text-xs font-semibold text-[#e0e0e0] uppercase tracking-wider">
            Sector Rotation
          </span>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5">
            <span className="text-xs text-[#6b7280]">Phase:</span>
            <span
              className="text-xs font-bold uppercase px-2 py-0.5 rounded"
              style={{ background: `${phaseColor}20`, color: phaseColor, border: `1px solid ${phaseColor}40` }}
            >
              {phase}
            </span>
          </div>
          <div className="flex items-center gap-1">
            {data.rotation.signal === 'risk_on' ? (
              <ArrowUpRight className="w-3.5 h-3.5 text-[#00c853]" />
            ) : (
              <ArrowDownRight className="w-3.5 h-3.5 text-[#ff1744]" />
            )}
            <span className={`text-xs font-mono font-semibold ${
              data.rotation.signal === 'risk_on' ? 'text-[#00c853]' : 'text-[#ff1744]'
            }`}>
              {data.rotation.signal.replace('_', ' ').toUpperCase()}
            </span>
          </div>
        </div>
      </div>

      <div className="p-4">
        <div className="grid grid-cols-12 gap-4">
          {/* Bar chart */}
          <div className="col-span-8 h-32">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 0, right: 0, bottom: 0, left: -20 }}>
                <XAxis
                  dataKey="name"
                  tick={{ fill: '#6b7280', fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  tick={{ fill: '#6b7280', fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(v) => `${v}%`}
                />
                <Tooltip
                  contentStyle={{ background: '#111111', border: '1px solid #1e1e1e', borderRadius: 4 }}
                  itemStyle={{ color: '#e0e0e0', fontSize: 11 }}
                  formatter={(v: number) => [`${v.toFixed(2)}%`, '30d Return']}
                />
                <Bar dataKey="value" radius={[2, 2, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell
                      key={index}
                      fill={entry.value >= 0 ? '#00c853' : '#ff1744'}
                      opacity={entry.category === 'cyclical' ? 1.0 : 0.6}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Stats */}
          <div className="col-span-4 space-y-2">
            <div className="bg-[#0d0d0d] rounded p-2 border border-[#1a1a1a]">
              <p className="text-xs text-[#6b7280]">Cyclical Avg</p>
              <p className={`text-sm font-mono font-bold ${data.rotation.cyclical_avg_return >= 0 ? 'text-[#00c853]' : 'text-[#ff1744]'}`}>
                {data.rotation.cyclical_avg_return >= 0 ? '+' : ''}{data.rotation.cyclical_avg_return.toFixed(2)}%
              </p>
            </div>
            <div className="bg-[#0d0d0d] rounded p-2 border border-[#1a1a1a]">
              <p className="text-xs text-[#6b7280]">Defensive Avg</p>
              <p className={`text-sm font-mono font-bold ${data.rotation.defensive_avg_return >= 0 ? 'text-[#00c853]' : 'text-[#ff1744]'}`}>
                {data.rotation.defensive_avg_return >= 0 ? '+' : ''}{data.rotation.defensive_avg_return.toFixed(2)}%
              </p>
            </div>
            <div className="bg-[#0d0d0d] rounded p-2 border border-[#1a1a1a]">
              <p className="text-xs text-[#6b7280]">C/D Spread</p>
              <p className={`text-sm font-mono font-bold ${data.rotation.ratio >= 0 ? 'text-[#00c853]' : 'text-[#ff1744]'}`}>
                {data.rotation.ratio >= 0 ? '+' : ''}{data.rotation.ratio.toFixed(2)}%
              </p>
            </div>
          </div>
        </div>

        <p className="text-xs text-[#6b7280] mt-2 italic">{data.recommendation}</p>
      </div>
    </div>
  )
}
