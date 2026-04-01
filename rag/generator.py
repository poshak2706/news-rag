import os
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def generate_answer(query, retrieved_chunks):
    if not retrieved_chunks:
        return f"""
No strongly relevant news found for query: "{query}"

Try more specific queries like:
- Ukraine war
- Iran Israel conflict
"""

    context = "\n\n".join([
        f"Title: {c['title']}\nContent: {c['content']}"
        for c in retrieved_chunks
    ])

    prompt = f"""
You are a real-time news analyst.

Query: {query}

Context:
{context}

Instructions:
- Only include directly relevant developments
- Ignore weak or unrelated information
- Focus on latest events
- Be precise

Output:
1. Key Developments
2. Brief Summary
"""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            print(f"Retry {attempt+1}: {e}")
            time.sleep(2)

    return "⚠️ LLM request failed"