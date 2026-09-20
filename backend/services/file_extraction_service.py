"""
Text Extraction Service (spec section 17 - Text File Upload).
Extracts plain text from TXT, PDF, and DOCX uploads so it can be fed into
the TTS pipeline. Kept as its own seam (like tts_service.py) so adding a
new file type later means editing this file only.
"""
import io
from pypdf import PdfReader
from docx import Document

SUPPORTED_EXTENSIONS = {"txt", "pdf", "docx"}


class UnsupportedFileTypeError(Exception):
    pass


class FileExtractionError(Exception):
    pass


def get_extension(filename):
    if not filename or "." not in filename:
        return ""
    return filename.rsplit(".", 1)[1].lower()


def extract_text(file_storage):
    """
    Extract plain text from a Flask FileStorage object.
    Raises UnsupportedFileTypeError or FileExtractionError on failure.
    """
    ext = get_extension(file_storage.filename)
    if ext not in SUPPORTED_EXTENSIONS:
        raise UnsupportedFileTypeError(f"Unsupported file type: .{ext}")

    raw = file_storage.read()

    try:
        if ext == "txt":
            return raw.decode("utf-8", errors="ignore").strip()

        if ext == "pdf":
            reader = PdfReader(io.BytesIO(raw))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(pages).strip()

        if ext == "docx":
            document = Document(io.BytesIO(raw))
            paragraphs = [p.text for p in document.paragraphs]
            return "\n".join(paragraphs).strip()

    except Exception as exc:
        raise FileExtractionError(str(exc)) from exc

    raise UnsupportedFileTypeError(f"Unsupported file type: .{ext}")
