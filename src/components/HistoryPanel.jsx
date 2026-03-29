import { Clock, Trash2, ShieldCheck, ShieldX } from 'lucide-react'

const SPAM_LABELS = new Set(['spam', 'fake'])
const isNegative  = (p) => SPAM_LABELS.has(p?.toLowerCase())

function timeAgo(iso) {
  const diffMs = Date.now() - new Date(iso).getTime()
  const s = Math.floor(diffMs / 1000)
  if (s < 60)  return `${s}s ago`
  const m = Math.floor(s / 60)
  if (m < 60)  return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24)  return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}

function HistoryItem({ item, onSelect, darkMode }) {
  const neg = isNegative(item.result.prediction)
  const pct = Math.round(item.result.confidence * 100)
  const preview = item.text.length > 80 ? item.text.slice(0, 80) + '…' : item.text

  return (
    <button
      onClick={() => onSelect(item)}
      className={`
        w-full text-left p-3 rounded-xl border transition-all duration-150 hover:scale-[1.01] active:scale-100
        ${darkMode
          ? 'bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20'
          : 'bg-gray-50 border-gray-200 hover:bg-white hover:border-gray-300 shadow-sm'}
      `}
    >
      <div className="flex items-center gap-2 mb-1.5">
        {neg
          ? <ShieldX size={13} className="text-red-400 shrink-0" />
          : <ShieldCheck size={13} className="text-emerald-400 shrink-0" />}
        <span className={`text-[11px] font-bold uppercase tracking-wider ${neg ? 'text-red-400' : 'text-emerald-400'}`}>
          {item.result.prediction}
        </span>
        <span className={`ml-auto text-[11px] font-mono ${neg ? 'text-red-400' : 'text-emerald-400'}`}>
          {pct}%
        </span>
      </div>

      <p className={`text-xs leading-relaxed line-clamp-2 ${darkMode ? 'text-white/50' : 'text-gray-500'}`}>
        {preview}
      </p>

      <div className={`flex items-center gap-1 mt-1.5 text-[10px] ${darkMode ? 'text-white/20' : 'text-gray-300'}`}>
        <Clock size={9} />
        {timeAgo(item.timestamp)}
      </div>
    </button>
  )
}

export default function HistoryPanel({ history, onSelect, onClear, darkMode }) {
  const spamCount = history.filter(h => isNegative(h.result.prediction)).length
  const hamCount  = history.length - spamCount

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className={`px-4 py-3 border-b flex items-center justify-between shrink-0 ${darkMode ? 'border-white/10' : 'border-gray-200'}`}>
        <div>
          <h3 className={`text-sm font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>
            History
          </h3>
          {history.length > 0 && (
            <p className={`text-[11px] ${darkMode ? 'text-white/30' : 'text-gray-400'}`}>
              {spamCount} spam · {hamCount} legit
            </p>
          )}
        </div>
        {history.length > 0 && (
          <button
            onClick={onClear}
            className={`flex items-center gap-1 text-[11px] px-2 py-1 rounded-lg transition-colors
              ${darkMode ? 'text-white/30 hover:text-red-400 hover:bg-red-400/10' : 'text-gray-400 hover:text-red-500 hover:bg-red-50'}`}
          >
            <Trash2 size={11} />
            Clear
          </button>
        )}
      </div>

      {/* Stats bar */}
      {history.length > 0 && (
        <div className={`px-4 py-2 border-b ${darkMode ? 'border-white/5' : 'border-gray-100'}`}>
          <div className={`h-1.5 rounded-full overflow-hidden ${darkMode ? 'bg-white/10' : 'bg-gray-100'}`}>
            <div
              className="h-full bg-gradient-to-r from-red-500 to-rose-500 rounded-full transition-all duration-500"
              style={{ width: `${(spamCount / history.length) * 100}%` }}
            />
          </div>
          <div className={`flex justify-between text-[10px] mt-1 ${darkMode ? 'text-white/20' : 'text-gray-300'}`}>
            <span className="text-red-400">{Math.round((spamCount / history.length) * 100)}% spam</span>
            <span className="text-emerald-400">{Math.round((hamCount / history.length) * 100)}% legit</span>
          </div>
        </div>
      )}

      {/* List */}
      <div className="flex-1 overflow-y-auto p-3 flex flex-col gap-2">
        {history.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-2 py-8">
            <Clock size={28} className={darkMode ? 'text-white/10' : 'text-gray-200'} />
            <p className={`text-xs text-center ${darkMode ? 'text-white/20' : 'text-gray-300'}`}>
              Your analysis history<br />will appear here
            </p>
          </div>
        ) : (
          history.map((item, i) => (
            <HistoryItem
              key={`${item.timestamp}-${i}`}
              item={item}
              onSelect={onSelect}
              darkMode={darkMode}
            />
          ))
        )}
      </div>
    </div>
  )
}
