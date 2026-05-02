import { Newspaper, Clock } from 'lucide-react'
import type { NewsEvent } from '../types'

interface Props {
  events: NewsEvent[]
}

const IMPACT_STYLES: Record<string, string> = {
  high: 'bg-[#ff1744]/10 text-[#ff1744] border-[#ff1744]/20',
  medium: 'bg-[#ffab00]/10 text-[#ffab00] border-[#ffab00]/20',
  low: 'bg-[#6b7280]/10 text-[#6b7280] border-[#6b7280]/20',
}

const MOCK_EVENTS: NewsEvent[] = [
  { id: '1', time: '08:30', currency: 'USD', event: 'Non-Farm Payrolls', impact: 'high', forecast: '185K', previous: '175K', actual: '210K', deviation: 25, sentiment_score: 35, upcoming: false },
  { id: '2', time: '10:00', currency: 'USD', event: 'ISM Manufacturing PMI', impact: 'high', forecast: '49.5', previous: '48.7', actual: '50.3', deviation: 0.8, sentiment_score: 15, upcoming: false },
  { id: '3', time: '14:00', currency: 'EUR', event: 'ECB Rate Decision', impact: 'high', forecast: '4.50%', previous: '4.50%', actual: null, deviation: null, sentiment_score: 0, upcoming: true },
  { id: '4', time: '12:30', currency: 'USD', event: 'CPI m/m', impact: 'high', forecast: '0.2%', previous: '0.3%', actual: '0.4%', deviation: 0.2, sentiment_score: 30, upcoming: false },
  { id: '5', time: '09:45', currency: 'USD', event: 'Chicago PMI', impact: 'medium', forecast: '46.0', previous: '44.0', actual: '44.9', deviation: -1.1, sentiment_score: -12, upcoming: false },
  { id: '6', time: '15:30', currency: 'GBP', event: 'BOE Governor Speaks', impact: 'high', forecast: null, previous: null, actual: null, deviation: null, sentiment_score: 0, upcoming: true },
  { id: '7', time: '13:30', currency: 'USD', event: 'Initial Jobless Claims', impact: 'medium', forecast: '218K', previous: '215K', actual: '207K', deviation: -11, sentiment_score: 20, upcoming: false },
]

function DeviationBadge({ deviation, impact }: { deviation: number | null; impact: string }) {
  if (deviation === null) return <span className="text-xs text-[#6b7280]">—</span>
  const color = deviation > 0 ? 'text-[#00c853]' : deviation < 0 ? 'text-[#ff1744]' : 'text-[#6b7280]'
  return (
    <span className={`text-xs font-mono font-semibold ${color}`}>
      {deviation > 0 ? '+' : ''}{typeof deviation === 'number' ? deviation.toFixed(1) : deviation}
    </span>
  )
}

export default function NewsPanel({ events }: Props) {
  const displayEvents = events.length > 0 ? events : MOCK_EVENTS
  const upcoming = displayEvents.filter((e) => e.upcoming)
  const nextEvent = upcoming[0]

  return (
    <div className="terminal-card h-full flex flex-col">
      <div className="terminal-card-header">
        <div className="flex items-center gap-2">
          <Newspaper className="w-4 h-4 text-[#00e5ff]" />
          <span className="text-xs font-semibold text-[#e0e0e0] uppercase tracking-wider">
            Economic Calendar
          </span>
        </div>
        {nextEvent && (
          <div className="flex items-center gap-1 text-xs text-[#ffab00]">
            <Clock className="w-3 h-3" />
            <span className="font-mono">Next: {nextEvent.time}</span>
          </div>
        )}
      </div>

      <div className="flex-1 overflow-y-auto max-h-80">
        {displayEvents.map((event) => (
          <div
            key={event.id}
            className={`px-3 py-2 border-b border-[#1a1a1a] hover:bg-[#161616] transition-colors ${
              event.upcoming ? 'opacity-60' : ''
            }`}
          >
            <div className="flex items-start justify-between gap-2 mb-1">
              <div className="flex items-center gap-1.5 min-w-0">
                <span className="text-xs font-mono text-[#6b7280] flex-shrink-0">{event.time}</span>
                <span className="text-xs font-bold text-[#00e5ff] flex-shrink-0 w-8">{event.currency}</span>
                <span className="text-xs text-[#e0e0e0] truncate">{event.event}</span>
              </div>
              <div className="flex items-center gap-1 flex-shrink-0">
                {event.upcoming && (
                  <span className="text-xs px-1 py-0.5 rounded bg-[#2979ff]/10 text-[#2979ff] border border-[#2979ff]/20">
                    upcoming
                  </span>
                )}
                <span className={`text-xs px-1 py-0.5 rounded border ${IMPACT_STYLES[event.impact]}`}>
                  {event.impact}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-3 text-xs font-mono">
              {event.forecast && (
                <span className="text-[#6b7280]">F: {event.forecast}</span>
              )}
              {event.actual && (
                <span className="text-[#e0e0e0] font-semibold">A: {event.actual}</span>
              )}
              {event.previous && (
                <span className="text-[#6b7280]">P: {event.previous}</span>
              )}
              <DeviationBadge deviation={event.deviation} impact={event.impact} />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
