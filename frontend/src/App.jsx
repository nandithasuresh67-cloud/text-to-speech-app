import { useEffect, useState } from 'react'
import TextInput from './components/TextInput'
import LanguageSelector from './components/LanguageSelector'
import VoiceSelector from './components/VoiceSelector'
import GenerateButton from './components/GenerateButton'
import AudioPlayer from './components/AudioPlayer'
import DownloadButton from './components/DownloadButton'
import ErrorMessage from './components/ErrorMessage'
import AuthPanel from './components/AuthPanel'
import HistoryPanel from './components/HistoryPanel'
import FileUpload from './components/FileUpload'
import EnhanceControls from './components/EnhanceControls'
import { fetchVoices, generateSpeech, resolveAudioUrl } from './api'
import { MAX_CHARACTERS, DEFAULT_LANGUAGES, DEFAULT_VOICES } from './constants'

export default function App() {
  const [text, setText] = useState('')
  const [languages, setLanguages] = useState(DEFAULT_LANGUAGES)
  const [voicesByLanguage, setVoicesByLanguage] = useState(DEFAULT_VOICES)
  const [language, setLanguage] = useState(DEFAULT_LANGUAGES[0].code)
  const [voice, setVoice] = useState(DEFAULT_VOICES[DEFAULT_LANGUAGES[0].code][0].id)
  const [loading, setLoading] = useState(false)
  const [audioUrl, setAudioUrl] = useState(null)
  const [error, setError] = useState(null)
  const [historyRefreshKey, setHistoryRefreshKey] = useState(0)

  // Load voices/languages from the backend on mount. Fall back to the
  // built-in defaults if the backend is unreachable — the UI should still work.
  useEffect(() => {
    let cancelled = false
    fetchVoices()
      .then((data) => {
        if (cancelled || !data) return
        if (data.languages && data.languages.length > 0) {
          setLanguages(data.languages)
          setLanguage(data.languages[0].code)
        }
        if (data.voicesByLanguage) {
          setVoicesByLanguage(data.voicesByLanguage)
          const firstLang = data.languages ? data.languages[0].code : language
          const firstVoices = data.voicesByLanguage[firstLang] || []
          if (firstVoices.length > 0) setVoice(firstVoices[0].id)
        }
      })
      .catch(() => {
        // Backend not available yet (e.g. Day 1 frontend-only run) — keep defaults.
      })
    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const currentVoices = voicesByLanguage[language] || []

  const handleLanguageChange = (code) => {
    setLanguage(code)
    const nextVoices = voicesByLanguage[code] || []
    setVoice(nextVoices.length > 0 ? nextVoices[0].id : '')
  }

  const handleClear = () => {
    setText('')
    setAudioUrl(null)
    setError(null)
  }

  const validate = () => {
    if (text.trim().length === 0) {
      return 'Please enter some text before generating speech.'
    }
    if (text.length > MAX_CHARACTERS) {
      return `Text exceeds the maximum allowed length of ${MAX_CHARACTERS} characters.`
    }
    if (!language) {
      return 'Please select a language.'
    }
    if (!voice) {
      return 'Please select a voice.'
    }
    return null
  }

  const handleGenerate = async () => {
    const validationError = validate()
    if (validationError) {
      setError(validationError)
      return
    }

    setError(null)
    setAudioUrl(null)
    setLoading(true)

    try {
      const result = await generateSpeech({ text, language, voice })
      if (result && result.success && result.audio_url) {
        setAudioUrl(resolveAudioUrl(result.audio_url))
        setHistoryRefreshKey((k) => k + 1)
      } else {
        setError((result && result.message) || 'The server could not generate audio for this request.')
      }
    } catch (err) {
      if (err.response) {
        const status = err.response.status
        const serverMessage = err.response.data && err.response.data.message
        if (status === 400) {
          setError(serverMessage || 'Invalid request. Please check your text, language and voice.')
        } else if (status === 401 || status === 403) {
          setError('Authentication with the speech service failed. Please contact the administrator.')
        } else if (status === 429) {
          setError('Too many requests. Please wait a moment and try again.')
        } else if (status === 503) {
          setError('The text-to-speech service is temporarily unavailable. Please try again later.')
        } else {
          setError(serverMessage || 'The server encountered an error while generating speech.')
        }
      } else if (err.code === 'ECONNABORTED') {
        setError('The request timed out. Please try again with shorter text or check your connection.')
      } else if (err.request) {
        setError('Could not reach the server. Please check your network connection.')
      } else {
        setError('Something went wrong while generating speech.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-brand-50 to-white py-10 px-4">
      <div className="max-w-2xl mx-auto">
        <header className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Text to Speech</h1>
          <p className="text-gray-500 mt-1">Convert written text into natural-sounding speech.</p>
        </header>

        <div className="mb-6">
          <AuthPanel />
        </div>

        <div className="bg-white rounded-2xl shadow-md p-6 sm:p-8">
          <TextInput text={text} onChange={setText} />

          <div className="flex flex-wrap items-center gap-3 mt-3">
            <FileUpload
              onExtracted={(extractedText, truncated) => {
                setText(extractedText)
                setError(truncated ? `Text was truncated to ${MAX_CHARACTERS} characters.` : null)
              }}
              onError={setError}
            />
            <EnhanceControls
              text={text}
              onEnhanced={setText}
              onError={setError}
              disabled={loading}
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-6">
            <LanguageSelector languages={languages} selected={language} onChange={handleLanguageChange} />
            <VoiceSelector voices={currentVoices} selected={voice} onChange={setVoice} />
          </div>

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 mt-6">
            <GenerateButton onClick={handleGenerate} loading={loading} disabled={text.trim().length === 0} />
            <button
              type="button"
              onClick={handleClear}
              className="w-full sm:w-auto rounded-lg border border-gray-300 px-6 py-2.5 text-gray-700 font-medium hover:bg-gray-50 transition"
            >
              Clear
            </button>
          </div>

          <ErrorMessage message={error} onDismiss={() => setError(null)} />

          <AudioPlayer audioUrl={audioUrl} />
          <DownloadButton audioUrl={audioUrl} />

          <HistoryPanel refreshKey={historyRefreshKey} />
        </div>

        <footer className="text-center text-xs text-gray-400 mt-6">
          Python Stack &middot; React + Flask/FastAPI
        </footer>
      </div>
    </div>
  )
}
