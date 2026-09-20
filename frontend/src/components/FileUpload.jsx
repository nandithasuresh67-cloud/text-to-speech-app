import { useRef, useState } from 'react'
import { uploadFile } from '../api'

export default function FileUpload({ onExtracted, onError }) {
  const inputRef = useRef(null)
  const [uploading, setUploading] = useState(false)

  const handleChange = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    setUploading(true)
    try {
      const result = await uploadFile(file)
      if (result.success) {
        onExtracted(result.text, result.truncated)
      } else {
        onError(result.message || 'Could not extract text from that file.')
      }
    } catch (err) {
      const message = err.response?.data?.message || 'Could not upload that file. Please try again.'
      onError(message)
    } finally {
      setUploading(false)
      if (inputRef.current) inputRef.current.value = ''
    }
  }

  return (
    <div>
      <input
        ref={inputRef}
        type="file"
        accept=".txt,.pdf,.docx"
        onChange={handleChange}
        disabled={uploading}
        className="hidden"
        id="file-upload-input"
      />
      <label
        htmlFor="file-upload-input"
        className="inline-flex items-center gap-2 text-xs rounded-lg border border-gray-300 px-3 py-1.5 text-gray-600 hover:bg-gray-50 cursor-pointer"
      >
        {uploading ? 'Extracting text...' : 'Upload a .txt, .pdf or .docx file'}
      </label>
    </div>
  )
}
