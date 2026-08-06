from pathlib import Path
from typing import Any

import pandas as pd
from pypdf import PdfReader


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DOCUMENTS_DIR = (
    PROJECT_ROOT
    / "documents"
    / "source"
)

MANIFEST_PATH = (
    PROJECT_ROOT
    / "documents"
    / "document_manifest.csv"
)


STAKEHOLDERS = (
    "maintenance",
    "operations",
    "production",
    "ot_cybersecurity",
)


REQUIRED_COLUMNS = {
    "document_id",
    "file_name",
    "title",
    *STAKEHOLDERS,
}


ALLOWED_CLASSIFICATION_VALUES = {
    "direct",
    "supporting",
    "none",
}


def load_document_manifest() -> pd.DataFrame:
    """
    Load and validate the document classification manifest.
    """

    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(
            "Manifest file was not found: "
            f"{MANIFEST_PATH}"
        )

    manifest = pd.read_csv(
        MANIFEST_PATH,
        dtype=str,
        keep_default_na=False,
    )

    missing_columns = (
        REQUIRED_COLUMNS
        - set(manifest.columns)
    )

    if missing_columns:
        raise ValueError(
            "The manifest is missing these columns: "
            f"{sorted(missing_columns)}"
        )

    manifest = manifest.copy()

    text_columns = (
        "document_id",
        "file_name",
        "title",
        *STAKEHOLDERS,
    )

    for column in text_columns:
        manifest[column] = (
            manifest[column]
            .astype(str)
            .str.strip()
        )

    for column in (
        "document_id",
        "file_name",
        "title",
    ):
        empty_rows = manifest.index[
            manifest[column] == ""
        ].tolist()

        if empty_rows:
            csv_rows = [
                row_index + 2
                for row_index in empty_rows
            ]

            raise ValueError(
                f"Column '{column}' contains empty values "
                f"at CSV rows: {csv_rows}"
            )

    duplicate_document_ids = manifest.loc[
        manifest["document_id"].duplicated(
            keep=False
        ),
        "document_id",
    ].unique()

    if len(duplicate_document_ids) > 0:
        raise ValueError(
            "Duplicate document IDs were found: "
            f"{sorted(duplicate_document_ids.tolist())}"
        )

    duplicate_file_names = manifest.loc[
        manifest["file_name"].duplicated(
            keep=False
        ),
        "file_name",
    ].unique()

    if len(duplicate_file_names) > 0:
        raise ValueError(
            "Duplicate file names were found: "
            f"{sorted(duplicate_file_names.tolist())}"
        )

    for stakeholder in STAKEHOLDERS:
        manifest[stakeholder] = (
            manifest[stakeholder]
            .str.lower()
        )

        invalid_values = sorted(
            set(manifest[stakeholder])
            - ALLOWED_CLASSIFICATION_VALUES
        )

        if invalid_values:
            raise ValueError(
                "Invalid classification values for "
                f"{stakeholder}: {invalid_values}. "
                "Allowed values are: "
                f"{sorted(ALLOWED_CLASSIFICATION_VALUES)}"
            )

    return manifest


def resolve_pdf_path(
    file_name: str,
) -> Path:
    """
    Resolve and validate one PDF path from the manifest.
    """

    cleaned_file_name = file_name.strip()

    if not cleaned_file_name:
        raise ValueError(
            "PDF file name cannot be empty."
        )

    documents_directory = (
        DOCUMENTS_DIR.resolve()
    )

    pdf_path = (
        documents_directory
        / cleaned_file_name
    ).resolve()

    try:
        pdf_path.relative_to(
            documents_directory
        )

    except ValueError as error:
        raise ValueError(
            "The PDF path must remain inside "
            f"{DOCUMENTS_DIR}: {cleaned_file_name}"
        ) from error

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(
            "Only PDF documents are supported: "
            f"{cleaned_file_name}"
        )

    if not pdf_path.exists():
        raise FileNotFoundError(
            "PDF listed in the manifest "
            f"was not found: {pdf_path}"
        )

    if not pdf_path.is_file():
        raise ValueError(
            "The manifest path is not a file: "
            f"{pdf_path}"
        )

    return pdf_path


def extract_pdf_pages(
    pdf_path: Path,
    document_metadata: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Extract text page by page from one PDF document.

    Each page is returned with document and stakeholder metadata.
    """

    try:
        reader = PdfReader(
            str(pdf_path)
        )

    except Exception as error:
        raise ValueError(
            f"Failed to open PDF: {pdf_path}"
        ) from error

    pages: list[
        dict[str, Any]
    ] = []

    for page_number, page in enumerate(
        reader.pages,
        start=1,
    ):
        try:
            page_text = (
                page.extract_text()
                or ""
            ).strip()

        except Exception as error:
            raise ValueError(
                "Failed to extract text from "
                f"{pdf_path.name}, page {page_number}."
            ) from error

        if not page_text:
            continue

        pages.append(
            {
                "document_id": str(
                    document_metadata[
                        "document_id"
                    ]
                ),
                "file_name": str(
                    document_metadata[
                        "file_name"
                    ]
                ),
                "title": str(
                    document_metadata[
                        "title"
                    ]
                ),
                "page_number": page_number,
                "text": page_text,
                "maintenance": str(
                    document_metadata[
                        "maintenance"
                    ]
                ),
                "operations": str(
                    document_metadata[
                        "operations"
                    ]
                ),
                "production": str(
                    document_metadata[
                        "production"
                    ]
                ),
                "ot_cybersecurity": str(
                    document_metadata[
                        "ot_cybersecurity"
                    ]
                ),
            }
        )

    return pages


def load_all_documents(
    verbose: bool = False,
) -> list[dict[str, Any]]:
    """
    Load all PDFs listed in document_manifest.csv.

    Args:
        verbose:
            Print loading progress when True.

    Returns:
        A list where each item represents one extracted PDF page.
    """

    manifest = load_document_manifest()

    all_pages: list[
        dict[str, Any]
    ] = []

    for _, row in manifest.iterrows():
        document_metadata = row.to_dict()

        pdf_path = resolve_pdf_path(
            document_metadata[
                "file_name"
            ]
        )

        extracted_pages = extract_pdf_pages(
            pdf_path=pdf_path,
            document_metadata=(
                document_metadata
            ),
        )

        all_pages.extend(
            extracted_pages
        )

        if verbose:
            print(
                "Loaded: "
                f"{document_metadata['file_name']} "
                f"({len(extracted_pages)} text pages)"
            )

    return all_pages


if __name__ == "__main__":
    pages = load_all_documents(
        verbose=True
    )

    print("\nDocument loading completed.")
    print(
        "Total extracted pages: "
        f"{len(pages)}"
    )

    if pages:
        first_page = pages[0]

        print("\nFirst extracted page:")
        print(
            "Document ID: "
            f"{first_page['document_id']}"
        )
        print(
            "File: "
            f"{first_page['file_name']}"
        )
        print(
            "Title: "
            f"{first_page['title']}"
        )
        print(
            "Page: "
            f"{first_page['page_number']}"
        )

        print(
            "\nStakeholder classifications:"
        )
        print(
            "Maintenance: "
            f"{first_page['maintenance']}"
        )
        print(
            "Operations: "
            f"{first_page['operations']}"
        )
        print(
            "Production: "
            f"{first_page['production']}"
        )
        print(
            "OT Cybersecurity: "
            f"{first_page['ot_cybersecurity']}"
        )

        print("\nText preview:")
        print(
            first_page["text"][:500]
        )