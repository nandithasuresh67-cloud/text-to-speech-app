export default function VoiceSelector({ voices, selected, onChange }) {
  return (
    <div>
      <label htmlFor="voice-select" className="block text-sm font-medium text-gray-700 mb-2">
        Voice
      </label>
      <select
        id="voice-select"
        value={selected}
        onChange={(e) => onChange(e.target.value)}
        disabled={voices.length === 0}
        className="w-full rounded-lg border border-gray-300 p-2.5 text-gray-800 shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500 bg-white disabled:bg-gray-100"
      >
        {voices.length === 0 && <option value="">No voices available</option>}
        {voices.map((voice) => (
          <option key={voice.id} value={voice.id}>
            {voice.label}
          </option>
        ))}
      </select>
    </div>
  )
}
