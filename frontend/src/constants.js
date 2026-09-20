export const MAX_CHARACTERS = 1000

// Fallback list used until /api/voices responds (or if it fails).
export const DEFAULT_LANGUAGES = [
  { code: 'en-US', label: 'English (US)' },
  { code: 'hi-IN', label: 'Hindi' },
  { code: 'gu-IN', label: 'Gujarati' },
  { code: 'mr-IN', label: 'Marathi' },
  { code: 'es-ES', label: 'Spanish' },
  { code: 'fr-FR', label: 'French' },
  { code: 'de-DE', label: 'German' },
]

export const DEFAULT_VOICES = {
  'en-US': [
    { id: 'en-US-female-1', label: 'English Female' },
    { id: 'en-US-male-1', label: 'English Male' },
  ],
  'hi-IN': [
    { id: 'hi-IN-female-1', label: 'Hindi Female' },
    { id: 'hi-IN-male-1', label: 'Hindi Male' },
  ],
  'gu-IN': [
    { id: 'gu-IN-female-1', label: 'Gujarati Female' },
  ],
  'mr-IN': [
    { id: 'mr-IN-female-1', label: 'Marathi Female' },
  ],
  'es-ES': [
    { id: 'es-ES-female-1', label: 'Spanish Female' },
    { id: 'es-ES-male-1', label: 'Spanish Male' },
  ],
  'fr-FR': [
    { id: 'fr-FR-female-1', label: 'French Female' },
  ],
  'de-DE': [
    { id: 'de-DE-female-1', label: 'German Female' },
  ],
}
