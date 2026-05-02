import { useState } from 'react'
import { Play, Square, Settings, Zap, TrendingUp, Brain } from 'lucide-react'
import type { BotStatus } from '../types'

interface Props {
  status: BotStatus
  loading: boolean
  onStart: (mode: 'scalp' | 'swing') => void
  onStop: () => void
  onRiskSettings: () => void
}

export default function BotControl({ status, loading, onStart, onStop, onRiskSettings }: Props) {
  const [selectedMode, setSelectedMode] = useState<'scalp' | 'swing'>('scalp')

  const statusColor = status.running ? 'text-[#00c853]' : 'text-[#6b7280]'
  const statusBg = status.running ? 'bg-[#00c853]/10 border-[#00c853]/30' : 'bg-[#111111] border-[#1e1e1e]'

  return (
    <div className="terminal-card h-full">
      <div className="terminal-card-header">
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-[#ffab00]" />
          <span className="text-xs font-semibold text-[#e0e0e0] uppercase tracking-wider">Bot Control</span>
        </div>
        <button
          onClick={onRiskSettings}
          className="p-1 rounded hover:bg-[#1e1e1e] text-[#6b7280] hover:text-[#e0e0e0] transition-colors"
        >
          <Settings className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="p-4 space-y-4">
        {/* Status indicator */}
        <div className={`flex items-center gap-2 px-3 py-2 rounded border ${statusBg}`}>
          <span className={`w-2 h-2 rounded-full ${status.running ? 'bg-[#00c853] blink' : 'bg-[#6b7280]'}`} />
          <span className={`text-xs font-mono font-semibold ${statusColor}`}>
            {status.status_message.toUpperCase()}
          </span>
        </div>

        {/* Mode selector */}
        <div>
          <p className="text-xs text-[#6b7280] mb-2 uppercase tracking-wider">Trading Mode</p>
          <div className="grid grid-cols-2 gap-1.5">
            <button
              onClick={() => setSelectedMode('scalp')}
              disabled={status.running}
              className={`flex items-center justify-center gap-1.5 py-2 rounded text-xs font-semibold transition-all ${
                selectedMode === 'scalp'
                  ? 'bg-[#2979ff]/20 border border-[#2979ff]/50 text-[#2979ff]'
                  : 'bg-[#1a1a1a] border border-[#2a2a2a] text-[#6b7280] hover:text-[#e0e0e0]'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              <Zap className="w-3 h-3" />
              SCALP
            </button>
            <button
              onClick={() => setSelectedMode('swing')}
              disabled={status.running}
              className={`flex items-center justify-center gap-1.5 py-2 rounded text-xs font-semibold transition-all ${
                selectedMode === 'swing'
                  ? 'bg-[#ffab00]/20 border border-[#ffab00]/50 text-[#ffab00]'
                  : 'bg-[#1a1a1a] border border-[#2a2a2a] text-[#6b7280] hover:text-[#e0e0e0]'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              <TrendingUp className="w-3 h-3" />
              SWING
            </button>
          </div>
        </div>

        {/* Fundamental toggle */}
        <div
          className={`flex items-center justify-between px-3 py-2 rounded border cursor-pointer transition-all ${
            status.fundamental_enabled
              ? 'bg-[#00c853]/10 border-[#00c853]/30'
              : 'bg-[#1a1a1a] border-[#2a2a2a]'
          }`}
          onClick={() => {}}
        >
          <div className="flex items-center gap-2">
            <Brain className="w-3.5 h-3.5 text-[#00e5ff]" />
            <span className="text-xs text-[#e0e0e0]">Fundamental Analysis</span>
          </div>
          <div className={`w-8 h-4 rounded-full relative transition-colors ${
            status.fundamental_enabled ? 'bg-[#00c853]' : 'bg-[#2a2a2a]'
          }`}>
            <span className={`absolute top-0.5 w-3 h-3 rounded-full bg-white transition-all ${
              status.fundamental_enabled ? 'left-4' : 'left-0.5'
            }`} />
          </div>
        </div>

        {/* Start / Stop */}
        {!status.running ? (
          <button
            onClick={() => onStart(selectedMode)}
            disabled={loading}
            className="w-full py-3 rounded font-bold text-sm uppercase tracking-wider bg-[#00c853] hover:bg-[#00e676] text-black transition-all pulse-active disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <Play className="w-4 h-4" />
            {loading ? 'Starting…' : `Start ${selectedMode.toUpperCase()}`}
          </button>
        ) : (
          <button
            onClick={onStop}
            disabled={loading}
            className="w-full py-3 rounded font-bold text-sm uppercase tracking-wider bg-[#ff1744] hover:bg-[#ff4569] text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            <Square className="w-4 h-4" />
            {loading ? 'Stopping…' : 'Stop Bot'}
          </button>
        )}

        {/* Stats */}
        <div className="grid grid-cols-2 gap-2 pt-1">
          <div className="bg-[#0d0d0d] rounded p-2 border border-[#1a1a1a]">
            <p className="text-xs text-[#6b7280]">Trades Today</p>
            <p className="text-lg font-mono font-bold text-[#e0e0e0]">{status.trades_today}</p>
          </div>
          <div className="bg-[#0d0d0d] rounded p-2 border border-[#1a1a1a]">
            <p className="text-xs text-[#6b7280]">Daily P&L</p>
            <p className={`text-lg font-mono font-bold ${status.daily_pnl >= 0 ? 'text-[#00c853]' : 'text-[#ff1744]'}`}>
              {status.daily_pnl >= 0 ? '+' : ''}{status.daily_pnl.toFixed(2)}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
