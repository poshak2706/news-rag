from fastapi import FastAPI
from pydantic import BaseModel

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


# Health check
@app.get("/")
def root():
    return {"message": "News RAG API is running"}


# Main endpoint
@app.post("/query")
def query_news(request: QueryRequest):
    query = request.query.strip()

    if not query:
        return {"error": "Empty query"}

    # Retrieval
    results = search(query, store)

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