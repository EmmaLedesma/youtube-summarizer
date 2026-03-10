"""
Cliente para AWS Bedrock — invoca Claude 3.5 Haiku para resumir transcripts.
"""

import json
import boto3
from botocore.exceptions import ClientError


MODEL_ID = "us.anthropic.claude-3-5-haiku-20241022-v1:0"


def get_bedrock_client(region: str = "us-east-1"):
    """Crea cliente de Bedrock Runtime."""
    session = boto3.Session(profile_name="yt-summarizer")
    return session.client("bedrock-runtime", region_name=region)


def build_prompt(transcript_text: str, language: str) -> str:
    """
    Construye el prompt para Claude 3.5 Haiku.
    """
    return f"""You are an expert at analyzing and summarizing video content.

Analyze the following video transcript and provide a structured summary.
The transcript language is: {language}
Respond in the SAME language as the transcript.

TRANSCRIPT:
{transcript_text[:15000]}

Provide your response in the following JSON format (no markdown, just JSON):
{{
  "executive_summary": "2-3 sentence overview of the main topic",
  "key_points": [
    "Key point 1",
    "Key point 2",
    "Key point 3",
    "Key point 4",
    "Key point 5"
  ],
  "main_topics": ["topic1", "topic2", "topic3"],
  "detected_language": "language name in English",
  "content_type": "tutorial/lecture/conference/interview/other"
}}"""


def summarize_transcript(transcript_text: str, language: str) -> dict:
    """
    Envía el transcript a Claude 3.5 Haiku via Bedrock y retorna el resumen.
    Usa la Converse API — agnóstica al modelo.
    """
    client = get_bedrock_client()
    prompt = build_prompt(transcript_text, language)

    try:
        response = client.converse(
            modelId=MODEL_ID,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": prompt}],
                }
            ],
            inferenceConfig={
                "maxTokens": 1024,
                "temperature": 0.3,
                "topP": 0.9,
            },
        )

        response_text = response["output"]["message"]["content"][0]["text"]
        summary = json.loads(response_text)

        summary["_usage"] = {
            "input_tokens": response["usage"]["inputTokens"],
            "output_tokens": response["usage"]["outputTokens"],
        }

        return summary

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "AccessDeniedException":
            raise RuntimeError(
                "Sin acceso a Bedrock. Verificá los permisos IAM."
            )
        raise RuntimeError(f"Error de Bedrock: {error_code} — {str(e)}")

    except json.JSONDecodeError:
        return {
            "executive_summary": response_text,
            "key_points": [],
            "main_topics": [],
            "detected_language": language,
            "content_type": "other",
            "_usage": {},
        }