import { useState, useCallback } from 'react'
import Header from './components/Header'
import TextAnalyzer from './components/TextAnalyzer'
import HistoryPanel from './components/HistoryPanel'
import { analyzeText } from './api'

export default function App() {
  const [darkMode, setDarkMode] = useState(true)
  const [history, setHistory] = useState([])
  const [showHistory, setShowHistory] = useState(false)
  const [selectedHistoryItem, setSelectedHistoryItem] = useState(null)

  const handleResult = useCallback((entry) => {
    setHistory(prev => {
      const updated = [entry, ...prev].slice(0, 50)
      return updated
    })
  }, [])

  const handleHistorySelect = useCallback((item) => {
    setSelectedHistoryItem(item)
  }, [])

  const handleClearHistory = useCallback(() => {
    setHistory([])
    setSelectedHistoryItem(null)
  }, [])

  return (
    <div className={darkMode ? 'dark' : 'light'}>
      <div className={`min-h-screen transition-colors duration-500 ${darkMode ? 'bg-animated text-white' : 'bg-light text-gray-900'}`}>
        <Header
          darkMode={darkMode}
          setDarkMode={setDarkMode}
          showHistory={showHistory}
          setShowHistory={setShowHistory}
          historyCount={history.length}
        />

        <div className="flex h-[calc(100vh-64px)]">
          {/* Main content */}
          <main className="flex-1 overflow-y-auto">
            <TextAnalyzer
              onResult={handleResult}
              prefill={selectedHistoryItem}
              darkMode={darkMode}
            />
          </main>

          {/* History sidebar */}
          {showHistory && (
            <aside className={`
              w-80 border-l overflow-hidden flex-shrink-0
              ${darkMode
                ? 'border-white/10 bg-black/20 backdrop-blur-xl'
                : 'border-gray-200 bg-white/60 backdrop-blur-xl'}
            `}>
              <HistoryPanel
                history={history}
                onSelect={handleHistorySelect}
                onClear={handleClearHistory}
                darkMode={darkMode}
              />
            </aside>
          )}
        </div>
      </div>
    </div>
  )
}
