import { useEffect, useState } from 'react'

export default function ConfidenceBar({ pct, barClass, darkMode }) {
  const [width, setWidth] = useState(0)

  useEffect(() => {
    const id = setTimeout(() => setWidth(pct), 80)
    return () => clearTimeout(id)
  }, [pct])

  return (
    <div className={`relative h-3 rounded-full overflow-hidden ${darkMode ? 'bg-white/10' : 'bg-gray-200'}`}>
      {/* Animated fill */}
      <div
        className={`absolute inset-y-0 left-0 rounded-full bar-fill ${barClass}`}
        style={{ width: `${width}%` }}
      />
      {/* Tick marks */}
      {[25, 50, 75].map(t => (
        <div
          key={t}
          className={`absolute top-0 bottom-0 w-px ${darkMode ? 'bg-white/10' : 'bg-white/60'}`}
          style={{ left: `${t}%` }}
        />
      ))}
      {/* Shine overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-white/20 to-transparent rounded-full pointer-events-none" />
    </div>
  )
}
