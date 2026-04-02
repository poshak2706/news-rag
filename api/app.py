from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from embeddings.vector_store import VectorStore
from embeddings.azure_retriever import search_azure as search
from rag.generator import generate_answer


app = FastAPI(title="News RAG API")

# Load vector store once at startup
store = VectorStore(dim=768)
store.load()


# Request schema
class QueryRequest(BaseModel):
    query: str




# Main endpoint
@app.post("/query")
def query_news(request: QueryRequest):
    query = request.query.strip()

    if not query:
        return {"error": "Empty query"}

    # Retrieval
    results = search(query)

    if not results:
        return {
            "query": query,
            "answer": "No relevant news found",
            "sources": []
        }

    # Generation
    answer = generate_answer(query, results)

    # Return sources (important for frontend)
    sources = list(set([r["title"] for r in results]))

    return {
        "query": query,
        "answer": answer,
        "sources": sources
    }


@app.get("/", response_class=HTMLResponse)
def ui():
    return """
    <html>
    <head>
        <title>News RAG</title>
    </head>
    <body>
        <h2>News RAG Chat</h2>
        <input id="query" placeholder="Ask something..." size="50"/>
        <button onclick="sendQuery()">Ask</button>
        <pre id="response"></pre>

        <script>
        async function sendQuery() {
            const q = document.getElementById("query").value;
            const res = await fetch("/query", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({query: q})
            });
            const data = await res.json();
            document.getElementById("response").innerText = data.answer;
        }
        </script>
    </body>
    </html>
    """