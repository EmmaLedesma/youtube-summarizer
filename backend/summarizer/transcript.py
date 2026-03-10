"""
Módulo para extraer transcripts de videos de YouTube.
Usa youtube-transcript-api v1.x (no requiere API key).
"""

import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)


def extract_video_id(url: str) -> str:
    """
    Extrae el videoId de cualquier formato de URL de YouTube.

    Soporta:
    - https://www.youtube.com/watch?v=dQw4w9WgXcQ
    - https://youtu.be/dQw4w9WgXcQ
    - https://www.youtube.com/embed/dQw4w9WgXcQ
    """
    patterns = [
        r"(?:v=)([a-zA-Z0-9_-]{11})",
        r"(?:youtu\.be/)([a-zA-Z0-9_-]{11})",
        r"(?:embed/)([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    raise ValueError(f"No se pudo extraer videoId de la URL: {url}")


def get_transcript(video_id: str) -> dict:
    """
    Obtiene el transcript de un video de YouTube.

    Retorna:
    {
        "text": "texto completo del transcript",
        "language": "Spanish",
        "language_code": "es",
        "is_generated": True/False,
        "duration_seconds": 1234
    }
    """
    try:
        api = YouTubeTranscriptApi()

        # Listar transcripts disponibles
        transcript_list = api.list(video_id)

        # Prioridad: manual > generado automáticamente
        transcript = None
        is_generated = False

        try:
            transcript = transcript_list.find_manually_created_transcript()
        except Exception:
            try:
                transcript = transcript_list.find_generated_transcript(["es", "en"])
                is_generated = True
            except Exception:
                # Tomar cualquier transcript disponible
                all_transcripts = list(transcript_list)
                if all_transcripts:
                    transcript = all_transcripts[0]
                    is_generated = True

        if not transcript:
            raise NoTranscriptFound(video_id, [], {})

        # Obtener las entradas del transcript
        fetched = transcript.fetch()

        # En v1.x, fetch() retorna un FetchedTranscript iterable
        entries = list(fetched)

        # Extraer texto de cada snippet
        full_text = " ".join(
            snippet.text for snippet in entries
        ).replace("\n", " ").strip()

        # Duración total
        last = entries[-1] if entries else None
        duration = int(last.start + last.duration) if last else 0

        return {
            "text": full_text,
            "language": transcript.language,
            "language_code": transcript.language_code,
            "is_generated": is_generated,
            "duration_seconds": duration,
        }

    except TranscriptsDisabled:
        raise ValueError(
            "Este video tiene los subtítulos desactivados por el autor."
        )
    except NoTranscriptFound:
        raise ValueError(
            "No se encontraron subtítulos para este video. "
            "Puede ser muy reciente o no tener captions disponibles."
        )
    except VideoUnavailable:
        raise ValueError(
            "El video no está disponible. Verificá que la URL sea correcta "
            "y que el video sea público."
        )