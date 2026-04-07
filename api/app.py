from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from embeddings.vector_store import VectorStore
from embeddings.azure_retriever import search_azure as search
from rag.generator import generate_answer
import os

def log(msg):
    print(msg)
    os.makedirs("/app/logs", exist_ok=True)

    with open("/app/logs/logs.txt", "a") as f:
        f.write(msg + "\n")
app = FastAPI(title="News RAG API")

# Request schema
class QueryRequest(BaseModel):
    query: str

@app.get("/", response_class=HTMLResponse)
def ui():
    log("Retrieved Basic UI")
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
        <h3>Pipeline Logs</h3>
        <pre id="logs"></pre>

        <script>
        async function fetchLogs() {
            const res = await fetch("/logs");
            const data = await res.json();
            document.getElementById("logs").innerText = data.logs;
        }

        setInterval(fetchLogs, 5000);
        </script>
    </body>
    </html>
    """


# Main endpoint
@app.post("/query")
def query_news(request: QueryRequest):
    query = request.query.strip()
    log("Query Recieved")

    if not query:
        log("Empty Query")
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
    log("Generated Response")

    return {
        "query": query,
        "answer": answer,
        "sources": sources
    }

@app.get("/logs")
def get_logs():
    try:
        with open("/app/logs/logs.txt", "r") as f:
            logs = f.read()
        return {"logs": logs}
    except:
        return {"logs": "No logs yet"}