export default function GenerateButton({ onClick, loading, disabled }) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled || loading}
      className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-lg bg-brand-600 px-6 py-2.5 text-white font-medium shadow-sm transition
        hover:bg-brand-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
    >
      {loading && (
        <span className="h-4 w-4 border-2 border-white/60 border-t-white rounded-full animate-spin" />
      )}
      {loading ? 'Generating...' : 'Generate Speech'}
    </button>
  )
}
