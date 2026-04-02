from embeddings.azure_retriever import search_azure


class VectorStore:
    def __init__(self):
        pass

    def load(self):
        # No local index to load anymore
        # Azure Search handles everything
        print("Using Azure Search as vector store")

    def add(self, embeddings, metadata):
        # Not needed because ingestion pipeline directly uploads to Azure Search
        pass

    def save(self):
        # No local persistence needed
        pass

    def query(self, query):
        results = search_azure(query)
        return results