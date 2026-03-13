"""
Cliente para AWS Bedrock — invoca Claude 3.5 Haiku para resumir transcripts.
"""

import json
import boto3
from botocore.exceptions import ClientError

MODEL_ID = "us.anthropic.claude-3-5-haiku-20241022-v1:0"


def get_bedrock_client(region: str = "us-east-1"):
    return boto3.client("bedrock-runtime", region_name=region)


def build_prompt(transcript_text: str, language: str) -> str:
    return f"""You are an expert at analyzing and summarizing video and lecture content.

Analyze the following video transcript and provide a DETAILED and COMPREHENSIVE structured summary.
The transcript language is: {language}
Respond in the SAME language as the transcript. If the language is Spanish, respond entirely in Spanish. If English, in English, etc.

TRANSCRIPT:
{transcript_text[:20000]}

Provide your response in the following JSON format (no markdown, just JSON):
{{
  "executive_summary": "A thorough 4-6 sentence overview covering the main topic, key arguments, and conclusions of the video",
  "key_points": [
    "Detailed key point 1 — include context and explanation, not just a title",
    "Detailed key point 2 — include context and explanation, not just a title",
    "Detailed key point 3 — include context and explanation, not just a title",
    "Detailed key point 4 — include context and explanation, not just a title",
    "Detailed key point 5 — include context and explanation, not just a title",
    "Detailed key point 6 — include context and explanation, not just a title",
    "Detailed key point 7 — include context and explanation, not just a title",
    "Detailed key point 8 — include context and explanation, not just a title"
  ],
  "main_topics": ["topic1", "topic2", "topic3", "topic4", "topic5"],
  "detected_language": "language name in English",
  "content_type": "tutorial/lecture/conference/interview/other"
}}"""


def summarize_transcript(transcript_text: str, language: str) -> dict:
    client = get_bedrock_client()
    prompt = build_prompt(transcript_text, language)

    try:
        response = client.converse(
            modelId=MODEL_ID,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={
                "maxTokens": 2048,
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
            raise RuntimeError("Sin acceso a Bedrock. Verificá los permisos IAM.")
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