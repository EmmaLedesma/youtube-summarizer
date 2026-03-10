from transcript import extract_video_id, get_transcript

# Video corto con subtítulos — charla TED
url = "https://www.youtube.com/watch?v=arj7oStGLkU"

video_id = extract_video_id(url)
print(f"videoId: {video_id}")

transcript = get_transcript(video_id)
print(f"Idioma: {transcript['language']} (generado: {transcript['is_generated']})")
print(f"Duración: {transcript['duration_seconds']}s")
print(f"Primeros 300 chars: {transcript['text'][:300]}")
