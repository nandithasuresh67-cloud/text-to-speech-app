import { MAX_CHARACTERS } from '../constants'

export default function TextInput({ text, onChange }) {
  const charCount = text.length
  const wordCount = text.trim().length === 0 ? 0 : text.trim().split(/\s+/).length
  const overLimit = charCount > MAX_CHARACTERS

  return (
    <div className="w-full">
      <label htmlFor="tts-text" className="block text-sm font-medium text-gray-700 mb-2">
        Enter your text
      </label>
      <textarea
        id="tts-text"
        value={text}
        onChange={(e) => onChange(e.target.value)}
        rows={8}
        placeholder="Type or paste the text you want to convert to speech..."
        className={`w-full rounded-lg border p-4 text-gray-800 shadow-sm focus:outline-none focus:ring-2 resize-y
          ${overLimit ? 'border-red-400 focus:ring-red-300' : 'border-gray-300 focus:ring-brand-500'}`}
      />
      <div className="flex justify-between text-xs mt-1">
        <span className={overLimit ? 'text-red-600 font-medium' : 'text-gray-500'}>
          Characters: {charCount} / {MAX_CHARACTERS}
        </span>
        <span className="text-gray-500">Words: {wordCount}</span>
      </div>
      {overLimit && (
        <p className="text-red-600 text-xs mt-1">
          Text exceeds the maximum allowed length of {MAX_CHARACTERS} characters.
        </p>
      )}
    </div>
  )
}
