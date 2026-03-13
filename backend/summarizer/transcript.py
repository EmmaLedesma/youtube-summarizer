"""
transcript.py — Extrae transcripts de YouTube via youtube-transcript-api.
"""

from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled


def get_transcript(video_id: str) -> dict:
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Prioridad: manual > auto-generated, cualquier idioma
        try:
            transcript = transcript_list.find_manually_created_transcript(
                ['en', 'es', 'pt', 'fr', 'de', 'it', 'ja', 'ko', 'zh', 'ru', 'ar', 'hi']
            )
        except NoTranscriptFound:
            transcript = transcript_list.find_generated_transcript(
                ['en', 'es', 'pt', 'fr', 'de', 'it', 'ja', 'ko', 'zh', 'ru', 'ar', 'hi']
            )

        language_code = transcript.language_code
        entries = transcript.fetch()
        transcript_text = " ".join(entry["text"] for entry in entries).strip()

        if not transcript_text:
            raise ValueError("El transcript está vacío.")

        return {
            "text": transcript_text,
            "language": _language_code_to_name(language_code),
            "languageCode": language_code,
        }

    except TranscriptsDisabled:
        raise ValueError("Este video tiene los subtítulos desactivados.")
    except NoTranscriptFound:
        raise ValueError("No se encontró transcript para este video.")
    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise RuntimeError(f"Error obteniendo transcript: {str(e)}")


def _language_code_to_name(code: str) -> str:
    mapping = {
        "en": "English", "es": "Spanish", "pt": "Portuguese",
        "fr": "French", "de": "German", "it": "Italian",
        "ja": "Japanese", "ko": "Korean", "zh": "Chinese",
        "ru": "Russian", "ar": "Arabic", "hi": "Hindi",
    }
    return mapping.get(code.lower(), code.upper())