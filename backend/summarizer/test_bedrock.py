import sys
sys.path.insert(0, ".")

from transcript import extract_video_id, get_transcript
from bedrock_client import summarize_transcript

url = "https://www.youtube.com/watch?v=arj7oStGLkU"
video_id = extract_video_id(url)
print(f"Obteniendo transcript de: {video_id}")

transcript = get_transcript(video_id)
print(f"Transcript obtenido: {len(transcript['text'])} caracteres")
print("Llamando a Bedrock (Claude Haiku)...")

summary = summarize_transcript(transcript["text"], transcript["language"])

print("\n===== RESUMEN =====")
print(f"Resumen ejecutivo: {summary['executive_summary']}")
print(f"\nPuntos clave:")
for i, point in enumerate(summary["key_points"], 1):
    print(f"  {i}. {point}")
print(f"\nTopicos: {summary['main_topics']}")
print(f"Tipo de contenido: {summary['content_type']}")
print(f"\nTokens usados - Input: {summary['_usage'].get('input_tokens')}, Output: {summary['_usage'].get('output_tokens')}")