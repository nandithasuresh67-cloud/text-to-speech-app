import { useState } from 'react'
import { enhanceText } from '../api'

const MODES = [
  { value: 'cleanup', label: 'Clean up text' },
  { value: 'conversational', label: 'Make conversational' },
  { value: 'shorten', label: 'Shorten' },
]

export default function EnhanceControls({ text, onEnhanced, onError, disabled }) {
  const [mode, setMode] = useState('cleanup')
  const [loading, setLoading] = useState(false)

  const handleEnhance = async () => {
    if (!text.trim()) return
    setLoading(true)
    try {
      const result = await enhanceText(text, mode)
      if (result.success) {
        onEnhanced(result.text)
      } else {
        onError(result.message || 'Could not enhance the text.')
      }
    } catch (err) {
      const message = err.response?.data?.message || 'Could not enhance the text right now.'
      onError(message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex items-center gap-2">
      <select
        value={mode}
        onChange={(e) => setMode(e.target.value)}
        className="text-xs rounded-lg border border-gray-300 px-2 py-1.5 text-gray-600 bg-white"
      >
        {MODES.map((m) => (
          <option key={m.value} value={m.value}>
            {m.label}
          </option>
        ))}
      </select>
      <button
        type="button"
        onClick={handleEnhance}
        disabled={disabled || loading || !text.trim()}
        className="text-xs rounded-lg border border-gray-300 px-3 py-1.5 text-gray-600 hover:bg-gray-50 disabled:opacity-50"
      >
        {loading ? 'Enhancing...' : 'Enhance with AI'}
      </button>
    </div>
  )
}
