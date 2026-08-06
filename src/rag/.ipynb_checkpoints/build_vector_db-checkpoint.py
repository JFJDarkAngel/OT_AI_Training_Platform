from pathlib import Path
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection

from src.rag.document_loader import (
    load_all_documents,
)
from src.rag.embeddings import (
    EMBEDDING_MODEL_NAME,
    create_embeddings,
)
from src.rag.text_splitter import (
    create_document_chunks,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

VECTOR_DB_PATH = (
    PROJECT_ROOT
    / "vector_db"
)

COLLECTION_NAME = "ot_training_documents"

DATABASE_BATCH_SIZE = 100
EMBEDDING_BATCH_SIZE = 32


def get_chroma_client() -> chromadb.PersistentClient:
    """
    Create a persistent ChromaDB client.

    The database files are stored inside the vector_db folder.
    """

    VECTOR_DB_PATH.mkdir(
        parents=True,
        exist_ok=True,
    )

    return chromadb.PersistentClient(
        path=str(VECTOR_DB_PATH)
    )


def create_collection(
    rebuild: bool = False,
) -> Collection:
    """
    Create or retrieve the OT documents collection.

    Args:
        rebuild:
            Delete the existing collection before creating it again.
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

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={
            "description": (
                "OT incident-response training documents"
            ),
            "embedding_model": EMBEDDING_MODEL_NAME,
        },
    )


def prepare_metadata(
    chunk: dict[str, Any],
) -> dict[str, Any]:
    """
    Prepare one chunk's metadata for ChromaDB.

    Chroma metadata values must use simple data types.
    """

    required_fields = {
        "document_id",
        "file_name",
        "title",
        "page_number",
        "chunk_number",
        "maintenance",
        "operations",
        "production",
        "ot_cybersecurity",
    }

    missing_fields = (
        required_fields
        - set(chunk)
    )

    if missing_fields:
        raise ValueError(
            "Chunk metadata is missing fields: "
            f"{sorted(missing_fields)}"
        )

    return {
        "document_id": str(
            chunk["document_id"]
        ),
        "file_name": str(
            chunk["file_name"]
        ),
        "title": str(
            chunk["title"]
        ),
        "page_number": int(
            chunk["page_number"]
        ),
        "chunk_number": int(
            chunk["chunk_number"]
        ),
        "maintenance": str(
            chunk["maintenance"]
        ),
        "operations": str(
            chunk["operations"]
        ),
        "production": str(
            chunk["production"]
        ),
        "ot_cybersecurity": str(
            chunk["ot_cybersecurity"]
        ),
    }


def validate_chunks(
    chunks: list[dict[str, Any]],
) -> None:
    """
    Validate chunk IDs and text before database storage.
    """

    if not chunks:
        raise ValueError(
            "No document chunks were provided."
        )

    chunk_ids: list[str] = []

    for index, chunk in enumerate(
        chunks
    ):
        chunk_id = str(
            chunk.get(
                "chunk_id",
                "",
            )
        ).strip()

        chunk_text = str(
            chunk.get(
                "text",
                "",
            )
        ).strip()

        if not chunk_id:
            raise ValueError(
                "Chunk ID cannot be empty "
                f"at index {index}."
            )

        if not chunk_text:
            raise ValueError(
                "Chunk text cannot be empty "
                f"at index {index}."
            )

        chunk_ids.append(
            chunk_id
        )

    duplicate_ids = {
        chunk_id
        for chunk_id in chunk_ids
        if chunk_ids.count(
            chunk_id
        ) > 1
    }

    if duplicate_ids:
        raise ValueError(
            "Duplicate chunk IDs were found: "
            f"{sorted(duplicate_ids)}"
        )


def store_chunks_in_batches(
    collection: Collection,
    chunks: list[dict[str, Any]],
    verbose: bool = False,
) -> None:
    """
    Generate embeddings and store all chunks in batches.
    """

    validate_chunks(
        chunks
    )

    total_chunks = len(
        chunks
    )

    for batch_start in range(
        0,
        total_chunks,
        DATABASE_BATCH_SIZE,
    ):
        batch_end = min(
            batch_start
            + DATABASE_BATCH_SIZE,
            total_chunks,
        )

        batch_chunks = chunks[
            batch_start:batch_end
        ]

        batch_ids = [
            str(
                chunk["chunk_id"]
            )
            for chunk in batch_chunks
        ]

        batch_documents = [
            str(
                chunk["text"]
            ).strip()
            for chunk in batch_chunks
        ]

        batch_metadatas = [
            prepare_metadata(
                chunk
            )
            for chunk in batch_chunks
        ]

        batch_embeddings = create_embeddings(
            texts=batch_documents,
            batch_size=EMBEDDING_BATCH_SIZE,
            show_progress=verbose,
        )

        collection.upsert(
            ids=batch_ids,
            documents=batch_documents,
            metadatas=batch_metadatas,
            embeddings=(
                batch_embeddings.tolist()
            ),
        )

        if verbose:
            print(
                f"Stored chunks "
                f"{batch_start + 1} "
                f"to {batch_end} "
                f"of {total_chunks}"
            )


def build_vector_database(
    rebuild: bool = True,
    verbose: bool = True,
) -> Collection:
    """
    Build the complete ChromaDB vector database.
    """

    if DATABASE_BATCH_SIZE <= 0:
        raise ValueError(
            "DATABASE_BATCH_SIZE must be greater than zero."
        )

    if EMBEDDING_BATCH_SIZE <= 0:
        raise ValueError(
            "EMBEDDING_BATCH_SIZE must be greater than zero."
        )

    if verbose:
        print(
            "Loading PDF documents..."
        )

    pages = load_all_documents(
        verbose=verbose
    )

    if not pages:
        raise ValueError(
            "No PDF pages were extracted."
        )

    if verbose:
        print(
            "\nCreating document chunks..."
        )

    chunks = create_document_chunks(
        pages=pages
    )

    if not chunks:
        raise ValueError(
            "No document chunks were generated."
        )

    if verbose:
        print(
            f"Total pages: {len(pages)}"
        )
        print(
            f"Total chunks: {len(chunks)}"
        )
        print(
            "\nCreating ChromaDB collection..."
        )

    collection = create_collection(
        rebuild=rebuild
    )

    if verbose:
        print(
            "\nCreating embeddings "
            "and storing chunks..."
        )

    store_chunks_in_batches(
        collection=collection,
        chunks=chunks,
        verbose=verbose,
    )

    stored_count = collection.count()

    if stored_count != len(chunks):
        raise ValueError(
            "Stored record count does not match "
            "the generated chunk count. "
            f"Expected {len(chunks)}, "
            f"stored {stored_count}."
        )

    if verbose:
        print(
            "\nVector database built successfully."
        )
        print(
            f"Collection: {COLLECTION_NAME}"
        )
        print(
            f"Stored records: {stored_count}"
        )
        print(
            f"Database path: {VECTOR_DB_PATH}"
        )

    return collection


if __name__ == "__main__":
    build_vector_database(
        rebuild=True,
        verbose=True,
    )