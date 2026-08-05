from src.rag.document_loader import load_all_documents


DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200


def split_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    """
    Split text into overlapping character-based chunks.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative.")

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size."
        )

    cleaned_text = " ".join(text.split())

    if not cleaned_text:
        return []

    chunks = []
    start = 0
    text_length = len(cleaned_text)

    while start < text_length:
        end = min(start + chunk_size, text_length)

        chunk = cleaned_text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == text_length:
            break

        start = end - chunk_overlap

    return chunks


def create_document_chunks(
    pages: list[dict],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[dict]:
    """
    Convert extracted PDF pages into smaller chunks.

    Each chunk keeps the original document metadata.
    """

    all_chunks = []

    for page in pages:
        page_chunks = split_text(
            text=page["text"],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        for chunk_index, chunk_text in enumerate(
            page_chunks,
            start=1,
        ):
            chunk_record = {
                "chunk_id": (
                    f"{page['document_id']}"
                    f"-P{page['page_number']}"
                    f"-C{chunk_index}"
                ),
                "document_id": page["document_id"],
                "file_name": page["file_name"],
                "title": page["title"],
                "page_number": page["page_number"],
                "chunk_number": chunk_index,
                "text": chunk_text,
                "maintenance": page["maintenance"],
                "operations": page["operations"],
                "production": page["production"],
                "ot_cybersecurity": page[
                    "ot_cybersecurity"
                ],
            }

            all_chunks.append(chunk_record)

    return all_chunks


if __name__ == "__main__":
    pages = load_all_documents()

    chunks = create_document_chunks(pages)

    print("\nText splitting completed.")
    print(f"Total extracted pages: {len(pages)}")
    print(f"Total generated chunks: {len(chunks)}")

    if chunks:
        first_chunk = chunks[0]

        print("\nFirst generated chunk:")
        print(f"Chunk ID: {first_chunk['chunk_id']}")
        print(f"Document: {first_chunk['title']}")
        print(f"Page: {first_chunk['page_number']}")
        print(f"Chunk number: {first_chunk['chunk_number']}")

        print("\nStakeholder classifications:")
        print(f"Maintenance: {first_chunk['maintenance']}")
        print(f"Operations: {first_chunk['operations']}")
        print(f"Production: {first_chunk['production']}")
        print(
            "OT Cybersecurity: "
            f"{first_chunk['ot_cybersecurity']}"
        )

        print("\nChunk preview:")
        print(first_chunk["text"][:500])