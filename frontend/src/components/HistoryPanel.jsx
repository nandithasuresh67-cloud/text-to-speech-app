import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { fetchHistory, deleteHistoryEntry, fetchFavorites, addFavorite, removeFavorite, resolveAudioUrl } from '../api'

export default function HistoryPanel({ refreshKey }) {
  const { isAuthenticated } = useAuth()
  const [history, setHistory] = useState([])
  const [favorites, setFavorites] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const favoriteEntryIds = new Set(favorites.map((f) => f.history_entry?.id))
  const favoriteIdByEntry = Object.fromEntries(favorites.map((f) => [f.history_entry?.id, f.id]))

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const [historyData, favoritesData] = await Promise.all([fetchHistory(), fetchFavorites()])
      setHistory(historyData.history || [])
      setFavorites(favoritesData.favorites || [])
    } catch {
      setError('Could not load your history right now.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isAuthenticated) load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated, refreshKey])

  if (!isAuthenticated) return null

  const handleDelete = async (id) => {
    try {
      await deleteHistoryEntry(id)
      setHistory((prev) => prev.filter((h) => h.id !== id))
      setFavorites((prev) => prev.filter((f) => f.history_entry?.id !== id))
    } catch {
      setError('Could not delete that entry.')
    }
  }

  const toggleFavorite = async (entryId) => {
    try {
      if (favoriteEntryIds.has(entryId)) {
        await removeFavorite(favoriteIdByEntry[entryId])
      } else {
        await addFavorite(entryId)
      }
      const favoritesData = await fetchFavorites()
      setFavorites(favoritesData.favorites || [])
    } catch {
      setError('Could not update favorites.')
    }
  }

  return (
    <div className="mt-8">
      <h2 className="text-sm font-medium text-gray-700 mb-3">Your speech history</h2>

      {loading && <p className="text-xs text-gray-400">Loading...</p>}
      {error && <p className="text-xs text-red-600">{error}</p>}
      {!loading && history.length === 0 && (
        <p className="text-xs text-gray-400">Nothing generated yet — it'll show up here once you do.</p>
      )}

      <ul className="space-y-2">
        {history.map((entry) => (
          <li
            key={entry.id}
            className="flex items-start justify-between gap-3 rounded-lg border border-gray-200 p-3 text-sm"
          >
            <div className="flex-1 min-w-0">
              <p className="text-gray-800 truncate">{entry.text}</p>
              <p className="text-xs text-gray-400 mt-0.5">
                {entry.language} &middot; {entry.voice} &middot; {new Date(entry.created_at).toLocaleString()}
              </p>
              <audio controls src={resolveAudioUrl(entry.audio_url)} className="w-full mt-2 h-8" />
            </div>
            <div className="flex flex-col gap-1 shrink-0">
              <button
                type="button"
                onClick={() => toggleFavorite(entry.id)}
                className={`text-xs px-2 py-1 rounded border ${
                  favoriteEntryIds.has(entry.id)
                    ? 'border-yellow-400 bg-yellow-50 text-yellow-700'
                    : 'border-gray-300 text-gray-500 hover:bg-gray-50'
                }`}
              >
                {favoriteEntryIds.has(entry.id) ? '★ Favorited' : '☆ Favorite'}
              </button>
              <button
                type="button"
                onClick={() => handleDelete(entry.id)}
                className="text-xs px-2 py-1 rounded border border-gray-300 text-gray-500 hover:bg-gray-50"
              >
                Delete
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
