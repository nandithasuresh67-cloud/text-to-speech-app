export default function DownloadButton({ audioUrl, fileName = 'generated-speech.mp3' }) {
  if (!audioUrl) return null

  return (
    <a
      href={audioUrl}
      download={fileName}
      className="mt-3 inline-flex items-center gap-2 rounded-lg border border-brand-600 px-4 py-2 text-sm font-medium text-brand-700 hover:bg-brand-50 transition"
    >
      Download Audio
    </a>
  )
}
