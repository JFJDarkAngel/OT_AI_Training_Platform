from pathlib import Path
from typing import Any

import chromadb

from src.rag.build_vector_db import (
    COLLECTION_NAME,
)
from src.rag.embeddings import (
    create_query_embedding,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

VECTOR_DB_PATH = (
    PROJECT_ROOT
    / "vector_db"
)


ALLOWED_STAKEHOLDERS = {
    "maintenance",
    "operations",
    "production",
    "ot_cybersecurity",
}


DEFAULT_TOP_K = 5
MAX_TOP_K = 20


def get_collection():
    """
    Connect to the saved ChromaDB collection.
    """

    if not VECTOR_DB_PATH.exists():
        raise FileNotFoundError(
            "Vector database folder was not found: "
            f"{VECTOR_DB_PATH}"
        )

    client = chromadb.PersistentClient(
        path=str(VECTOR_DB_PATH)
    )

    try:
        collection = client.get_collection(
            name=COLLECTION_NAME
        )

    except Exception as error:
        raise ValueError(
            "ChromaDB collection was not found: "
            f"{COLLECTION_NAME}. "
            "Build the vector database first."
        ) from error

    if collection.count() == 0:
        raise ValueError(
            "The ChromaDB collection is empty."
        )

    return collection


def validate_stakeholder(
    stakeholder: str,
) -> str:
    """
    Validate and normalize a stakeholder name.
    """

    cleaned_stakeholder = (
        stakeholder.strip().lower()
    )

    if not cleaned_stakeholder:
        raise ValueError(
            "Stakeholder cannot be empty."
        )

    if (
        cleaned_stakeholder
        not in ALLOWED_STAKEHOLDERS
    ):
        raise ValueError(
            "Invalid stakeholder: "
            f"{cleaned_stakeholder}. "
            "Allowed stakeholders: "
            f"{sorted(ALLOWED_STAKEHOLDERS)}"
        )

    return cleaned_stakeholder


def retrieve_relevant_chunks(
    query: str,
    stakeholder: str,
    top_k: int = DEFAULT_TOP_K,
) -> list[dict[str, Any]]:
    """
    Retrieve document chunks relevant to a query and stakeholder.

    Only documents classified as direct or supporting
    for the selected stakeholder are searched.
    """

    cleaned_query = query.strip()

    if not cleaned_query:
        raise ValueError(
            "Query cannot be empty."
        )

    cleaned_stakeholder = validate_stakeholder(
        stakeholder
    )

    if top_k <= 0:
        raise ValueError(
            "top_k must be greater than zero."
        )

    if top_k > MAX_TOP_K:
        raise ValueError(
            f"top_k cannot exceed {MAX_TOP_K}."
        )

    collection = get_collection()

    available_records = collection.count()

    requested_results = min(
        top_k,
        available_records,
    )

    query_embedding = create_query_embedding(
        cleaned_query
    )

    results = collection.query(
        query_embeddings=[
            query_embedding
        ],
        n_results=requested_results,
        where={
            cleaned_stakeholder: {
                "$in": [
                    "direct",
                    "supporting",
                ]
            }
        },
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    ids_groups = results.get(
        "ids"
    ) or [[]]

    document_groups = results.get(
        "documents"
    ) or [[]]

    metadata_groups = results.get(
        "metadatas"
    ) or [[]]

    distance_groups = results.get(
        "distances"
    ) or [[]]

    ids = (
        ids_groups[0]
        if ids_groups
        else []
    )

    documents = (
        document_groups[0]
        if document_groups
        else []
    )

    metadatas = (
        metadata_groups[0]
        if metadata_groups
        else []
    )

    distances = (
        distance_groups[0]
        if distance_groups
        else []
    )

    result_count = min(
        len(ids),
        len(documents),
        len(metadatas),
        len(distances),
    )

    retrieved_chunks: list[
        dict[str, Any]
    ] = []

    for index in range(
        result_count
    ):
        chunk_id = str(
            ids[index]
        )

        document = (
            documents[index]
            or ""
        )

        metadata = (
            metadatas[index]
            or {}
        )

        distance = distances[index]

        cleaned_document = str(
            document
        ).strip()

        if not chunk_id:
            continue

        if not cleaned_document:
            continue

        try:
            cleaned_distance = float(
                distance
            )

        except (
            TypeError,
            ValueError,
        ):
            continue

        retrieved_chunks.append(
            {
                "chunk_id": chunk_id,
                "text": cleaned_document,
                "metadata": dict(
                    metadata
                ),
                "distance": (
                    cleaned_distance
                ),
            }
        )

    return retrieved_chunks


def print_retrieval_results(
    query: str,
    stakeholder: str,
    results: list[dict[str, Any]],
) -> None:
    """
    Print retrieved chunks in a readable format.
    """

    cleaned_stakeholder = validate_stakeholder(
        stakeholder
    )

    print("\n" + "=" * 70)
    print("RETRIEVAL RESULTS")
    print("=" * 70)

    print(
        f"Stakeholder: {cleaned_stakeholder}"
    )

    print(
        f"Query: {query.strip()}"
    )

    print(
        f"Results returned: {len(results)}"
    )

    for index, result in enumerate(
        results,
        start=1,
    ):
        metadata = (
            result.get("metadata")
            or {}
        )

        print("\n" + "-" * 70)
        print(
            f"Result {index}"
        )
        print(
            "Chunk ID: "
            f"{result.get('chunk_id')}"
        )
        print(
            "Document: "
            f"{metadata.get('title')}"
        )
        print(
            "File: "
            f"{metadata.get('file_name')}"
        )
        print(
            "Page: "
            f"{metadata.get('page_number')}"
        )
        print(
            "Classification: "
            f"{metadata.get(cleaned_stakeholder)}"
        )
        print(
            "Distance: "
            f"{float(result.get('distance', 0.0)):.4f}"
        )

        print("\nText:")
        print(
            str(
                result.get(
                    "text",
                    "",
                )
            )[:700]
        )


def run_test(
    query: str,
    stakeholder: str,
) -> None:
    """
    Run one retrieval test and print the results.
    """

    results = retrieve_relevant_chunks(
        query=query,
        stakeholder=stakeholder,
        top_k=DEFAULT_TOP_K,
    )

    print_retrieval_results(
        query=query,
        stakeholder=stakeholder,
        results=results,
    )


if __name__ == "__main__":
    test_cases = [
        {
            "stakeholder": "maintenance",
            "query": (
                "What should maintenance personnel inspect "
                "and verify before restarting equipment "
                "after an incident?"
            ),
        },
        {
            "stakeholder": "operations",
            "query": (
                "What should operations personnel do when "
                "abnormal process conditions are detected?"
            ),
        },
        {
            "stakeholder": "production",
            "query": (
                "How should production personnel assess impact "
                "and prioritize the return to production?"
            ),
        },
        {
            "stakeholder": "ot_cybersecurity",
            "query": (
                "What actions should be taken to isolate affected "
                "industrial control assets and preserve evidence?"
            ),
        },
    ]

    for test_case in test_cases:
        run_test(
            query=test_case["query"],
            stakeholder=test_case[
                "stakeholder"
            ],
        )