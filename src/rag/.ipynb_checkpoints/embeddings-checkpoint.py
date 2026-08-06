from functools import lru_cache
from typing import Sequence

import numpy as np
from sentence_transformers import SentenceTransformer

from src.rag.document_loader import load_all_documents
from src.rag.text_splitter import create_document_chunks


EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"

DEFAULT_BATCH_SIZE = 32


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Load and reuse the embedding model.

    The model converts text into normalized numerical vectors
    for storage and retrieval through ChromaDB.
    """

    return SentenceTransformer(
        EMBEDDING_MODEL_NAME
    )


def validate_texts(
    texts: Sequence[str],
) -> list[str]:
    """
    Validate and normalize texts before embedding generation.

    One valid text must exist for every expected embedding.
    """

    if isinstance(
        texts,
        (str, bytes),
    ):
        raise TypeError(
            "texts must be a sequence of strings, "
            "not one string."
        )

    normalized_texts = [
        str(text).strip()
        for text in texts
    ]

    if not normalized_texts:
        raise ValueError(
            "No text was provided for embedding generation."
        )

    empty_indexes = [
        index
        for index, text in enumerate(
            normalized_texts
        )
        if not text
    ]

    if empty_indexes:
        raise ValueError(
            "Empty text values were found at indexes: "
            f"{empty_indexes}"
        )

    return normalized_texts


def create_embeddings(
    texts: Sequence[str],
    batch_size: int = DEFAULT_BATCH_SIZE,
    show_progress: bool = False,
) -> np.ndarray:
    """
    Convert text strings into normalized embeddings.

    Args:
        texts:
            Text strings that will be converted into vectors.

        batch_size:
            Number of texts processed in one model batch.

        show_progress:
            Display the embedding progress bar when True.

    Returns:
        A two-dimensional NumPy array containing one embedding
        for every supplied text.
    """

    if batch_size <= 0:
        raise ValueError(
            "batch_size must be greater than zero."
        )

    cleaned_texts = validate_texts(
        texts
    )

    model = get_embedding_model()

    embeddings = model.encode(
        cleaned_texts,
        batch_size=batch_size,
        show_progress_bar=show_progress,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    embeddings_array = np.asarray(
        embeddings,
        dtype=np.float32,
    )

    if embeddings_array.ndim != 2:
        raise ValueError(
            "The embedding model returned an invalid "
            "array shape."
        )

    if (
        embeddings_array.shape[0]
        != len(cleaned_texts)
    ):
        raise ValueError(
            "The number of generated embeddings does not "
            "match the number of supplied texts."
        )

    if not np.isfinite(
        embeddings_array
    ).all():
        raise ValueError(
            "The generated embeddings contain "
            "non-finite values."
        )

    return embeddings_array


def create_query_embedding(
    query: str,
) -> list[float]:
    """
    Convert one search query into a normalized embedding.
    """

    cleaned_query = query.strip()

    if not cleaned_query:
        raise ValueError(
            "Query cannot be empty."
        )

    embeddings = create_embeddings(
        texts=[cleaned_query],
        batch_size=1,
        show_progress=False,
    )

    return embeddings[0].tolist()


if __name__ == "__main__":
    print(
        "Loading documents and creating chunks..."
    )

    pages = load_all_documents(
        verbose=True
    )

    chunks = create_document_chunks(
        pages=pages
    )

    if not chunks:
        raise ValueError(
            "No document chunks were generated."
        )

    sample_chunks = chunks[:5]

    sample_texts = [
        str(chunk["text"])
        for chunk in sample_chunks
    ]

    print(
        "\nGenerating embeddings for "
        f"{len(sample_texts)} sample chunks..."
    )

    sample_embeddings = create_embeddings(
        texts=sample_texts,
        show_progress=True,
    )

    print(
        "\nEmbedding test completed successfully."
    )

    print(
        "Number of embeddings: "
        f"{sample_embeddings.shape[0]}"
    )

    print(
        "Embedding dimensions: "
        f"{sample_embeddings.shape[1]}"
    )

    print("\nSample Chunk IDs:")

    for chunk in sample_chunks:
        print(
            chunk["chunk_id"]
        )

    query = (
        "What should maintenance personnel do "
        "before restarting equipment?"
    )

    query_embedding = create_query_embedding(
        query
    )

    print(
        "\nQuery embedding created successfully."
    )

    print(
        f"Query: {query}"
    )

    print(
        "Query embedding dimensions: "
        f"{len(query_embedding)}"
    )