"""
Lambda handler principal — orquesta el flujo completo:
1. Recibe URL de YouTube via API Gateway
2. Extrae transcript
3. Llama a Bedrock para resumir
4. Guarda en DynamoDB
5. Retorna resumen al frontend
"""

import json
import os
import uuid
from datetime import datetime, timezone, timedelta

import boto3

from transcript import get_transcript, extract_video_id
from bedrock_client import summarize_transcript


# Variables de entorno (configuradas en Terraform)
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE", "yt-summarizer-dev-summaries")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)


def build_response(status_code: int, body: dict) -> dict:
    """Construye respuesta HTTP con headers CORS para el frontend."""
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


def save_to_dynamodb(video_id: str, summary: dict, transcript_meta: dict) -> str:
    """Guarda el resumen en DynamoDB. Retorna el createdAt para el response."""
    table = dynamodb.Table(DYNAMODB_TABLE)
    created_at = datetime.now(timezone.utc).isoformat()

    # TTL: 90 días desde ahora (epoch timestamp)
    expires_at = int(
        (datetime.now(timezone.utc) + timedelta(days=90)).timestamp()
    )

    item = {
        "videoId": video_id,
        "createdAt": created_at,
        "expiresAt": expires_at,
        "language": transcript_meta.get("language_code", "unknown"),
        "isGenerated": transcript_meta.get("is_generated", True),
        "durationSeconds": transcript_meta.get("duration_seconds", 0),
        "summary": {
            "executiveSummary": summary.get("executive_summary", ""),
            "keyPoints": summary.get("key_points", []),
            "mainTopics": summary.get("main_topics", []),
            "detectedLanguage": summary.get("detected_language", ""),
            "contentType": summary.get("content_type", "other"),
        },
        "usage": summary.get("_usage", {}),
    }

    table.put_item(Item=item)
    return created_at


def lambda_handler(event, context):
    """
    Entry point de la Lambda.

    Espera un body JSON con:
    { "url": "https://www.youtube.com/watch?v=..." }
    """
    # Manejar preflight CORS (OPTIONS)
    if event.get("httpMethod") == "OPTIONS":
        return build_response(200, {})

    try:
        # Parsear body
        body = json.loads(event.get("body", "{}"))
        url = body.get("url", "").strip()

        if not url:
            return build_response(400, {
                "error": "URL requerida",
                "message": "Enviá un body JSON con el campo 'url'"
            })

        # 1. Extraer videoId
        video_id = extract_video_id(url)

        # 2. Verificar si ya existe en DynamoDB (cache)
        table = dynamodb.Table(DYNAMODB_TABLE)
        existing = table.query(
            KeyConditionExpression="videoId = :vid",
            ExpressionAttributeValues={":vid": video_id},
            ScanIndexForward=False,  # Más reciente primero
            Limit=1,
        )

        if existing.get("Items"):
            cached = existing["Items"][0]
            return build_response(200, {
                "videoId": video_id,
                "cached": True,
                "createdAt": cached["createdAt"],
                "language": cached.get("language"),
                "summary": cached["summary"],
            })

        # 3. Extraer transcript
        transcript_data = get_transcript(video_id)

        # 4. Llamar a Bedrock
        summary = summarize_transcript(
            transcript_data["text"],
            transcript_data["language"]
        )

        # 5. Guardar en DynamoDB
        created_at = save_to_dynamodb(video_id, summary, transcript_data)

        # 6. Retornar respuesta
        return build_response(200, {
            "videoId": video_id,
            "cached": False,
            "createdAt": created_at,
            "language": transcript_data["language_code"],
            "durationSeconds": transcript_data["duration_seconds"],
            "summary": {
                "executiveSummary": summary.get("executive_summary", ""),
                "keyPoints": summary.get("key_points", []),
                "mainTopics": summary.get("main_topics", []),
                "detectedLanguage": summary.get("detected_language", ""),
                "contentType": summary.get("content_type", "other"),
            },
        })

    except ValueError as e:
        # Errores esperados: URL inválida, sin subtítulos, video privado
        return build_response(422, {
            "error": "Contenido no procesable",
            "message": str(e)
        })

    except Exception as e:
        # Error inesperado — loggear para CloudWatch
        print(f"ERROR: {type(e).__name__}: {str(e)}")
        return build_response(500, {
            "error": "Error interno",
            "message": "Ocurrió un error procesando el video. Intentá nuevamente."
        })