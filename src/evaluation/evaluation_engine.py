from typing import Any

from src.database.evaluation_repository import save_evaluation
from src.evaluation.models import StakeholderEvaluation
from src.evaluation.role_evaluator import evaluate_role_response
from src.prompts.stakeholder_responsibilities import (
    normalize_stakeholder,
)
from src.rag.retriever import retrieve_relevant_chunks


DEFAULT_TOP_K = 5


def build_retrieval_query(
    scenario_text: str,
    stakeholder: str,
    user_response: str,
) -> str:
    """
    Build a stakeholder-specific query for the RAG retriever.
    """

    return (
        "Industrial OT incident evaluation.\n\n"
        f"Scenario:\n{scenario_text}\n\n"
        f"Stakeholder:\n{stakeholder}\n\n"
        f"Stakeholder response:\n{user_response}\n\n"
        "Retrieve guidance relevant to evaluating the response's "
        "safety, correctness, completeness, role responsibilities, "
        "coordination, containment, recovery, and restart readiness."
    )


def evaluate_stakeholder_response(
    scenario_id: str,
    scenario_text: str,
    stakeholder: str,
    user_response: str,
    scenario_analysis: dict[str, Any] | None = None,
    top_k: int = DEFAULT_TOP_K,
    save_result: bool = True,
) -> StakeholderEvaluation:
    """
    Run the complete RAG + OpenAI evaluation pipeline
    for one stakeholder response.
    """

    cleaned_scenario_id = scenario_id.strip()
    cleaned_scenario_text = scenario_text.strip()
    cleaned_user_response = user_response.strip()
    cleaned_stakeholder = normalize_stakeholder(
        stakeholder
    )

    if not cleaned_scenario_id:
        raise ValueError(
            "Scenario ID cannot be empty."
        )

    if not cleaned_scenario_text:
        raise ValueError(
            "Scenario text cannot be empty."
        )

    if not cleaned_user_response:
        raise ValueError(
            "Stakeholder response cannot be empty."
        )

    if top_k <= 0:
        raise ValueError(
            "top_k must be greater than zero."
        )

    retrieval_query = build_retrieval_query(
        scenario_text=cleaned_scenario_text,
        stakeholder=cleaned_stakeholder,
        user_response=cleaned_user_response,
    )

    retrieved_chunks = retrieve_relevant_chunks(
        query=retrieval_query,
        stakeholder=cleaned_stakeholder,
        top_k=top_k,
    )

    if not retrieved_chunks:
        raise ValueError(
            "The RAG system did not retrieve "
            "any relevant document chunks."
        )

    evaluation = evaluate_role_response(
        scenario_text=cleaned_scenario_text,
        stakeholder=cleaned_stakeholder,
        user_response=cleaned_user_response,
        retrieved_chunks=retrieved_chunks,
        scenario_analysis=scenario_analysis,
    )

    if save_result:
        save_evaluation(
            scenario_id=cleaned_scenario_id,
            evaluation=evaluation,
        )

    return evaluation