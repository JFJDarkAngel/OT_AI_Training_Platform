from functools import lru_cache
from typing import Sequence

import numpy as np
from sentence_transformers import SentenceTransformer

from src.rag.document_loader import load_all_documents
from src.rag.text_splitter import create_document_chunks


EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Load the embedding model once and reuse it.

    The model converts text into numerical vectors
    that can later be stored in ChromaDB.
    """

    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    return model


def create_embeddings(
    texts: Sequence[str],
    batch_size: int = 32,
) -> np.ndarray:
    """
    Convert a collection of text strings into normalized embeddings.

    Args:
        texts:
            Text strings that will be converted into vectors.

        batch_size:
            Number of texts processed together.

    Returns:
        A NumPy array containing one embedding per text.
    """

    cleaned_texts = [
        str(text).strip()
        for text in texts
        if str(text).strip()
    ]

    if not cleaned_texts:
        raise ValueError(
            "No valid text was provided for embedding generation."
        )

    model = get_embedding_model()

    embeddings = model.encode(
        cleaned_texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    return embeddings


def create_query_embedding(query: str) -> list[float]:
    """
    Convert one search query into a normalized embedding.
    """

    cleaned_query = query.strip()

    if not cleaned_query:
        raise ValueError("Query cannot be empty.")

    embedding = create_embeddings(
        texts=[cleaned_query],
        batch_size=1,
    )[0]

    return embedding.tolist()


if __name__ == "__main__":
    print("Loading documents and creating chunks...")

    pages = load_all_documents()
    chunks = create_document_chunks(pages)

    # We only test the first five chunks here.
    # All chunks will be embedded when building ChromaDB.
    sample_chunks = chunks[:5]
    sample_texts = [
        chunk["text"]
        for chunk in sample_chunks
    ]

    print(
        f"\nGenerating embeddings for "
        f"{len(sample_texts)} sample chunks..."
    )

    sample_embeddings = create_embeddings(sample_texts)

    print("\nEmbedding test completed successfully.")
    print(f"Number of embeddings: {len(sample_embeddings)}")
    print(
        "Embedding dimensions: "
        f"{sample_embeddings.shape[1]}"
    )

    print("\nSample Chunk IDs:")

    for chunk in sample_chunks:
        print(chunk["chunk_id"])

    query = (
        "What should maintenance personnel do "
        "before restarting equipment?"
    )

    query_embedding = create_query_embedding(query)

    print("\nQuery embedding created successfully.")
    print(f"Query: {query}")
    print(
        "Query embedding dimensions: "
        f"{len(query_embedding)}"
    )