from embeddings.vector_store import VectorStore
from embeddings.azure_retriever import search_azure as search
from rag.generator import generate_answer

print("News RAG Chatbot")
print("Type 'exit' to quit.\n")

while True:
    query = input("Enter your query: ").strip()

    # Exit condition
    if query.lower() == "exit":
        print("Exiting")
        break

    if not query:
        print("Enter a valid query.\n")
        continue

    # Retrieval
    results = search(query)

    # Generation
    answer = generate_answer(query, results)

    print("\n===== FINAL ANSWER =====\n")
    print(answer)
    print("\n" + "="*50 + "\n")