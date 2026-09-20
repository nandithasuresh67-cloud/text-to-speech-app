# Text-to-Speech Application (Python Stack: React + Flask)

Converts written text into natural-sounding speech. Users enter text, pick a
language and voice, generate audio, then play or download it.

## Progress against the suggested timeline

**Day 1 — Foundation**
- [x] Project requirements reviewed (see attached spec).
- [x] Project structure created (`frontend/`, `backend/`) matching the spec's
      Flask layout.

**Day 2 — UI design & build**
- [x] React + Tailwind frontend built with all core components:
      `TextInput`, `LanguageSelector`, `VoiceSelector`, `GenerateButton`,
      `AudioPlayer`, `DownloadButton`, `ErrorMessage`.
- [x] Text input with live character/word count and a max-length limit.
- [x] Language and voice selection (voice list updates based on language).
- [x] Client-side validation (empty text, over-limit text, missing
      language/voice).
- [x] Clear/reset control.

**Days 6–7 — Backend & connection**
- [x] Flask backend created (`/api/tts`, `/api/voices`, `/api/health`) using
      gTTS as the TTS provider.
- [x] Frontend connected to the backend over REST (axios + Vite dev proxy).
- [x] Backend-side validation, error handling, and HTTP status codes
      (400/429/500/503) per the spec's section 15.

**Days 8–10 — Backend & TTS integration hardening**
- [x] Rate limiting on the API (60/min overall, 10/min on `/api/tts`) per the
      spec's security section — returns a proper `429` with a clear message.
- [x] Retry logic in the TTS service: transient provider failures are retried
      twice with a short backoff before returning `503`.
- [x] Automatic cleanup of generated audio files older than 1 hour (audio is
      not stored permanently, per spec section 16).
- [x] `backend/test_api.py` — automated pytest suite covering health, voices,
      and all `/api/tts` validation/error paths (9 tests, all passing).
- [x] `backend/postman_collection.json` — importable Postman collection
      covering the happy path and every error case from spec section 18.

**Days 11–13 — Audio return, playback & download**
- [x] Backend returns generated audio via `audio_url`, served from
      `/api/audio/<file>` (Day 11).
- [x] Frontend `AudioPlayer` plays the returned audio inline (Day 12).
- [x] `DownloadButton` lets users download the generated file (Day 13).
- [x] `resolveAudioUrl` in `api.js` makes playback/download work whether the
      frontend and backend are served from the same origin (dev) or two
      different origins (production deployment).

**Day 14 — Testing, error handling & deployment**
- [x] React `ErrorBoundary` added around the app to catch unexpected render
      errors gracefully instead of a blank white screen.
- [x] Distinct handling for request timeouts vs. generic network failure in
      the frontend's error messages.
- [x] Production deployment configs added (see "Deployment" below):
      `Procfile` + `gunicorn` for the backend, `vercel.json` / `netlify.toml`
      for the frontend, and `VITE_API_BASE_URL` for cross-origin deployments.
- [x] Backend test suite (`pytest`) and Postman collection from Days 8–10
      cover the required API testing.

**Not yet done**
- [ ] Cloud audio storage (S3/GCS) instead of local disk.
- [ ] Admin dashboard and analytics.
- [ ] Real LLM-backed text enhancement (current implementation is
      rule-based — see "Level 3" below for the upgrade path).

## Level 2 — Authentication, speech history & favorites

Beyond the 14-day plan, the project also includes the spec's Level 2
(Intermediate) features:

- **User authentication** — JWT-based register/login (`flask-jwt-extended`),
  passwords hashed with Werkzeug's `generate_password_hash`.
- **Database** — SQLite by default via SQLAlchemy (`backend/models.py`);
  swap in Postgres in production by setting `DATABASE_URL`.
- **Speech history** — every `/api/tts` call made while logged in is saved
  (text, language, voice, audio URL, timestamp) and viewable/deletable via
  the frontend's history panel. Anonymous requests still work exactly as
  before — auth is optional on `/api/tts`.
- **Favorites** — logged-in users can star/unstar any history entry.
- **Frontend** — `AuthContext` (token stored in `localStorage`), `AuthPanel`
  (login/register/logout), `HistoryPanel` (list, play, delete, favorite).

Level 2 backend endpoints:
- `POST /api/auth/register` — `{ email, password }` → `{ access_token, user }`
- `POST /api/auth/login` — `{ email, password }` → `{ access_token, user }`
- `GET /api/history` *(auth required)* — recent generations for the logged-in user
- `DELETE /api/history/<id>` *(auth required)*
- `GET /api/favorites` *(auth required)*
- `POST /api/favorites/<history_id>` *(auth required)*
- `DELETE /api/favorites/<favorite_id>` *(auth required)*

## Level 3 — AI enhancement, file upload & usage limits

- **AI text enhancement** (`POST /api/enhance`) — three modes: `cleanup`
  (whitespace/punctuation/capitalization fixes), `conversational` (adds
  contractions for a more natural spoken tone), and `shorten` (naive
  extractive summary). Implemented rule-based by default (no API key
  needed); `services/enhancement_service.py` has a clear seam
  (`_enhance_with_llm`) to swap in a real LLM later, same pattern as the
  TTS provider.
- **Text file upload** (`POST /api/upload`) — extracts text from `.txt`,
  `.pdf`, and `.docx` files (5 MB max) so it can be dropped straight into
  the text box. Frontend: `FileUpload` component next to the text area.
- **Usage limits** — logged-in users are capped at `DAILY_GENERATION_LIMIT`
  (default 50) speech generations per rolling 24 hours; a `429` is returned
  once the limit is hit. Anonymous users are unaffected by this cap (they
  still only have the per-minute rate limit from Days 8–10).

Level 3 backend endpoints:
- `POST /api/upload` — multipart form, field `file` → `{ text, truncated }`
- `POST /api/enhance` — `{ text, mode }` → `{ text }`

## Project structure

```
text-to-speech/
├── frontend/                # React + Vite + Tailwind
│   ├── src/
│   │   ├── components/      # TextInput, LanguageSelector, VoiceSelector,
│   │   │                    # GenerateButton, AudioPlayer, DownloadButton,
│   │   │                    # ErrorMessage, ErrorBoundary, AuthPanel,
│   │   │                    # HistoryPanel, FileUpload, EnhanceControls
│   │   ├── context/
│   │   │   └── AuthContext.jsx   # login/register/logout, JWT storage
│   │   ├── api.js           # axios client for the backend
│   │   ├── constants.js     # default languages/voices + max char limit
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
│
├── backend/                  # Flask
│   ├── app.py
│   ├── models.py              # User, HistoryEntry, Favorite (SQLAlchemy)
│   ├── routes/
│   │   ├── tts_routes.py      # /api/tts, /api/voices, /api/health, /api/audio/<file>
│   │   ├── auth_routes.py     # /api/auth/register, /api/auth/login
│   │   ├── history_routes.py  # /api/history, /api/favorites
│   │   └── content_routes.py  # /api/upload, /api/enhance
│   ├── services/
│   │   ├── tts_service.py           # provider seam — currently gTTS
│   │   ├── file_extraction_service.py  # TXT/PDF/DOCX text extraction
│   │   └── enhancement_service.py      # rule-based text enhancement
│   ├── utils/
│   │   └── validation.py
│   └── generated_audio/      # generated mp3 files (gitignored)
│
│   ├── extensions.py          # shared Flask extensions (db, jwt, limiter)
│   ├── postman_collection.json
│   ├── test_api.py            # pytest suite (24 tests)
│   └── Procfile               # gunicorn start command for Render/Railway
│
├── requirements.txt          # (see backend/requirements.txt)
├── .env.example
└── README.md
```

## Running it locally

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env         # adjust if needed
python app.py                   # runs on http://localhost:5000
```

### Frontend

```bash
cd frontend
npm install
npm run dev                     # runs on http://localhost:5173
```

The Vite dev server proxies `/api` and `/audio` requests to the Flask
backend (see `frontend/vite.config.js`), so no CORS configuration is needed
in development beyond what's already set up in `backend/app.py`.

Open http://localhost:5173, type some text, pick a language/voice, and click
**Generate Speech**. If the backend isn't running, the UI still loads (using
built-in default languages/voices) and will show a clear network-error
message when you try to generate.

## Testing

```bash
cd backend
pip install -r requirements.txt pytest
pytest test_api.py -v
```

A Postman collection (`backend/postman_collection.json`) is also included —
import it, covering both the core TTS endpoints and all Level 2/3
endpoints (register, login, history, favorites, upload, enhance). The
history/favorites/enhance requests that need auth expect an
`Authorization: Bearer <token>` header, obtained from the login response.

## API

- `POST /api/tts` — `{ "text": "...", "language": "en-US", "voice": "en-US-female-1" }`
  → `{ "success": true, "audio_url": "/api/audio/<file>.mp3" }` (adds
  `history_id` when authenticated)
- `GET /api/voices` — returns `{ languages, voicesByLanguage }`
- `GET /api/health` — returns `{ "status": "ok" }`
- `POST /api/upload` — multipart `file` field → `{ text, truncated }`
- `POST /api/enhance` — `{ text, mode }` → `{ text }`
- Auth & history/favorites endpoints — see "Level 2" above.

## Notes on the TTS provider

The spec lists Google Cloud TTS / Azure / Polly / ElevenLabs as options.
Those need paid API keys, so this implementation uses **gTTS** (free, no key
required) so the app is fully runnable out of the box. `services/tts_service.py`
is intentionally the only place that talks to the provider — swapping in a
cloud provider later means changing that file only, not the routes or the
frontend.

## Deployment

### Backend (Render / Railway)

1. Push the `backend/` folder to a Git repo (or point the platform at this
   whole repo with `backend` as the root/start directory).
2. Set environment variables from `.env.example` in the platform's dashboard
   — at minimum `FRONTEND_ORIGIN` (your deployed frontend's URL, for CORS).
3. Both Render and Railway detect `Procfile` automatically and run:
   ```
   gunicorn -w 2 -b 0.0.0.0:$PORT app:app
   ```
4. Note: `flask-limiter`'s default in-memory store doesn't share state across
   multiple gunicorn workers/replicas. For a single small instance (as in
   this project) that's fine; for multi-instance production use, configure a
   shared backend (e.g. Redis) per the flask-limiter docs.

### Frontend (Vercel / Netlify)

1. Set the project root to `frontend/`.
2. Build command: `npm run build`, output directory: `dist` (both
   `vercel.json` and `netlify.toml` are already included and pre-configured).
3. Set the environment variable `VITE_API_BASE_URL` to your deployed
   backend's URL (e.g. `https://text-to-speech-backend.onrender.com`) —
   without this, the frontend will try to call its own origin for the API,
   which only works when frontend and backend share a domain.
4. Redeploy after setting the env var (Vite bakes env vars in at build time).
