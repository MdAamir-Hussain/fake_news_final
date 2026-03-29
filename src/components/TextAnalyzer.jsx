import { useState, useEffect, useRef, useCallback } from 'react'
import { Send, Trash2, ClipboardPaste, AlertCircle } from 'lucide-react'
import ResultCard from './ResultCard'
import LoadingSpinner from './LoadingSpinner'
import { analyzeText } from '../api'

const EXAMPLES = [
  {
    label: '🚨 Spam example',
    text: 'WINNER!! You have been selected as a lucky winner of a £1,000 prize! Call 09061701461 NOW to claim your reward before it expires! T&C apply.',
  },
  {
    label: '✅ Legit message',
    text: "Hey, just a reminder about our meeting tomorrow at 10am in the conference room. Could you bring the Q3 report? Thanks!",
  },
  {
    label: '📰 Fake news',
    text: 'BREAKING: Scientists discover that drinking bleach cures all diseases! Big Pharma is trying to HIDE this miracle cure from the public. Share before they delete this!',
  },
]

const MAX_CHARS = 5000

export default function TextAnalyzer({ onResult, prefill, darkMode }) {
  const [text, setText] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const textareaRef = useRef(null)

  // Pre-fill from history selection
  useEffect(() => {
    if (prefill) {
      setText(prefill.text)
      setResult(prefill.result)
      setError(null)
      textareaRef.current?.focus()
    }
  }, [prefill])

  const handleAnalyze = useCallback(async () => {
    const trimmed = text.trim()
    if (!trimmed) return

    setLoading(true)
    setResult(null)
    setError(null)

    try {
      const data = await analyzeText(trimmed)
      setResult(data)
      onResult?.({
        text: trimmed,
        result: data,
        timestamp: new Date().toISOString(),
      })
    } catch (err) {
      const msg = err?.response?.data?.detail
        || err?.message
        || 'Failed to connect to the API. Is the backend running?'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }, [text, onResult])

  const handleKeyDown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault()
      handleAnalyze()
    }
  }

  const handlePaste = async () => {
    try {
      const t = await navigator.clipboard.readText()
      setText(t.slice(0, MAX_CHARS))
      textareaRef.current?.focus()
    } catch {
      // clipboard not available
    }
  }

  const charCount = text.length
  const charPct   = Math.min((charCount / MAX_CHARS) * 100, 100)
  const charColor = charPct > 90 ? 'text-red-400' : charPct > 70 ? 'text-amber-400' : darkMode ? 'text-white/30' : 'text-gray-400'

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 flex flex-col gap-6">

      {/* Hero text */}
      <div className="text-center animate-fade-in">
        <h2 className="text-3xl sm:text-4xl font-bold leading-tight mb-2">
          <span className="gradient-text">Detect Spam & Fake News</span>
        </h2>
        <p className={`text-sm ${darkMode ? 'text-white/50' : 'text-gray-500'}`}>
          Powered by machine learning · TF-IDF + Logistic Regression / Naive Bayes / Random Forest
        </p>
      </div>

      {/* Input card */}
      <div className={`
        rounded-2xl p-5 shadow-2xl animate-slide-up
        ${darkMode
          ? 'glass border border-white/10 shadow-black/40'
          : 'bg-white border border-gray-200 shadow-gray-200/60'}
      `}>
        {/* Textarea */}
        <textarea
          ref={textareaRef}
          value={text}
          onChange={e => setText(e.target.value.slice(0, MAX_CHARS))}
          onKeyDown={handleKeyDown}
          placeholder="Paste or type any text to analyze — news article, SMS, email, social post…"
          rows={8}
          className={`input-area ${darkMode ? '' : 'light'}`}
        />

        {/* Char counter */}
        <div className="flex items-center justify-between mt-2 mb-4">
          <div className="flex gap-2">
            {EXAMPLES.map((ex) => (
              <button
                key={ex.label}
                onClick={() => { setText(ex.text); setResult(null); setError(null) }}
                className={`
                  text-[11px] px-2 py-1 rounded-md border transition-all duration-150
                  ${darkMode
                    ? 'border-white/10 text-white/40 hover:border-white/30 hover:text-white/70 hover:bg-white/5'
                    : 'border-gray-200 text-gray-400 hover:border-gray-300 hover:text-gray-600 hover:bg-gray-50'}
                `}
              >
                {ex.label}
              </button>
            ))}
          </div>
          <span className={`text-xs font-mono ${charColor}`}>
            {charCount}/{MAX_CHARS}
          </span>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <button onClick={handleAnalyze} disabled={!text.trim() || loading} className="btn-primary flex-1 sm:flex-none justify-center">
            {loading ? <LoadingSpinner size={16} /> : <Send size={16} />}
            {loading ? 'Analyzing…' : 'Analyze'}
            {!loading && <span className={`text-[10px] font-normal opacity-60 hidden sm:inline`}>(Ctrl+Enter)</span>}
          </button>

          <button
            onClick={handlePaste}
            className="btn-secondary"
            title="Paste from clipboard"
          >
            <ClipboardPaste size={15} />
            <span className="hidden sm:inline">Paste</span>
          </button>

          {(text || result) && (
            <button
              onClick={() => { setText(''); setResult(null); setError(null) }}
              className="btn-secondary"
              title="Clear"
            >
              <Trash2 size={15} />
              <span className="hidden sm:inline">Clear</span>
            </button>
          )}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-start gap-3 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 animate-slide-up">
          <AlertCircle size={18} className="shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-sm">Analysis failed</p>
            <p className="text-sm opacity-80 mt-0.5">{error}</p>
          </div>
        </div>
      )}

      {/* Loading state */}
      {loading && (
        <div className={`
          flex flex-col items-center gap-4 p-8 rounded-2xl animate-fade-in
          ${darkMode ? 'glass border border-white/10' : 'bg-white border border-gray-200'}
        `}>
          <div className="flex gap-2">
            <span className="typing-dot bg-indigo-400" />
            <span className="typing-dot bg-purple-400" />
            <span className="typing-dot bg-pink-400" />
          </div>
          <p className={`text-sm ${darkMode ? 'text-white/50' : 'text-gray-400'}`}>
            Processing text through ML pipeline…
          </p>
        </div>
      )}

      {/* Result */}
      {result && !loading && (
        <ResultCard result={result} text={text} darkMode={darkMode} />
      )}
    </div>
  )
}
