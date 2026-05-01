import { DollarSign, TrendingDown, BarChart2, CreditCard } from 'lucide-react'
import type { AccountInfo, BotStatus } from '../types'

interface Props {
  account: AccountInfo | null
  botStatus: BotStatus
}

function Metric({
  label,
  value,
  sub,
  color,
  icon: Icon,
}: {
  label: string
  value: string
  sub?: string
  color?: string
  icon: React.ElementType
}) {
  return (
    <div className="bg-[#0d0d0d] rounded border border-[#1a1a1a] p-3 flex items-start gap-3">
      <div className="p-1.5 rounded bg-[#1a1a1a]">
        <Icon className="w-4 h-4 text-[#6b7280]" />
      </div>
      <div className="min-w-0">
        <p className="text-xs text-[#6b7280] uppercase tracking-wider mb-0.5">{label}</p>
        <p className={`text-xl font-mono font-bold ${color ?? 'text-[#e0e0e0]'}`}>{value}</p>
        {sub && <p className="text-xs text-[#6b7280] font-mono mt-0.5">{sub}</p>}
      </div>
    </div>
  )
}

export default function AccountMetrics({ account, botStatus }: Props) {
  const acc = account ?? {
    balance: 10000,
    equity: 10000,
    margin: 0,
    free_margin: 10000,
    profit: 0,
    leverage: 100,
    currency: 'USD',
    server: '—',
    simulate: true,
  }

  const drawdown = acc.balance > 0
    ? ((acc.balance - acc.equity) / acc.balance * 100)
    : 0
  const marginUsedPct = acc.equity > 0 ? (acc.margin / acc.equity * 100) : 0

  const profitColor =
    acc.profit > 0 ? 'text-[#00c853]' : acc.profit < 0 ? 'text-[#ff1744]' : 'text-[#e0e0e0]'

  return (
    <div className="terminal-card h-full">
      <div className="terminal-card-header">
        <div className="flex items-center gap-2">
          <DollarSign className="w-4 h-4 text-[#00c853]" />
          <span className="text-xs font-semibold text-[#e0e0e0] uppercase tracking-wider">
            Account Overview
          </span>
          {acc.simulate && (
            <span className="text-xs px-1.5 py-0.5 rounded bg-[#ffab00]/10 text-[#ffab00] border border-[#ffab00]/20">
              SIM
            </span>
          )}
        </div>
        <div className="text-xs text-[#6b7280] font-mono">{acc.server}</div>
      </div>

      <div className="p-3 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
        <Metric
          label="Balance"
          value={`$${acc.balance.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          icon={DollarSign}
        />
        <Metric
          label="Equity"
          value={`$${acc.equity.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
          sub={`Leverage 1:${acc.leverage}`}
          icon={BarChart2}
        />
        <Metric
          label="Open P&L"
          value={`${acc.profit >= 0 ? '+' : ''}$${acc.profit.toFixed(2)}`}
          sub={`${acc.profit >= 0 ? '▲' : '▼'} ${Math.abs(acc.profit / Math.max(acc.balance, 1) * 100).toFixed(2)}%`}
          color={profitColor}
          icon={TrendingDown}
        />
        <Metric
          label="Free Margin"
          value={`$${acc.free_margin.toFixed(2)}`}
          icon={CreditCard}
        />
        <Metric
          label="Drawdown"
          value={`${drawdown.toFixed(2)}%`}
          color={drawdown > 5 ? 'text-[#ff1744]' : drawdown > 2 ? 'text-[#ffab00]' : 'text-[#00c853]'}
          icon={TrendingDown}
        />
        <Metric
          label="Margin Used"
          value={`${marginUsedPct.toFixed(1)}%`}
          color={marginUsedPct > 50 ? 'text-[#ff1744]' : 'text-[#e0e0e0]'}
          icon={BarChart2}
        />
      </div>
    </div>
  )
}
