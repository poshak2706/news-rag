from google import genai
from google.genai import types
import os

def get_client():
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("API key missing")

    return genai.Client(api_key=api_key)

def get_embeddings(texts):
    client=get_client()
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=texts,
        config=types.EmbedContentConfig(output_dimensionality=768)
    )

    return [e.values for e in response.embeddings]