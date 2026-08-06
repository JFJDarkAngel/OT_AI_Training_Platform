from typing import Any

from src.rag.document_loader import (
    load_all_documents,
)


DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200


def validate_chunk_settings(
    chunk_size: int,
    chunk_overlap: int,
) -> None:
    """
    Validate text chunking settings.
    """

    if chunk_size <= 0:
        raise ValueError(
            "chunk_size must be greater than zero."
        )

    if chunk_overlap < 0:
        raise ValueError(
            "chunk_overlap cannot be negative."
        )

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller "
            "than chunk_size."
        )


def normalize_text(
    text: str,
) -> str:
    """
    Normalize whitespace while preserving readable text.
    """

    if not isinstance(text, str):
        raise TypeError(
            "Text must be a string."
        )

    return " ".join(
        text.split()
    ).strip()


def find_chunk_end(
    text: str,
    start: int,
    proposed_end: int,
) -> int:
    """
    Find a readable ending point near the proposed chunk end.

    Preference order:
    - paragraph or sentence boundary
    - whitespace boundary
    - proposed character boundary
    """

    if proposed_end >= len(text):
        return len(text)

    minimum_end = start + (
        proposed_end - start
    ) // 2

    sentence_boundaries = (
        ". ",
        "! ",
        "? ",
        "; ",
        ": ",
    )

    best_boundary = -1

    for boundary in sentence_boundaries:
        boundary_index = text.rfind(
            boundary,
            minimum_end,
            proposed_end,
        )

        if boundary_index > best_boundary:
            best_boundary = (
                boundary_index
                + len(boundary)
                - 1
            )

    if best_boundary > start:
        return best_boundary + 1

    whitespace_index = text.rfind(
        " ",
        minimum_end,
        proposed_end,
    )

    if whitespace_index > start:
        return whitespace_index

    return proposed_end


def split_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    """
    Split text into readable overlapping chunks.

    Chunk endings prefer sentence or whitespace boundaries
    instead of cutting words in the middle.
    """

    validate_chunk_settings(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    cleaned_text = normalize_text(
        text
    )

    if not cleaned_text:
        return []

    chunks: list[str] = []

    start = 0
    text_length = len(
        cleaned_text
    )

    while start < text_length:
        proposed_end = min(
            start + chunk_size,
            text_length,
        )

        end = find_chunk_end(
            text=cleaned_text,
            start=start,
            proposed_end=proposed_end,
        )

        chunk = cleaned_text[
            start:end
        ].strip()

        if chunk:
            chunks.append(
                chunk
            )

        if end >= text_length:
            break

        next_start = end - chunk_overlap

        if next_start <= start:
            next_start = end

        start = next_start

    return chunks


def validate_page_record(
    page: dict[str, Any],
) -> None:
    """
    Validate one extracted PDF page record.
    """

    required_fields = {
        "document_id",
        "file_name",
        "title",
        "page_number",
        "text",
        "maintenance",
        "operations",
        "production",
        "ot_cybersecurity",
    }

    missing_fields = (
        required_fields
        - set(page)
    )

    if missing_fields:
        raise ValueError(
            "Page record is missing fields: "
            f"{sorted(missing_fields)}"
        )

    if not str(
        page["document_id"]
    ).strip():
        raise ValueError(
            "Page document_id cannot be empty."
        )

    if not str(
        page["text"]
    ).strip():
        raise ValueError(
            "Page text cannot be empty."
        )

    try:
        page_number = int(
            page["page_number"]
        )

    except (
        TypeError,
        ValueError,
    ) as error:
        raise ValueError(
            "Page number must be an integer."
        ) from error

    if page_number < 1:
        raise ValueError(
            "Page number must be greater than zero."
        )


def create_document_chunks(
    pages: list[dict[str, Any]],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[dict[str, Any]]:
    """
    Convert extracted PDF pages into smaller chunks.

    Each chunk keeps the original document metadata.
    """

    validate_chunk_settings(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    if not pages:
        return []

    all_chunks: list[
        dict[str, Any]
    ] = []

    seen_chunk_ids: set[str] = set()

    for page in pages:
        validate_page_record(
            page
        )

        document_id = str(
            page["document_id"]
        ).strip()

        page_number = int(
            page["page_number"]
        )

        page_chunks = split_text(
            text=str(
                page["text"]
            ),
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        for chunk_index, chunk_text in enumerate(
            page_chunks,
            start=1,
        ):
            chunk_id = (
                f"{document_id}"
                f"-P{page_number}"
                f"-C{chunk_index}"
            )

            if chunk_id in seen_chunk_ids:
                raise ValueError(
                    "Duplicate chunk ID generated: "
                    f"{chunk_id}"
                )

            chunk_record = {
                "chunk_id": chunk_id,
                "document_id": document_id,
                "file_name": str(
                    page["file_name"]
                ),
                "title": str(
                    page["title"]
                ),
                "page_number": page_number,
                "chunk_number": chunk_index,
                "text": chunk_text,
                "maintenance": str(
                    page["maintenance"]
                ),
                "operations": str(
                    page["operations"]
                ),
                "production": str(
                    page["production"]
                ),
                "ot_cybersecurity": str(
                    page["ot_cybersecurity"]
                ),
            }

            all_chunks.append(
                chunk_record
            )

            seen_chunk_ids.add(
                chunk_id
            )

    return all_chunks


if __name__ == "__main__":
    pages = load_all_documents(
        verbose=True
    )

    chunks = create_document_chunks(
        pages=pages
    )

    print("\nText splitting completed.")
    print(
        "Total extracted pages: "
        f"{len(pages)}"
    )
    print(
        "Total generated chunks: "
        f"{len(chunks)}"
    )

    if chunks:
        first_chunk = chunks[0]

        print("\nFirst generated chunk:")
        print(
            "Chunk ID: "
            f"{first_chunk['chunk_id']}"
        )
        print(
            "Document: "
            f"{first_chunk['title']}"
        )
        print(
            "Page: "
            f"{first_chunk['page_number']}"
        )
        print(
            "Chunk number: "
            f"{first_chunk['chunk_number']}"
        )

        print(
            "\nStakeholder classifications:"
        )
        print(
            "Maintenance: "
            f"{first_chunk['maintenance']}"
        )
        print(
            "Operations: "
            f"{first_chunk['operations']}"
        )
        print(
            "Production: "
            f"{first_chunk['production']}"
        )
        print(
            "OT Cybersecurity: "
            f"{first_chunk['ot_cybersecurity']}"
        )

        print("\nChunk preview:")
        print(
            first_chunk["text"][:500]
        )