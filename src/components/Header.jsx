import { useState, useEffect } from 'react'
import { Sun, Moon, History, Zap, Wifi, WifiOff } from 'lucide-react'
import { fetchHealth } from '../api'

export default function Header({ darkMode, setDarkMode, showHistory, setShowHistory, historyCount }) {
  const [apiStatus, setApiStatus] = useState('checking') // 'checking' | 'online' | 'offline'
  const [modelName, setModelName] = useState(null)

  useEffect(() => {
    const check = async () => {
      try {
        const data = await fetchHealth()
        setApiStatus(data.status === 'ready' ? 'online' : 'no_model')
        setModelName(data.model_name)
      } catch {
        setApiStatus('offline')
      }
    }
    check()
    const id = setInterval(check, 30_000)
    return () => clearInterval(id)
  }, [])

  const statusDot = {
    online:   { color: 'bg-emerald-400', label: 'API Online',    icon: <Wifi size={12} /> },
    no_model: { color: 'bg-amber-400',   label: 'No Model',      icon: <Wifi size={12} /> },
    offline:  { color: 'bg-red-400',     label: 'API Offline',   icon: <WifiOff size={12} /> },
    checking: { color: 'bg-gray-400 animate-pulse', label: 'Connecting…', icon: null },
  }[apiStatus]

  return (
    <header className={`
      h-16 px-4 sm:px-6 flex items-center justify-between gap-4 z-50
      border-b backdrop-blur-xl sticky top-0
      ${darkMode
        ? 'border-white/10 bg-black/30'
        : 'border-gray-200/80 bg-white/70'}
    `}>
      {/* Logo */}
      <div className="flex items-center gap-2 shrink-0">
        <div className={`
          w-8 h-8 rounded-lg flex items-center justify-center
          bg-gradient-to-br from-indigo-500 to-purple-600
          shadow-lg shadow-indigo-500/30
        `}>
          <Zap size={16} className="text-white" />
        </div>
        <div>
          <h1 className={`font-bold text-base leading-none ${darkMode ? 'text-white' : 'text-gray-900'}`}>
            TruthLens
          </h1>
          <p className={`text-[10px] leading-none mt-0.5 ${darkMode ? 'text-white/40' : 'text-gray-400'}`}>
            Spam &amp; Fake News Detector
          </p>
        </div>
      </div>

      {/* Center — API status pill */}
      <div className="hidden sm:flex items-center gap-1.5">
        <span className={`w-2 h-2 rounded-full ${statusDot.color}`} />
        <span className={`text-xs font-medium ${darkMode ? 'text-white/50' : 'text-gray-400'}`}>
          {statusDot.label}
        </span>
        {modelName && (
          <>
            <span className={`text-xs ${darkMode ? 'text-white/20' : 'text-gray-200'}`}>·</span>
            <span className={`text-xs font-mono ${darkMode ? 'text-indigo-400' : 'text-indigo-500'}`}>
              {modelName}
            </span>
          </>
        )}
      </div>

      {/* Right — controls */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => setShowHistory(v => !v)}
          className={`
            relative flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium
            transition-all duration-200
            ${showHistory
              ? 'bg-indigo-500/20 text-indigo-400 border border-indigo-500/30'
              : darkMode
                ? 'text-white/60 hover:text-white hover:bg-white/10 border border-transparent'
                : 'text-gray-500 hover:text-gray-900 hover:bg-gray-100 border border-transparent'}
          `}
        >
          <History size={15} />
          <span className="hidden sm:inline">History</span>
          {historyCount > 0 && (
            <span className="absolute -top-1 -right-1 w-4 h-4 text-[9px] font-bold
              bg-indigo-500 text-white rounded-full flex items-center justify-center">
              {historyCount > 9 ? '9+' : historyCount}
            </span>
          )}
        </button>

        <button
          onClick={() => setDarkMode(v => !v)}
          className={`
            w-8 h-8 rounded-lg flex items-center justify-center
            transition-all duration-200
            ${darkMode
              ? 'text-yellow-300 hover:bg-yellow-300/10'
              : 'text-gray-500 hover:bg-gray-100'}
          `}
          aria-label="Toggle dark mode"
        >
          {darkMode ? <Sun size={16} /> : <Moon size={16} />}
        </button>
      </div>
    </header>
  )
}
