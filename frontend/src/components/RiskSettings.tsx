import { useState } from 'react'
import { X, Shield, Save } from 'lucide-react'
import type { RiskParams } from '../types'

interface Props {
  params: RiskParams
  onClose: () => void
  onSave: (params: RiskParams) => Promise<void>
}

export default function RiskSettings({ params, onClose, onSave }: Props) {
  const [form, setForm] = useState<RiskParams>({ ...params })
  const [saving, setSaving] = useState(false)

  const handleSave = async () => {
    setSaving(true)
    try {
      await onSave(form)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
      <div className="bg-[#111111] border border-[#1e1e1e] rounded-lg w-full max-w-md shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-[#1e1e1e]">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-[#ffab00]" />
            <span className="text-sm font-semibold text-[#e0e0e0]">Risk Parameters</span>
          </div>
          <button onClick={onClose} className="p-1 rounded hover:bg-[#1e1e1e] text-[#6b7280] hover:text-[#e0e0e0]">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="p-5 space-y-5">
          {/* Risk % */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs text-[#6b7280] uppercase tracking-wider">Risk Per Trade</label>
              <span className="text-sm font-mono font-bold text-[#ffab00]">{form.risk_pct.toFixed(1)}%</span>
            </div>
            <input
              type="range"
              min={0.1}
              max={10}
              step={0.1}
              value={form.risk_pct}
              onChange={(e) => setForm((f) => ({ ...f, risk_pct: parseFloat(e.target.value) }))}
              className="w-full accent-[#ffab00]"
            />
            <div className="flex justify-between text-xs text-[#6b7280] mt-1">
              <span>Conservative (0.1%)</span>
              <span>Aggressive (10%)</span>
            </div>
          </div>

          {/* Max positions */}
          <div>
            <label className="text-xs text-[#6b7280] uppercase tracking-wider block mb-2">
              Max Open Positions
            </label>
            <input
              type="number"
              min={1}
              max={20}
              value={form.max_positions}
              onChange={(e) => setForm((f) => ({ ...f, max_positions: parseInt(e.target.value) || 1 }))}
              className="w-full bg-[#0d0d0d] border border-[#2a2a2a] rounded px-3 py-2 text-[#e0e0e0] font-mono text-sm focus:outline-none focus:border-[#2979ff]"
            />
          </div>

          {/* Daily loss limit */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs text-[#6b7280] uppercase tracking-wider">Daily Loss Limit</label>
              <span className="text-sm font-mono font-bold text-[#ff1744]">{form.daily_loss_limit.toFixed(1)}%</span>
            </div>
            <input
              type="range"
              min={0.5}
              max={20}
              step={0.5}
              value={form.daily_loss_limit}
              onChange={(e) => setForm((f) => ({ ...f, daily_loss_limit: parseFloat(e.target.value) }))}
              className="w-full accent-[#ff1744]"
            />
            <div className="flex justify-between text-xs text-[#6b7280] mt-1">
              <span>0.5%</span>
              <span>20%</span>
            </div>
          </div>

          {/* Mode */}
          <div>
            <label className="text-xs text-[#6b7280] uppercase tracking-wider block mb-2">Trading Mode</label>
            <div className="grid grid-cols-2 gap-2">
              {(['scalp', 'swing'] as const).map((m) => (
                <button
                  key={m}
                  onClick={() => setForm((f) => ({ ...f, mode: m }))}
                  className={`py-2 rounded text-xs font-bold uppercase transition-all ${
                    form.mode === m
                      ? 'bg-[#2979ff]/20 border border-[#2979ff]/50 text-[#2979ff]'
                      : 'bg-[#1a1a1a] border border-[#2a2a2a] text-[#6b7280] hover:text-[#e0e0e0]'
                  }`}
                >
                  {m}
                </button>
              ))}
            </div>
          </div>

          {/* Warning */}
          {form.risk_pct > 5 && (
            <div className="bg-[#ff1744]/10 border border-[#ff1744]/20 rounded px-3 py-2">
              <p className="text-xs text-[#ff1744]">
                ⚠ High risk setting ({form.risk_pct}%). Ensure you understand the risks.
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex gap-2 px-5 py-4 border-t border-[#1e1e1e]">
          <button
            onClick={onClose}
            className="flex-1 py-2 rounded text-xs font-semibold text-[#6b7280] border border-[#2a2a2a] hover:border-[#3a3a3a] hover:text-[#e0e0e0] transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex-1 py-2 rounded text-xs font-semibold text-black bg-[#00c853] hover:bg-[#00e676] transition-colors disabled:opacity-50 flex items-center justify-center gap-1.5"
          >
            <Save className="w-3.5 h-3.5" />
            {saving ? 'Saving…' : 'Save Parameters'}
          </button>
        </div>
      </div>
    </div>
  )
}
