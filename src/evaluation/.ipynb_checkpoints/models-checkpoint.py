from typing import Literal

from pydantic import BaseModel, Field


StakeholderName = Literal[
    "ot_cybersecurity",
    "maintenance",
    "operations",
    "production",
]


class EvaluationReference(BaseModel):
    """
    One document reference used to support an evaluation.
    """

    document_title: str
    file_name: str

    page_number: int = Field(
        ge=1,
    )

    chunk_id: str
    relevance: str


class StakeholderEvaluation(BaseModel):
    """
    Complete evaluation result for one stakeholder.
    """

    stakeholder: StakeholderName

    score: float = Field(
        ge=0,
        le=100,
    )

    correct_actions: list[str] = Field(
        default_factory=list,
        max_length=5,
    )

    missing_actions: list[str] = Field(
        default_factory=list,
        max_length=5,
    )

    incorrect_actions: list[str] = Field(
        default_factory=list,
        max_length=5,
    )

    feedback: str

    recommendations: list[str] = Field(
        default_factory=list,
        max_length=5,
    )

    references: list[EvaluationReference] = Field(
        default_factory=list,
    )


class StakeholderScoreSummary(BaseModel):
    """
    Individual stakeholder score included in the overall result.
    """

    stakeholder: StakeholderName

    score: float = Field(
        ge=0,
        le=100,
    )


class OverallEvaluation(BaseModel):
    """
    Combined result after evaluating all four stakeholders.
    """

    overall_score: float = Field(
        ge=0,
        le=100,
    )

    stakeholder_scores: list[StakeholderScoreSummary]

    executive_summary: str

    overall_feedback: str

    final_recommendations: list[str] = Field(
        default_factory=list,
        max_length=7,
    )