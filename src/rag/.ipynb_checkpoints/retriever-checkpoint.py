from pathlib import Path
from typing import Any

import chromadb

from src.rag.build_vector_db import COLLECTION_NAME
from src.rag.embeddings import create_query_embedding


PROJECT_ROOT = Path(__file__).resolve().parents[2]
VECTOR_DB_PATH = PROJECT_ROOT / "vector_db"

ALLOWED_STAKEHOLDERS = {
    "maintenance",
    "operations",
    "production",
    "ot_cybersecurity",
}


def get_collection():
    """
    Connect to the saved ChromaDB collection.
    """

    if not VECTOR_DB_PATH.exists():
        raise FileNotFoundError(
            f"Vector database folder was not found: {VECTOR_DB_PATH}"
        )

    client = chromadb.PersistentClient(
        path=str(VECTOR_DB_PATH)
    )

    collection = client.get_collection(
        name=COLLECTION_NAME
    )

    return collection


def retrieve_relevant_chunks(
    query: str,
    stakeholder: str,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """
    Retrieve document chunks relevant to a query and stakeholder.

    Only documents classified as direct or supporting
    for the selected stakeholder are searched.
    """

    cleaned_query = query.strip()
    cleaned_stakeholder = stakeholder.strip().lower()

    if not cleaned_query:
        raise ValueError("Query cannot be empty.")

    if cleaned_stakeholder not in ALLOWED_STAKEHOLDERS:
        raise ValueError(
            f"Invalid stakeholder: {stakeholder}. "
            f"Allowed stakeholders: "
            f"{sorted(ALLOWED_STAKEHOLDERS)}"
        )

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    collection = get_collection()

    query_embedding = create_query_embedding(
        cleaned_query
    )

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={
            cleaned_stakeholder: {
                "$in": ["direct", "supporting"]
            }
        },
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    retrieved_chunks = []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    ids = results.get("ids", [[]])[0]

    for chunk_id, document, metadata, distance in zip(
        ids,
        documents,
        metadatas,
        distances,
    ):
        retrieved_chunks.append(
            {
                "chunk_id": chunk_id,
                "text": document,
                "metadata": metadata,
                "distance": float(distance),
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

    print("\n" + "=" * 70)
    print("RETRIEVAL RESULTS")
    print("=" * 70)

    print(f"Stakeholder: {stakeholder}")
    print(f"Query: {query}")
    print(f"Results returned: {len(results)}")

    for index, result in enumerate(results, start=1):
        metadata = result["metadata"]

        print("\n" + "-" * 70)
        print(f"Result {index}")
        print(f"Chunk ID: {result['chunk_id']}")
        print(f"Document: {metadata.get('title')}")
        print(f"File: {metadata.get('file_name')}")
        print(f"Page: {metadata.get('page_number')}")
        print(
            "Classification: "
            f"{metadata.get(stakeholder)}"
        )
        print(f"Distance: {result['distance']:.4f}")

        print("\nText:")
        print(result["text"][:700])


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
        top_k=5,
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
            stakeholder=test_case["stakeholder"],
        )