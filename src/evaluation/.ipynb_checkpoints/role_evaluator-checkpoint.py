from typing import Any

from src.evaluation.models import (
    EvaluationReference,
    StakeholderEvaluation,
)
from src.llm.client import (
    TEXT_MODEL,
    get_openai_client,
)
from src.prompts.evaluation_prompt import (
    build_evaluation_input,
    build_evaluation_instructions,
)
from src.prompts.stakeholder_responsibilities import (
    normalize_stakeholder,
)


def validate_evaluation_references(
    evaluation: StakeholderEvaluation,
    retrieved_chunks: list[dict[str, Any]],
) -> StakeholderEvaluation:
    """
    Keep only references that actually exist in the RAG results.

    Metadata is copied from the retrieved chunks so the model
    cannot invent document names, pages, file names, or chunk IDs.
    """

    allowed_chunks: dict[str, dict[str, Any]] = {
        str(chunk["chunk_id"]): chunk
        for chunk in retrieved_chunks
        if chunk.get("chunk_id")
    }

    validated_references: list[
        EvaluationReference
    ] = []

    seen_chunk_ids: set[str] = set()

    for reference in evaluation.references:
        reference_chunk_id = str(
            reference.chunk_id
        )

        if reference_chunk_id in seen_chunk_ids:
            continue

        source_chunk = allowed_chunks.get(
            reference_chunk_id
        )

        if source_chunk is None:
            continue

        metadata = (
            source_chunk.get("metadata")
            or {}
        )

        page_number = metadata.get(
            "page_number"
        )

        try:
            validated_page_number = int(
                page_number
            )

        except (
            TypeError,
            ValueError,
        ):
            continue

        if validated_page_number < 1:
            continue

        relevance = reference.relevance.strip()

        if not relevance:
            relevance = (
                "This retrieved source supports "
                "the evaluation."
            )

        validated_references.append(
            EvaluationReference(
                document_title=str(
                    metadata.get(
                        "title",
                        "Unknown",
                    )
                ),
                file_name=str(
                    metadata.get(
                        "file_name",
                        "Unknown",
                    )
                ),
                page_number=(
                    validated_page_number
                ),
                chunk_id=str(
                    source_chunk[
                        "chunk_id"
                    ]
                ),
                relevance=relevance,
            )
        )

        seen_chunk_ids.add(
            reference_chunk_id
        )

    return evaluation.model_copy(
        update={
            "references": (
                validated_references
            ),
        }
    )


def evaluate_role_response(
    scenario_text: str,
    stakeholder: str,
    user_response: str,
    retrieved_chunks: list[dict[str, Any]],
    scenario_analysis: (
        dict[str, Any] | None
    ) = None,
) -> StakeholderEvaluation:
    """
    Evaluate one stakeholder response using OpenAI
    and return a structured StakeholderEvaluation.
    """

    cleaned_scenario_text = (
        scenario_text.strip()
    )

    cleaned_user_response = (
        user_response.strip()
    )

    if not cleaned_scenario_text:
        raise ValueError(
            "Scenario text cannot be empty."
        )

    if not cleaned_user_response:
        raise ValueError(
            "User response cannot be empty."
        )

    cleaned_stakeholder = (
        normalize_stakeholder(
            stakeholder
        )
    )

    if not retrieved_chunks:
        raise ValueError(
            "No RAG document chunks were supplied "
            "for the evaluation."
        )

    instructions = (
        build_evaluation_instructions(
            stakeholder=cleaned_stakeholder
        )
    )

    evaluation_input = (
        build_evaluation_input(
            scenario_text=(
                cleaned_scenario_text
            ),
            stakeholder=(
                cleaned_stakeholder
            ),
            user_response=(
                cleaned_user_response
            ),
            retrieved_chunks=(
                retrieved_chunks
            ),
            scenario_analysis=(
                scenario_analysis
            ),
        )
    )

    client = get_openai_client()

    response = client.responses.parse(
        model=TEXT_MODEL,
        instructions=instructions,
        input=evaluation_input,
        text_format=StakeholderEvaluation,
        store=False,
    )

    evaluation = response.output_parsed

    if evaluation is None:
        raise ValueError(
            "OpenAI did not return a valid "
            "stakeholder evaluation."
        )

    if (
        evaluation.stakeholder
        != cleaned_stakeholder
    ):
        raise ValueError(
            "Returned stakeholder does not match "
            "the requested stakeholder: "
            f"{cleaned_stakeholder}"
        )

    return validate_evaluation_references(
        evaluation=evaluation,
        retrieved_chunks=retrieved_chunks,
    )