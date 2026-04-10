from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from embeddings.vector_store import VectorStore
from embeddings.azure_retriever import search_azure as search
from rag.generator import generate_answer
import os
import time
from datetime import datetime

CACHE = {}
CACHE_TTL = 600

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    line=f"[{timestamp}] {msg}"
    print(line)
    os.makedirs("/app/logs", exist_ok=True)

    with open("/app/logs/logs.txt", "a") as f:
        f.write(line + "\n")
app = FastAPI(title="News RAG API")

# Request schema
class QueryRequest(BaseModel):
    query: str

@app.get("/", response_class=HTMLResponse)
def ui():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>News RAG</title>
    </head>
    <body>
        <h2>News RAG Chat</h2>
        <input id="query" placeholder="Ask something..." size="50"/>
        <button onclick="sendQuery()">Ask</button>
        <pre id="response"></pre>
        <h3> Sources </h3>
        <ul id = "sources"></ul>
        <script>
        async function sendQuery() {
            const q = document.getElementById("query").value;
            const res = await fetch("/query", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({query: q})
            });

            const data = await res.json();

            let responseText = data.answer || "No answer";

            if (data.cached) {
                responseText = "[Cached]" + responseText;
            }

            document.getElementById("response").innerText = responseText;

            const sourcesList = document.getElementById("sources");
            sourcesList.innerHTML = "";

            if (data.sources && Array.isArray(data.sources)) {
                data.sources.forEach(src => {
                    const li = document.createElement("li");
                    li.innerHTML = `<b>${src.title}</b><br><small>${src.published})</small>`; 
                    sourcesList.appendChild(li);
                });
            } else {
                const li = document.createElement("li");
                li.innerText = "No sources available";
                sourcesList.appendChild(li);
        }
}
        
        </script>
        <h3>Pipeline Logs</h3>
        <button onclick="clearlogs()">Clear Logs</button>
        <script>
        async function clearlogs() {
            await fetch("/clear-logs", { method : "POST" });
            get_logs();
        }
        </script>
        <pre id="logs"></pre>

        <script>
        async function fetchLogs() {
            const res = await fetch("/logs");
            const data = await res.json();
            document.getElementById("logs").innerText = data.logs;
        }

        setInterval(fetchLogs, 1000);
        </script>
    </body>
    </html>
    """


@app.post("/query")
def query_news(request: QueryRequest):
    query = request.query.strip()
    log("Query Recieved")
    now = time.time()


    if not query:
        log("Empty Query")
        return {"error": "Empty query"}
    if query in CACHE:
        entry = CACHE[query]

        if now - entry["timestamp"] < CACHE_TTL:
            print("CACHE HIT")
            log("CACHE HIT")
            return {
                "query": query,
                "answer": entry["answer"],
                "sources": entry["sources"],
                "cached":True
            }
        else:
            print("CACHE EXPIRED")
            log("CACHE EXPIRED")
            del CACHE[query]

    print("CACHE MISS")
    log("CACHE MISS")

    results = search(query)

    if not results:
        return {
            "query": query,
            "answer": "No relevant news found",
            "sources": []
        }

    answer = generate_answer(query, results)

    sources = []
    for r in results:
        sources.append({"title": r.get("title", "No title"),
                        "published": r.get("published", "No date")})
    log("Generated Response")

    CACHE[query] = {
        "answer": answer,
        "sources":sources,
        "timestamp": now
    }

    return {
        "query": query,
        "answer": answer,
        "sources":sources,
        "cached": False
    }

@app.get("/logs")
def get_logs():
    try:
        with open("/app/logs/logs.txt", "r") as f:
            logs = f.read()
        return {"logs": logs}
    except:
        return {"logs": "No logs yet"}
    
@app.post("/clear-logs")
def clear_logs():
    try:
        open("/app/logs/logs.txt", "w").close()
        return {"status": "logs cleared"}
    except:
        return {"status": "error"}