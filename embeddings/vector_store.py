import faiss
import numpy as np
import json

class VectorStore:
    def __init__(self, dim):
        self.index = faiss.IndexFlatL2(dim)
        self.metadata = []

    def add(self, embeddings, metadata):
        self.index.add(np.array(embeddings).astype("float32"))
        self.metadata.extend(metadata)

    def save(self):
        faiss.write_index(self.index, "data/faiss.index")
        with open("data/metadata.json", "w") as f:
            json.dump(self.metadata, f)

    def load(self):
        self.index = faiss.read_index("data/faiss.index")
        with open("data/metadata.json") as f:
            self.metadata = json.load(f)