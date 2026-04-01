import json
import uuid
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from embeddings.embedder import get_embeddings
import os
from dotenv import load_dotenv

load_dotenv()

endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
key = os.getenv("AZURE_SEARCH_KEY")
index_name = "news-index"

client = SearchClient(endpoint, index_name, AzureKeyCredential(key))

# Load your FAISS metadata (reuse existing data)
with open("data/metadata.json") as f:
    data = json.load(f)

documents = []

for item in data:
    embedding = get_embeddings([item["content"]])[0]

    documents.append({
        "id": str(uuid.uuid4()),
        "title": item["title"],
        "content": item["content"],
        "published": item.get("published", ""),
        "contentVector": embedding.tolist()
    })

# Upload
client.upload_documents(documents)

print(f"Uploaded {len(documents)} documents")