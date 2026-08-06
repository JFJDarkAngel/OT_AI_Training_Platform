import json
import sqlite3
from typing import Any

from src.database.connection import get_connection
from src.evaluation.evaluation_engine import (
    MAX_TOP_K,
    evaluate_stakeholder_response,
)
from src.evaluation.models import (
    OverallEvaluation,
    StakeholderEvaluation,
    StakeholderScoreSummary,
)
from src.evaluation.overall_evaluator import (
    generate_overall_evaluation,
)


REQUIRED_STAKEHOLDERS = (
    "maintenance",
    "operations",
    "production",
    "ot_cybersecurity",
)


def parse_json_list(
    value: Any,
) -> list[Any]:
    """
    Convert saved JSON text into a Python list.
    """

    if not value:
        return []

    if isinstance(value, list):
        return value

    try:
        parsed_value = json.loads(
            str(value)
        )

    except json.JSONDecodeError:
        return []

    if isinstance(parsed_value, list):
        return parsed_value

    return []


def validate_stakeholder_responses(
    stakeholder_responses: dict[str, str],
) -> dict[str, str]:
    """
    Validate and normalize the four stakeholder responses.
    """

    if not stakeholder_responses:
        raise ValueError(
            "Stakeholder responses cannot be empty."
        )

    normalized_responses: dict[str, str] = {}

    for stakeholder, response in stakeholder_responses.items():
        cleaned_stakeholder = (
            stakeholder.strip().lower()
        )

        cleaned_response = response.strip()

        if not cleaned_stakeholder:
            raise ValueError(
                "Stakeholder name cannot be empty."
            )

        if cleaned_stakeholder in normalized_responses:
            raise ValueError(
                "Duplicate stakeholder response found: "
                f"{cleaned_stakeholder}"
            )

        normalized_responses[
            cleaned_stakeholder
        ] = cleaned_response

    missing_stakeholders = [
        stakeholder
        for stakeholder in REQUIRED_STAKEHOLDERS
        if stakeholder not in normalized_responses
    ]

    if missing_stakeholders:
        raise ValueError(
            "Missing stakeholder responses: "
            f"{missing_stakeholders}"
        )

    unexpected_stakeholders = sorted(
        set(normalized_responses)
        - set(REQUIRED_STAKEHOLDERS)
    )

    if unexpected_stakeholders:
        raise ValueError(
            "Unexpected stakeholder names: "
            f"{unexpected_stakeholders}"
        )

    empty_responses = [
        stakeholder
        for stakeholder in REQUIRED_STAKEHOLDERS
        if not normalized_responses[
            stakeholder
        ]
    ]

    if empty_responses:
        raise ValueError(
            "Empty stakeholder responses: "
            f"{empty_responses}"
        )

    return {
        stakeholder: normalized_responses[
            stakeholder
        ]
        for stakeholder in REQUIRED_STAKEHOLDERS
    }


def save_overall_evaluation(
    scenario_id: str,
    overall_evaluation: OverallEvaluation,
) -> None:
    """
    Save the overall evaluation in the scenarios table.
    """

    cleaned_scenario_id = scenario_id.strip()

    if not cleaned_scenario_id:
        raise ValueError(
            "Scenario ID cannot be empty."
        )

    recommendations_json = json.dumps(
        overall_evaluation.final_recommendations,
        ensure_ascii=False,
    )

    executive_summary = (
        overall_evaluation
        .executive_summary
        .strip()
    )

    overall_feedback = (
        overall_evaluation
        .overall_feedback
        .strip()
    )

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            UPDATE scenarios
            SET
                overall_score = ?,
                executive_summary = ?,
                overall_feedback = ?,
                overall_recommendations = ?,
                status = 'evaluated',
                updated_at = CURRENT_TIMESTAMP
            WHERE scenario_id = ?
            """,
            (
                overall_evaluation.overall_score,
                executive_summary,
                overall_feedback,
                recommendations_json,
                cleaned_scenario_id,
            ),
        )

        if cursor.rowcount == 0:
            raise ValueError(
                "Scenario was not found: "
                f"{cleaned_scenario_id}"
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_saved_overall_evaluation(
    scenario_id: str,
) -> OverallEvaluation | None:
    """
    Retrieve the saved overall evaluation for one scenario.
    """

    cleaned_scenario_id = scenario_id.strip()

    if not cleaned_scenario_id:
        raise ValueError(
            "Scenario ID cannot be empty."
        )

    connection = get_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                overall_score,
                executive_summary,
                overall_feedback,
                overall_recommendations
            FROM scenarios
            WHERE scenario_id = ?
            """,
            (cleaned_scenario_id,),
        )

        scenario_row = cursor.fetchone()

        if scenario_row is None:
            return None

        if scenario_row["overall_score"] is None:
            return None

        cursor.execute(
            """
            SELECT
                stakeholder,
                score
            FROM evaluations
            WHERE scenario_id = ?
            ORDER BY
                CASE stakeholder
                    WHEN 'maintenance' THEN 1
                    WHEN 'operations' THEN 2
                    WHEN 'production' THEN 3
                    WHEN 'ot_cybersecurity' THEN 4
                    ELSE 5
                END
            """,
            (cleaned_scenario_id,),
        )

        score_rows = cursor.fetchall()

    finally:
        connection.close()

    stakeholder_scores = [
        StakeholderScoreSummary(
            stakeholder=row["stakeholder"],
            score=row["score"],
        )
        for row in score_rows
    ]

    recommendations = parse_json_list(
        scenario_row[
            "overall_recommendations"
        ]
    )

    return OverallEvaluation(
        overall_score=(
            scenario_row["overall_score"]
        ),
        stakeholder_scores=(
            stakeholder_scores
        ),
        executive_summary=(
            scenario_row[
                "executive_summary"
            ]
            or ""
        ),
        overall_feedback=(
            scenario_row[
                "overall_feedback"
            ]
            or ""
        ),
        final_recommendations=[
            str(item)
            for item in recommendations
        ],
    )


def evaluate_complete_scenario(
    scenario_id: str,
    scenario_text: str,
    stakeholder_responses: dict[str, str],
    scenario_analysis: (
        dict[str, Any] | None
    ) = None,
    top_k: int = 5,
) -> tuple[
    list[StakeholderEvaluation],
    OverallEvaluation,
]:
    """
    Evaluate all four stakeholder responses, generate the overall
    evaluation, and save all results in SQLite.
    """

    cleaned_scenario_id = scenario_id.strip()
    cleaned_scenario_text = scenario_text.strip()

    if not cleaned_scenario_id:
        raise ValueError(
            "Scenario ID cannot be empty."
        )

    if not cleaned_scenario_text:
        raise ValueError(
            "Scenario text cannot be empty."
        )

    if top_k <= 0:
        raise ValueError(
            "top_k must be greater than zero."
        )

    if top_k > MAX_TOP_K:
        raise ValueError(
            f"top_k cannot exceed {MAX_TOP_K}."
        )

    validated_responses = (
        validate_stakeholder_responses(
            stakeholder_responses
        )
    )

    stakeholder_evaluations: list[
        StakeholderEvaluation
    ] = []

    for stakeholder in REQUIRED_STAKEHOLDERS:
        evaluation = evaluate_stakeholder_response(
            scenario_id=cleaned_scenario_id,
            scenario_text=cleaned_scenario_text,
            stakeholder=stakeholder,
            user_response=(
                validated_responses[
                    stakeholder
                ]
            ),
            scenario_analysis=scenario_analysis,
            top_k=top_k,
            save_result=True,
        )

        stakeholder_evaluations.append(
            evaluation
        )

    if (
        len(stakeholder_evaluations)
        != len(REQUIRED_STAKEHOLDERS)
    ):
        raise ValueError(
            "The four stakeholder evaluations "
            "were not completed."
        )

    overall_evaluation = (
        generate_overall_evaluation(
            scenario_text=(
                cleaned_scenario_text
            ),
            evaluations=(
                stakeholder_evaluations
            ),
        )
    )

    save_overall_evaluation(
        scenario_id=cleaned_scenario_id,
        overall_evaluation=overall_evaluation,
    )

    return (
        stakeholder_evaluations,
        overall_evaluation,
    )