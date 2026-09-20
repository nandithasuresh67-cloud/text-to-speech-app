export default function ErrorMessage({ message, onDismiss }) {
  if (!message) return null

  return (
    <div className="mt-4 flex items-start justify-between gap-3 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
      <span>{message}</span>
      {onDismiss && (
        <button
          type="button"
          onClick={onDismiss}
          className="text-red-500 hover:text-red-700 font-bold leading-none"
          aria-label="Dismiss error"
        >
          &times;
        </button>
      )}
    </div>
  )
}
