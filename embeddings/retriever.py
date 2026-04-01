import numpy as np
from collections import defaultdict
from datetime import datetime
from embeddings.embedder import get_embeddings


def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z")
    except:
        return datetime.min


def search(query, vector_store, k=15, threshold=1.3, max_chunks=8):
    query_embedding = get_embeddings([query])

    distances, indices = vector_store.index.search(
        np.array(query_embedding).astype("float32"), k
    )

    candidates = []

    # Step 1: filter by threshold
    for i, idx in enumerate(indices[0]):
        dist = distances[0][i]
        if dist < threshold:
            candidates.append((dist, vector_store.metadata[idx]))

    if not candidates:
        return []

    # Step 2: group by title
    grouped = defaultdict(list)
    for dist, item in candidates:
        grouped[item["title"]].append((dist, item))

    # Step 3: sort per article
    for title in grouped:
        grouped[title] = sorted(grouped[title], key=lambda x: x[0])

    selected = []

    # Step 4: best chunk per article
    for title in grouped:
        selected.append(grouped[title][0][1])

    # Step 5: add second-best chunks if space
    for title in grouped:
        if len(selected) >= max_chunks:
            break
        if len(grouped[title]) > 1:
            selected.append(grouped[title][1][1])

    # Step 6: recency sort if overflow
    if len(selected) > max_chunks:
        selected = sorted(
            selected,
            key=lambda x: parse_date(x.get("published", "")),
            reverse=True
        )

    return selected[:max_chunks]