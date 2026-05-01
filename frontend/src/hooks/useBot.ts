import { useState, useCallback } from 'react'
import { tradingApi } from '../api/client'
import type { BotStatus, RiskParams } from '../types'

const DEFAULT_STATUS: BotStatus = {
  running: false,
  mode: 'scalp',
  fundamental_enabled: true,
  started_at: null,
  stopped_at: null,
  risk_params: {
    risk_pct: 1.0,
    max_positions: 5,
    daily_loss_limit: 3.0,
    mode: 'scalp',
  },
  trades_today: 0,
  daily_pnl: 0,
  status_message: 'Idle',
}

export function useBot() {
  const [status, setStatus] = useState<BotStatus>(DEFAULT_STATUS)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refreshStatus = useCallback(async () => {
    try {
      const res = await tradingApi.getStatus()
      setStatus(res.data)
    } catch (err) {
      // Silently fail on status refresh
    }
  }, [])

  const startBot = useCallback(async (mode: 'scalp' | 'swing') => {
    setLoading(true)
    setError(null)
    try {
      const res = await tradingApi.startBot(mode)
      setStatus((prev) => ({
        ...prev,
        running: true,
        mode,
        status_message: `Running (${mode.toUpperCase()})`,
        started_at: new Date().toISOString(),
      }))
      return res.data
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to start bot'
      setError(msg)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const stopBot = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await tradingApi.stopBot()
      setStatus((prev) => ({
        ...prev,
        running: false,
        status_message: 'Stopped',
        stopped_at: new Date().toISOString(),
      }))
      return res.data
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Failed to stop bot'
      setError(msg)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const updateFromWS = useCallback((wsStatus: BotStatus) => {
    setStatus(wsStatus)
  }, [])

  return {
    status,
    loading,
    error,
    startBot,
    stopBot,
    refreshStatus,
    updateFromWS,
  }
}
