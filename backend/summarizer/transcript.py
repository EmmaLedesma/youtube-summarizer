"""
transcript.py — Extrae transcripts de YouTube via Supadata API.

Supadata corre server-side, sin restricciones de IP ni CORS.
Documentación: https://supadata.ai/documentation
"""

import urllib.request
import urllib.error
import json


SUPADATA_BASE_URL = "https://api.supadata.ai/v1/youtube/transcript"


def get_transcript(video_id: str) -> dict:
    """
    Obtiene el transcript de un video de YouTube via Supadata.

    Args:
        video_id: ID del video (ej: "dQw4w9WgXcQ")

    Returns:
        dict con keys:
            - text (str): transcript completo como texto plano
            - language (str): idioma detectado

    Raises:
        ValueError: si el video no tiene subtítulos disponibles
        RuntimeError: si hay un error de conexión con Supadata
    """
    url = f"{SUPADATA_BASE_URL}?videoId={video_id}&text=true"

    try:
        req = urllib.request.Request(
            url,
            headers={"Accept": "application/json"},
        )

        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))

        # Supadata devuelve { content: "...", lang: "en" } cuando text=true
        transcript_text = data.get("content", "").strip()
        language_code = data.get("lang", "en")

        if not transcript_text:
            raise ValueError("El transcript está vacío.")

        return {
            "text": transcript_text,
            "language": _language_code_to_name(language_code),
            "languageCode": language_code,
        }

    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise ValueError(
                "No se encontraron subtítulos para este video. "
                "El video puede ser privado o no tener subtítulos disponibles."
            )
        if e.code == 429:
            raise RuntimeError(
                "Límite de requests a Supadata alcanzado. Intentá en unos minutos."
            )
        raise RuntimeError(f"Error de Supadata (HTTP {e.code}): {e.reason}")

    except urllib.error.URLError as e:
        raise RuntimeError(f"No se pudo conectar a Supadata: {str(e.reason)}")

    except json.JSONDecodeError:
        raise RuntimeError("Respuesta inválida de Supadata.")


def _language_code_to_name(code: str) -> str:
    """Convierte código ISO 639-1 a nombre legible."""
    mapping = {
        "en": "English",
        "es": "Spanish",
        "pt": "Portuguese",
        "fr": "French",
        "de": "German",
        "it": "Italian",
        "ja": "Japanese",
        "ko": "Korean",
        "zh": "Chinese",
        "ru": "Russian",
        "ar": "Arabic",
        "hi": "Hindi",
    }
    return mapping.get(code.lower(), code.upper())