from pathlib import Path
from typing import Any

import chromadb

from src.rag.document_loader import load_all_documents
from src.rag.embeddings import (
    EMBEDDING_MODEL_NAME,
    create_embeddings,
)
from src.rag.text_splitter import create_document_chunks


PROJECT_ROOT = Path(__file__).resolve().parents[2]

VECTOR_DB_PATH = PROJECT_ROOT / "vector_db"

COLLECTION_NAME = "ot_training_documents"

DATABASE_BATCH_SIZE = 100
EMBEDDING_BATCH_SIZE = 32


def get_chroma_client() -> chromadb.PersistentClient:
    """
    Create a persistent ChromaDB client.

    The database files are stored inside the vector_db folder.
    """

    VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)

    return chromadb.PersistentClient(
        path=str(VECTOR_DB_PATH)
    )


def create_collection(
    rebuild: bool = False,
):
    """
    Create or retrieve the OT documents collection.

    Args:
        rebuild:
            When True, delete the old collection and rebuild it.
    """

    client = get_chroma_client()

    if rebuild:
        existing_collection_names = {
            collection.name
            for collection in client.list_collections()
        }

        if COLLECTION_NAME in existing_collection_names:
            client.delete_collection(
                name=COLLECTION_NAME
            )

            print(
                f"Deleted old collection: {COLLECTION_NAME}"
            )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={
            "description": (
                "OT incident-response training documents"
            ),
            "embedding_model": EMBEDDING_MODEL_NAME,
        },
    )

    return collection


def prepare_metadata(chunk: dict[str, Any]) -> dict[str, Any]:
    """
    Prepare one chunk's metadata for ChromaDB.

    Chroma metadata values must be simple types such as
    strings, integers, floats, or booleans.
    """

    return {
        "document_id": str(chunk["document_id"]),
        "file_name": str(chunk["file_name"]),
        "title": str(chunk["title"]),
        "page_number": int(chunk["page_number"]),
        "chunk_number": int(chunk["chunk_number"]),
        "maintenance": str(chunk["maintenance"]),
        "operations": str(chunk["operations"]),
        "production": str(chunk["production"]),
        "ot_cybersecurity": str(
            chunk["ot_cybersecurity"]
        ),
    }


def store_chunks_in_batches(
    collection,
    chunks: list[dict],
) -> None:
    """
    Generate embeddings and store all chunks in batches.
    """

    total_chunks = len(chunks)

    if total_chunks == 0:
        raise ValueError(
            "No document chunks were provided."
        )

    for batch_start in range(
        0,
        total_chunks,
        DATABASE_BATCH_SIZE,
    ):
        batch_end = min(
            batch_start + DATABASE_BATCH_SIZE,
            total_chunks,
        )

        batch_chunks = chunks[batch_start:batch_end]

        batch_ids = [
            chunk["chunk_id"]
            for chunk in batch_chunks
        ]

        batch_documents = [
            chunk["text"]
            for chunk in batch_chunks
        ]

        batch_metadatas = [
            prepare_metadata(chunk)
            for chunk in batch_chunks
        ]

        batch_embeddings = create_embeddings(
            texts=batch_documents,
            batch_size=EMBEDDING_BATCH_SIZE,
        )

        collection.upsert(
            ids=batch_ids,
            documents=batch_documents,
            metadatas=batch_metadatas,
            embeddings=batch_embeddings.tolist(),
        )

        print(
            f"Stored chunks {batch_start + 1}"
            f" to {batch_end}"
            f" of {total_chunks}"
        )


def build_vector_database(
    rebuild: bool = True,
):
    """
    Build the complete ChromaDB vector database.
    """

    print("Loading PDF documents...")

    pages = load_all_documents()

    print("\nCreating document chunks...")

    chunks = create_document_chunks(pages)

    print(f"Total pages: {len(pages)}")
    print(f"Total chunks: {len(chunks)}")

    print("\nCreating ChromaDB collection...")

    collection = create_collection(
        rebuild=rebuild
    )

    print("\nCreating embeddings and storing chunks...")

    store_chunks_in_batches(
        collection=collection,
        chunks=chunks,
    )

    stored_count = collection.count()

    print("\nVector database built successfully.")
    print(f"Collection: {COLLECTION_NAME}")
    print(f"Stored records: {stored_count}")
    print(f"Database path: {VECTOR_DB_PATH}")

    return collection


if __name__ == "__main__":
    build_vector_database(rebuild=True)