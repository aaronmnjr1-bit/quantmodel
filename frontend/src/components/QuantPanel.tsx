import { Cpu, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import type { Position, BotStatus } from '../types'

interface Props {
  positions: Position[]
  botStatus: BotStatus
}

const ASSETS = ['XAUUSD', 'NAS100', 'US30', 'GER40', 'JP225', 'USDCAD']

const ASSET_LABELS: Record<string, string> = {
  XAUUSD: 'Gold',
  NAS100: 'Nasdaq',
  US30: 'Dow Jones',
  GER40: 'DAX',
  JP225: 'Nikkei',
  USDCAD: 'USD/CAD',
}

function SignalBar({
  label,
  sublabel,
  signal,
  strength,
  active,
}: {
  label: string
  sublabel: string
  signal: 'bullish' | 'bearish' | 'neutral'
  strength: number
  active?: boolean
}) {
  const color =
    signal === 'bullish' ? '#00c853'
    : signal === 'bearish' ? '#ff1744'
    : '#ffab00'

  const Icon =
    signal === 'bullish' ? TrendingUp
    : signal === 'bearish' ? TrendingDown
    : Minus

  return (
    <div className={`flex items-center gap-3 py-1.5 px-2 rounded ${active ? 'bg-[#161616]' : ''}`}>
      <div className="w-16 flex-shrink-0">
        <p className="text-xs font-semibold text-[#e0e0e0]">{label}</p>
        <p className="text-xs text-[#6b7280]">{sublabel}</p>
      </div>

      <div className="flex-1 h-2 bg-[#1a1a1a] rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${strength}%`, background: color }}
        />
      </div>

      <div className="flex items-center gap-1 w-20 flex-shrink-0 justify-end">
        <Icon className="w-3 h-3" style={{ color }} />
        <span className="text-xs font-mono font-semibold" style={{ color }}>
          {signal.toUpperCase()}
        </span>
        <span className="text-xs text-[#6b7280] font-mono">{strength.toFixed(0)}</span>
      </div>
    </div>
  )
}

function HawkDoveMeter({ score }: { score: number }) {
  // score: -100 (dovish) to +100 (hawkish)
  const normalized = (score + 100) / 200 * 100 // 0-100%
  const color = score > 20 ? '#ff1744' : score < -20 ? '#00c853' : '#ffab00'
  const label = score > 30 ? 'HAWKISH' : score < -30 ? 'DOVISH' : 'NEUTRAL'

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-[#00c853]">DOVISH</span>
        <span className="text-xs font-bold" style={{ color }}>{label}</span>
        <span className="text-xs font-semibold text-[#ff1744]">HAWKISH</span>
      </div>
      <div className="w-full h-3 bg-[#1a1a1a] rounded-full overflow-hidden relative">
        {/* Center line */}
        <div className="absolute left-1/2 top-0 w-px h-full bg-[#2a2a2a]" />
        <div
          className="absolute top-1 h-1 rounded-full transition-all duration-700"
          style={{
            width: '8px',
            left: `calc(${normalized}% - 4px)`,
            background: color,
            boxShadow: `0 0 6px ${color}`,
          }}
        />
      </div>
      <div className="text-center">
        <span className="text-xs font-mono text-[#6b7280]">
          Score: <span style={{ color }}>{score > 0 ? '+' : ''}{score}</span>
        </span>
      </div>
    </div>
  )
}

export default function QuantPanel({ positions, botStatus }: Props) {
  // Generate signals from position data or use mock
  const signalMap: Record<string, { signal: 'bullish' | 'bearish' | 'neutral'; strength: number }> = {}

  for (const asset of ASSETS) {
    const pos = positions.find((p) => p.symbol === asset)
    if (pos) {
      const dir = pos.direction === 'buy' ? 'bullish' : 'bearish'
      const strength = Math.min(40 + Math.abs(pos.pnl / 10), 95)
      signalMap[asset] = { signal: dir, strength }
    } else {
      // Mock signal
      const r = Math.random()
      signalMap[asset] = {
        signal: r > 0.55 ? 'bullish' : r < 0.35 ? 'bearish' : 'neutral',
        strength: 30 + Math.random() * 60,
      }
    }
  }

  // Aggregate hawkish/dovish score (mock based on signals)
  const bullCount = Object.values(signalMap).filter((s) => s.signal === 'bullish').length
  const bearCount = Object.values(signalMap).filter((s) => s.signal === 'bearish').length
  const hawkishScore = Math.round((bullCount - bearCount) / ASSETS.length * 60)

  // Overall bias
  const bullish = Object.values(signalMap).filter((s) => s.signal === 'bullish').length
  const bearish = Object.values(signalMap).filter((s) => s.signal === 'bearish').length
  const overallBias = bullish > bearish ? 'BULLISH' : bearish > bullish ? 'BEARISH' : 'NEUTRAL'
  const biasColor = overallBias === 'BULLISH' ? 'text-[#00c853]' : overallBias === 'BEARISH' ? 'text-[#ff1744]' : 'text-[#ffab00]'

  return (
    <div className="terminal-card h-full">
      <div className="terminal-card-header">
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-[#2979ff]" />
          <span className="text-xs font-semibold text-[#e0e0e0] uppercase tracking-wider">
            Quant Signals
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-[#6b7280]">Bias:</span>
          <span className={`text-xs font-bold ${biasColor}`}>{overallBias}</span>
        </div>
      </div>

      <div className="p-4 space-y-1">
        {ASSETS.map((asset) => {
          const { signal, strength } = signalMap[asset]
          const isActive = positions.some((p) => p.symbol === asset)
          return (
            <SignalBar
              key={asset}
              label={asset}
              sublabel={ASSET_LABELS[asset]}
              signal={signal}
              strength={strength}
              active={isActive}
            />
          )
        })}

        <div className="border-t border-[#1e1e1e] pt-3 mt-3">
          <p className="text-xs text-[#6b7280] uppercase tracking-wider mb-2">Fed Sentiment Meter</p>
          <HawkDoveMeter score={hawkishScore} />
        </div>
      </div>
    </div>
  )
}
