import axios from 'axios'

// In development, the Vite proxy (see vite.config.js) forwards /api and
// /audio to the local Flask server, so an empty base URL works. In
// production the frontend and backend are typically deployed separately
// (e.g. Vercel + Render), so VITE_API_BASE_URL must point at the deployed
// backend's origin (e.g. https://my-tts-backend.onrender.com).
const baseURL = import.meta.env.VITE_API_BASE_URL || ''

const client = axios.create({
  baseURL,
  timeout: 30000,
})

/**
 * Resolve a relative audio_url (e.g. "/api/audio/xyz.mp3") returned by the
 * backend into an absolute URL when the frontend is hosted separately from
 * the backend (production). In development this is a no-op since the Vite
 * proxy already handles relative paths.
 */
export function resolveAudioUrl(audioUrl) {
  if (!audioUrl) return audioUrl
  if (/^https?:\/\//i.test(audioUrl)) return audioUrl
  return `${baseURL}${audioUrl}`
}

/**
 * Fetch the list of available voices/languages from the backend.
 * Falls back gracefully — callers should handle rejection.
 */
export async function fetchVoices() {
  const response = await client.get('/api/voices')
  return response.data
}

/**
 * Check backend health.
 */
export async function checkHealth() {
  const response = await client.get('/api/health')
  return response.data
}

/**
 * Request speech generation from the backend.
 * @param {{text: string, language: string, voice: string}} payload
 */
export async function generateSpeech(payload) {
  const response = await client.post('/api/tts', payload)
  return response.data
}

/**
 * Upload a TXT/PDF/DOCX file and get its extracted text back.
 * @param {File} file
 */
export async function uploadFile(file) {
  const formData = new FormData()
  formData.append('file', file)
  const response = await client.post('/api/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

/**
 * Run AI text enhancement on the given text.
 * @param {string} text
 * @param {'cleanup'|'conversational'|'shorten'} mode
 */
export async function enhanceText(text, mode = 'cleanup') {
  const response = await client.post('/api/enhance', { text, mode })
  return response.data
}

/**
 * Fetch the current user's speech history (requires auth).
 */
export async function fetchHistory() {
  const response = await client.get('/api/history')
  return response.data
}

export async function deleteHistoryEntry(entryId) {
  const response = await client.delete(`/api/history/${entryId}`)
  return response.data
}

/**
 * Fetch the current user's favorited generations (requires auth).
 */
export async function fetchFavorites() {
  const response = await client.get('/api/favorites')
  return response.data
}

export async function addFavorite(entryId) {
  const response = await client.post(`/api/favorites/${entryId}`)
  return response.data
}

export async function removeFavorite(favoriteId) {
  const response = await client.delete(`/api/favorites/${favoriteId}`)
  return response.data
}

export default client

