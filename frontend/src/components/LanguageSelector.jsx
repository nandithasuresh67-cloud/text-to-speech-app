export default function LanguageSelector({ languages, selected, onChange }) {
  return (
    <div>
      <label htmlFor="language-select" className="block text-sm font-medium text-gray-700 mb-2">
        Language
      </label>
      <select
        id="language-select"
        value={selected}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-lg border border-gray-300 p-2.5 text-gray-800 shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500 bg-white"
      >
        {languages.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.label}
          </option>
        ))}
      </select>
    </div>
  )
}
