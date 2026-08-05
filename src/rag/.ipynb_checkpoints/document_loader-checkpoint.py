from pathlib import Path

import pandas as pd
from pypdf import PdfReader


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DOCUMENTS_DIR = PROJECT_ROOT / "documents" / "source"
MANIFEST_PATH = PROJECT_ROOT / "documents" / "document_manifest.csv"

STAKEHOLDERS = [
    "maintenance",
    "operations",
    "production",
    "ot_cybersecurity",
]


def load_document_manifest() -> pd.DataFrame:
    """
    Load and validate the document classification manifest.
    """

    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(
            f"Manifest file was not found: {MANIFEST_PATH}"
        )

    manifest = pd.read_csv(MANIFEST_PATH)

    required_columns = {
        "document_id",
        "file_name",
        "title",
        "maintenance",
        "operations",
        "production",
        "ot_cybersecurity",
    }

    missing_columns = required_columns.difference(manifest.columns)

    if missing_columns:
        raise ValueError(
            "The manifest is missing these columns: "
            f"{sorted(missing_columns)}"
        )

    manifest["file_name"] = manifest["file_name"].astype(str).str.strip()

    for stakeholder in STAKEHOLDERS:
        manifest[stakeholder] = (
            manifest[stakeholder]
            .astype(str)
            .str.strip()
            .str.lower()
        )

    return manifest


def extract_pdf_pages(
    pdf_path: Path,
    document_metadata: dict,
) -> list[dict]:
    """
    Extract text page by page from one PDF document.

    Each page is returned with its document and stakeholder metadata.
    """

    reader = PdfReader(pdf_path)
    pages = []

    for page_index, page in enumerate(reader.pages):
        page_text = page.extract_text() or ""
        page_text = page_text.strip()

        if not page_text:
            continue

        page_record = {
            "document_id": document_metadata["document_id"],
            "file_name": document_metadata["file_name"],
            "title": document_metadata["title"],
            "page_number": page_index + 1,
            "text": page_text,
            "maintenance": document_metadata["maintenance"],
            "operations": document_metadata["operations"],
            "production": document_metadata["production"],
            "ot_cybersecurity": document_metadata[
                "ot_cybersecurity"
            ],
        }

        pages.append(page_record)

    return pages


def load_all_documents() -> list[dict]:
    """
    Load all PDFs listed in document_manifest.csv.

    Returns:
        A list where each item represents one extracted PDF page.
    """

    manifest = load_document_manifest()
    all_pages = []

    for _, row in manifest.iterrows():
        document_metadata = row.to_dict()

        pdf_path = DOCUMENTS_DIR / document_metadata["file_name"]

        if not pdf_path.exists():
            raise FileNotFoundError(
                f"PDF listed in manifest was not found: {pdf_path}"
            )

        extracted_pages = extract_pdf_pages(
            pdf_path=pdf_path,
            document_metadata=document_metadata,
        )

        all_pages.extend(extracted_pages)

        print(
            f"Loaded: {document_metadata['file_name']} "
            f"({len(extracted_pages)} text pages)"
        )

    return all_pages


if __name__ == "__main__":
    pages = load_all_documents()

    print("\nDocument loading completed.")
    print(f"Total extracted pages: {len(pages)}")

    if pages:
        first_page = pages[0]

        print("\nFirst extracted page:")
        print(f"Document ID: {first_page['document_id']}")
        print(f"File: {first_page['file_name']}")
        print(f"Title: {first_page['title']}")
        print(f"Page: {first_page['page_number']}")

        print("\nStakeholder classifications:")
        print(f"Maintenance: {first_page['maintenance']}")
        print(f"Operations: {first_page['operations']}")
        print(f"Production: {first_page['production']}")
        print(
            "OT Cybersecurity: "
            f"{first_page['ot_cybersecurity']}"
        )

        print("\nText preview:")
        print(first_page["text"][:500])