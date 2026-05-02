import { useState } from 'react'
import { List, X } from 'lucide-react'
import type { Position } from '../types'
import { tradingApi } from '../api/client'

interface Props {
  positions: Position[]
}

export default function PositionsTable({ positions }: Props) {
  const [closing, setClosing] = useState<number | null>(null)

  const handleClose = async (ticket: number) => {
    setClosing(ticket)
    try {
      await tradingApi.closePosition(ticket)
    } catch {
      // Handle error
    } finally {
      setClosing(null)
    }
  }

  return (
    <div className="terminal-card">
      <div className="terminal-card-header">
        <div className="flex items-center gap-2">
          <List className="w-4 h-4 text-[#2979ff]" />
          <span className="text-xs font-semibold text-[#e0e0e0] uppercase tracking-wider">
            Open Positions
          </span>
          <span className="text-xs px-1.5 py-0.5 rounded bg-[#2979ff]/10 text-[#2979ff] border border-[#2979ff]/20 font-mono">
            {positions.length}
          </span>
        </div>
      </div>

      <div className="overflow-x-auto">
        {positions.length === 0 ? (
          <div className="flex items-center justify-center py-8 text-[#6b7280] text-sm">
            No open positions
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Ticket</th>
                <th>Symbol</th>
                <th>Side</th>
                <th>Volume</th>
                <th>Entry</th>
                <th>Current</th>
                <th>SL</th>
                <th>TP</th>
                <th>P&L</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {positions.map((pos) => {
                const pnlColor = pos.pnl >= 0 ? 'text-[#00c853]' : 'text-[#ff1744]'
                const sideColor = pos.direction === 'buy' ? 'text-[#00c853]' : 'text-[#ff1744]'
                return (
                  <tr key={pos.ticket}>
                    <td className="font-mono text-[#6b7280]">#{pos.ticket}</td>
                    <td className="font-semibold text-[#e0e0e0]">{pos.symbol}</td>
                    <td>
                      <span className={`font-bold uppercase ${sideColor}`}>
                        {pos.direction}
                      </span>
                    </td>
                    <td className="font-mono">{pos.volume.toFixed(2)}</td>
                    <td className="font-mono">{pos.entry_price?.toFixed(5)}</td>
                    <td className="font-mono">{pos.current_price?.toFixed(5)}</td>
                    <td className="font-mono text-[#ff1744]">{pos.sl?.toFixed(5) ?? '—'}</td>
                    <td className="font-mono text-[#00c853]">{pos.tp?.toFixed(5) ?? '—'}</td>
                    <td className={`font-mono font-semibold ${pnlColor}`}>
                      {pos.pnl >= 0 ? '+' : ''}{pos.pnl.toFixed(2)}
                    </td>
                    <td>
                      <button
                        onClick={() => handleClose(pos.ticket)}
                        disabled={closing === pos.ticket}
                        className="p-1 rounded hover:bg-[#ff1744]/10 text-[#6b7280] hover:text-[#ff1744] transition-colors disabled:opacity-50"
                        title="Close position"
                      >
                        <X className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
