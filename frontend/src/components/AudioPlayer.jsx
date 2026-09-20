export default function AudioPlayer({ audioUrl }) {
  if (!audioUrl) return null

  return (
    <div className="mt-6 rounded-lg border border-gray-200 bg-gray-50 p-4">
      <h3 className="text-sm font-medium text-gray-700 mb-2">Generated Audio</h3>
      <audio controls src={audioUrl} className="w-full">
        Your browser does not support the audio element.
      </audio>
    </div>
  )
}
