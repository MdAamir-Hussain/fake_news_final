import { useEffect, useState } from 'react'
import { ShieldCheck, ShieldX, AlertTriangle, ChevronDown, ChevronUp, Code2 } from 'lucide-react'
import ConfidenceBar from './ConfidenceBar'

const SPAM_LABELS  = new Set(['spam', 'fake'])
const isNegative = (prediction) => SPAM_LABELS.has(prediction?.toLowerCase())

function VerdictBadge({ prediction }) {
  const negative = isNegative(prediction)
  return (
    <div className={`
      inline-flex items-center gap-2 px-4 py-2 rounded-full font-bold text-lg
      ${negative
        ? 'bg-red-500/15 text-red-400 border border-red-500/25'
        : 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/25'}
    `}>
      {negative
        ? <ShieldX size={22} className="shrink-0" />
        : <ShieldCheck size={22} className="shrink-0" />}
      {prediction}
    </div>
  )
}

export default function ResultCard({ result, text, darkMode }) {
  const [showDetails, setShowDetails] = useState(false)
  const [animKey, setAnimKey] = useState(0)

  useEffect(() => {
    setAnimKey(k => k + 1)
    setShowDetails(false)
  }, [result])

  const negative = isNegative(result.prediction)
  const pct      = Math.round(result.confidence * 100)

  const accent = negative
    ? { glow: 'shadow-red-500/10', ring: 'ring-red-500/20', bar: 'bg-gradient-to-r from-red-500 to-rose-600' }
    : { glow: 'shadow-emerald-500/10', ring: 'ring-emerald-500/20', bar: 'bg-gradient-to-r from-emerald-500 to-teal-500' }

  // Verdict message
  const message = negative
    ? pct >= 90
      ? 'This content is highly likely spam or misinformation.'
      : pct >= 70
        ? 'This content shows strong spam or fake news signals.'
        : 'This content has some suspicious characteristics.'
    : pct >= 90
      ? 'This content appears to be legitimate and trustworthy.'
      : pct >= 70
        ? 'This content shows mostly legitimate characteristics.'
        : 'This content is likely legitimate, with minor uncertainty.'

  return (
    <div
      key={animKey}
      className={`
        rounded-2xl p-6 shadow-2xl animate-slide-up
        ${darkMode
          ? `glass border border-white/10 ${accent.glow}`
          : `bg-white border border-gray-200 shadow-gray-200/60`}
        ${accent.ring} ring-1
      `}
    >
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 mb-5">
        <VerdictBadge prediction={result.prediction} />
        <p className={`text-sm leading-relaxed flex-1 ${darkMode ? 'text-white/60' : 'text-gray-500'}`}>
          {message}
        </p>
      </div>

      {/* Confidence */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className={`text-xs font-semibold uppercase tracking-wider ${darkMode ? 'text-white/40' : 'text-gray-400'}`}>
            Confidence
          </span>
          <span className={`text-2xl font-bold font-mono ${negative ? 'text-red-400' : 'text-emerald-400'}`}>
            {pct}%
          </span>
        </div>
        <ConfidenceBar pct={pct} barClass={accent.bar} darkMode={darkMode} />
      </div>

      {/* Per-class probabilities */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        {Object.entries(result.probabilities).map(([cls, prob]) => {
          const isActive = cls.toLowerCase() === result.prediction.toLowerCase()
          const p = Math.round(prob * 100)
          return (
            <div
              key={cls}
              className={`
                rounded-xl p-3 border transition-all
                ${isActive
                  ? negative
                    ? 'bg-red-500/10 border-red-500/20'
                    : 'bg-emerald-500/10 border-emerald-500/20'
                  : darkMode
                    ? 'bg-white/5 border-white/10'
                    : 'bg-gray-50 border-gray-200'}
              `}
            >
              <div className={`text-xs uppercase tracking-wide font-semibold mb-1 ${darkMode ? 'text-white/40' : 'text-gray-400'}`}>
                {cls}
              </div>
              <div className={`text-xl font-bold font-mono ${
                isActive
                  ? negative ? 'text-red-400' : 'text-emerald-400'
                  : darkMode ? 'text-white/50' : 'text-gray-400'
              }`}>
                {p}%
              </div>
              <div className={`h-1 rounded-full mt-2 overflow-hidden ${darkMode ? 'bg-white/10' : 'bg-gray-200'}`}>
                <div
                  className={`h-full rounded-full bar-fill ${
                    isActive
                      ? negative ? 'bg-red-400' : 'bg-emerald-400'
                      : 'bg-gray-400/40'
                  }`}
                  style={{ width: `${p}%` }}
                />
              </div>
            </div>
          )
        })}
      </div>

      {/* Toggle details */}
      <button
        onClick={() => setShowDetails(v => !v)}
        className={`
          w-full flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-medium
          transition-all duration-200
          ${darkMode
            ? 'text-white/30 hover:text-white/60 hover:bg-white/5'
            : 'text-gray-400 hover:text-gray-600 hover:bg-gray-50'}
        `}
      >
        <Code2 size={12} />
        {showDetails ? 'Hide' : 'Show'} debug details
        {showDetails ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
      </button>

      {/* Debug details */}
      {showDetails && (
        <div className={`
          mt-3 rounded-xl p-4 font-mono text-xs overflow-x-auto
          ${darkMode ? 'bg-black/30 text-white/50' : 'bg-gray-50 text-gray-500'}
        `}>
          <div className="mb-2 font-semibold text-indigo-400">Processed text:</div>
          <p className="mb-3 break-words">{result.processed_text || '—'}</p>
          <div className="mb-2 font-semibold text-indigo-400">Raw response:</div>
          <pre className="whitespace-pre-wrap break-all">
            {JSON.stringify({ ...result, processed_text: undefined }, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}
