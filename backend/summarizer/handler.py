"""
Lambda handler — recibe transcript desde el frontend y llama a Bedrock.
El frontend es responsable de extraer el transcript (evita bloqueo de IP).
"""

import json
import os
from datetime import datetime, timezone, timedelta

import boto3

from bedrock_client import summarize_transcript

DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE", "yt-summarizer-dev-summaries")
AWS_REGION = os.environ.get("AWS_REGION_NAME", "us-east-1")

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)


def build_response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
        },
        "body": json.dumps(body, ensure_ascii=False),
    }


def save_to_dynamodb(video_id: str, summary: dict, language: str) -> str:
    table = dynamodb.Table(DYNAMODB_TABLE)
    created_at = datetime.now(timezone.utc).isoformat()
    expires_at = int(
        (datetime.now(timezone.utc) + timedelta(days=90)).timestamp()
    )

    table.put_item(Item={
        "videoId": video_id,
        "createdAt": created_at,
        "expiresAt": expires_at,
        "language": language,
        "summary": {
            "executiveSummary": summary.get("executive_summary", ""),
            "keyPoints": summary.get("key_points", []),
            "mainTopics": summary.get("main_topics", []),
            "detectedLanguage": summary.get("detected_language", ""),
            "contentType": summary.get("content_type", "other"),
        },
        "usage": summary.get("_usage", {}),
    })
    return created_at


def lambda_handler(event, context):
    if event.get("httpMethod") == "OPTIONS":
        return build_response(200, {})

    try:
        body = json.loads(event.get("body", "{}"))
        video_id = body.get("videoId", "").strip()
        transcript_text = body.get("transcriptText", "").strip()
        language = body.get("language", "English")

        if not video_id:
            return build_response(400, {
                "error": "videoId requerido",
            })

        if not transcript_text:
            return build_response(400, {
                "error": "transcriptText requerido",
                "message": "El frontend debe enviar el transcript extraído."
            })

        # Verificar cache en DynamoDB
        table = dynamodb.Table(DYNAMODB_TABLE)
        existing = table.query(
            KeyConditionExpression="videoId = :vid",
            ExpressionAttributeValues={":vid": video_id},
            ScanIndexForward=False,
            Limit=1,
        )

        if existing.get("Items"):
            cached = existing["Items"][0]
            return build_response(200, {
                "videoId": video_id,
                "cached": True,
                "createdAt": cached["createdAt"],
                "summary": cached["summary"],
            })

        # Llamar a Bedrock
        summary = summarize_transcript(transcript_text, language)

        # Guardar en DynamoDB
        created_at = save_to_dynamodb(video_id, summary, language)

        return build_response(200, {
            "videoId": video_id,
            "cached": False,
            "createdAt": created_at,
            "summary": {
                "executiveSummary": summary.get("executive_summary", ""),
                "keyPoints": summary.get("key_points", []),
                "mainTopics": summary.get("main_topics", []),
                "detectedLanguage": summary.get("detected_language", ""),
                "contentType": summary.get("content_type", "other"),
            },
        })

    except ValueError as e:
        return build_response(422, {
            "error": "Contenido no procesable",
            "message": str(e)
        })

    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {str(e)}")
        return build_response(500, {
            "error": "Error interno",
            "message": "Ocurrió un error procesando el video."
        })