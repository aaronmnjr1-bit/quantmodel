import { useEffect, useState, useCallback } from 'react'
import { Activity, RefreshCw, Wifi, WifiOff } from 'lucide-react'
import { useWebSocket } from '../hooks/useWebSocket'
import { useBot } from '../hooks/useBot'
import { dashboardApi, analysisApi } from '../api/client'
import type { DashboardData, VIXData, Position, NewsEvent } from '../types'
import BotControl from './BotControl'
import AccountMetrics from './AccountMetrics'
import PositionsTable from './PositionsTable'
import FundamentalPanel from './FundamentalPanel'
import SectorRotation from './SectorRotation'
import QuantPanel from './QuantPanel'
import RiskSettings from './RiskSettings'
import NewsPanel from './NewsPanel'

export default function Dashboard() {
  const { connected, lastMessage } = useWebSocket()
  const bot = useBot()
  const [dashData, setDashData] = useState<DashboardData | null>(null)
  const [showRisk, setShowRisk] = useState(false)
  const [refreshing, setRefreshing] = useState(false)

  const fetchDashboard = useCallback(async () => {
    try {
      const res = await dashboardApi.getSummary()
      setDashData(res.data)
    } catch {
      // Use mock/fallback data
    }
  }, [])

  useEffect(() => {
    fetchDashboard()
    const interval = setInterval(fetchDashboard, 10000)
    return () => clearInterval(interval)
  }, [fetchDashboard])

  // Apply WebSocket updates
  useEffect(() => {
    if (!lastMessage) return
    if (lastMessage.type === 'state_update') {
      bot.updateFromWS(lastMessage.bot)
      setDashData((prev) =>
        prev
          ? { ...prev, bot: lastMessage.bot, analysis: { ...prev.analysis, vix: lastMessage.vix } }
          : null,
      )
    }
  }, [lastMessage])

  const handleRefresh = async () => {
    setRefreshing(true)
    await fetchDashboard()
    setRefreshing(false)
  }

  const now = new Date()
  const timeStr = now.toLocaleTimeString('en-US', { hour12: false })
  const dateStr = now.toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' })

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-[#e0e0e0] p-3 font-sans">
      {/* Header */}
      <header className="flex items-center justify-between mb-3 px-1">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-[#00c853]" />
            <span className="text-lg font-bold tracking-wide text-white">QUANT<span className="text-[#00c853]">MODEL</span></span>
          </div>
          <span className="text-xs text-[#6b7280] font-mono border border-[#1e1e1e] px-2 py-0.5 rounded">
            ALGO TRADING v1.0
          </span>
        </div>

        <div className="flex items-center gap-4">
          <span className="text-xs font-mono text-[#6b7280]">{dateStr} {timeStr}</span>

          <button
            onClick={handleRefresh}
            className="p-1.5 rounded border border-[#1e1e1e] hover:border-[#2a2a2a] text-[#6b7280] hover:text-[#e0e0e0] transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />
          </button>

          <div className="flex items-center gap-1.5">
            {connected ? (
              <>
                <Wifi className="w-3.5 h-3.5 text-[#00c853]" />
                <span className="text-xs text-[#00c853] font-mono">LIVE</span>
                <span className="w-1.5 h-1.5 rounded-full bg-[#00c853] blink" />
              </>
            ) : (
              <>
                <WifiOff className="w-3.5 h-3.5 text-[#ff1744]" />
                <span className="text-xs text-[#ff1744] font-mono">DISCONNECTED</span>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Main grid */}
      <div className="grid grid-cols-12 gap-3">
        {/* Row 1: Bot Control | Account | Account | Account */}
        <div className="col-span-3">
          <BotControl
            status={bot.status}
            loading={bot.loading}
            onStart={bot.startBot}
            onStop={bot.stopBot}
            onRiskSettings={() => setShowRisk(true)}
          />
        </div>
        <div className="col-span-9">
          <AccountMetrics account={dashData?.account ?? null} botStatus={bot.status} />
        </div>

        {/* Row 2: Positions table full width */}
        <div className="col-span-12">
          <PositionsTable positions={dashData?.positions ?? []} />
        </div>

        {/* Row 3: Fundamental | Quant | News */}
        <div className="col-span-4">
          <FundamentalPanel
            vix={dashData?.analysis?.vix ?? null}
            fedwatch={dashData?.analysis?.fedwatch ?? null}
            cot={dashData?.analysis?.cot ?? null}
          />
        </div>
        <div className="col-span-4">
          <QuantPanel positions={dashData?.positions ?? []} botStatus={bot.status} />
        </div>
        <div className="col-span-4">
          <NewsPanel events={dashData?.news ?? []} />
        </div>

        {/* Row 4: Sector Rotation */}
        <div className="col-span-12">
          <SectorRotation sector={dashData?.analysis?.sector ?? null} />
        </div>
      </div>

      {/* Risk settings modal */}
      {showRisk && (
        <RiskSettings
          params={bot.status.risk_params}
          onClose={() => setShowRisk(false)}
          onSave={async (params) => {
            const { riskApi } = await import('../api/client')
            await riskApi.updateParams(params)
            setShowRisk(false)
            await fetchDashboard()
          }}
        />
      )}
    </div>
  )
}
