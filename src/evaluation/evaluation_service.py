import json
import sqlite3
from typing import Any

from src.database.connection import get_connection
from src.evaluation.evaluation_engine import (
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


def validate_stakeholder_responses(
    stakeholder_responses: dict[str, str],
) -> dict[str, str]:
    """
    Validate and normalize the four stakeholder responses.
    """

    normalized_responses = {
        stakeholder.strip().lower(): response.strip()
        for stakeholder, response in stakeholder_responses.items()
    }

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

    empty_responses = [
        stakeholder
        for stakeholder in REQUIRED_STAKEHOLDERS
        if not normalized_responses[stakeholder]
    ]

    if empty_responses:
        raise ValueError(
            "Empty stakeholder responses: "
            f"{empty_responses}"
        )

    unexpected_stakeholders = (
        set(normalized_responses)
        - set(REQUIRED_STAKEHOLDERS)
    )

    if unexpected_stakeholders:
        raise ValueError(
            "Unexpected stakeholder names: "
            f"{sorted(unexpected_stakeholders)}"
        )

    return {
        stakeholder: normalized_responses[stakeholder]
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
        raise ValueError("Scenario ID cannot be empty.")

    recommendations_json = json.dumps(
        overall_evaluation.final_recommendations,
        ensure_ascii=False,
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
                overall_evaluation.executive_summary,
                overall_evaluation.overall_feedback,
                recommendations_json,
                cleaned_scenario_id,
            ),
        )

        if cursor.rowcount == 0:
            raise ValueError(
                f"Scenario was not found: {cleaned_scenario_id}"
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
        raise ValueError("Scenario ID cannot be empty.")

    connection = get_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

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
        connection.close()
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
    connection.close()

    if scenario_row["overall_score"] is None:
        return None

    stakeholder_scores = [
        StakeholderScoreSummary(
            stakeholder=row["stakeholder"],
            score=row["score"],
        )
        for row in score_rows
    ]

    recommendations = json.loads(
        scenario_row["overall_recommendations"] or "[]"
    )

    return OverallEvaluation(
        overall_score=scenario_row["overall_score"],
        stakeholder_scores=stakeholder_scores,
        executive_summary=(
            scenario_row["executive_summary"] or ""
        ),
        overall_feedback=(
            scenario_row["overall_feedback"] or ""
        ),
        final_recommendations=recommendations,
    )


def evaluate_complete_scenario(
    scenario_id: str,
    scenario_text: str,
    stakeholder_responses: dict[str, str],
    scenario_analysis: dict[str, Any] | None = None,
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
        raise ValueError("Scenario ID cannot be empty.")

    if not cleaned_scenario_text:
        raise ValueError("Scenario text cannot be empty.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    validated_responses = validate_stakeholder_responses(
        stakeholder_responses
    )

    stakeholder_evaluations: list[
        StakeholderEvaluation
    ] = []

    for stakeholder in REQUIRED_STAKEHOLDERS:
        print(
            f"Evaluating {stakeholder} response..."
        )

        evaluation = evaluate_stakeholder_response(
            scenario_id=cleaned_scenario_id,
            scenario_text=cleaned_scenario_text,
            stakeholder=stakeholder,
            user_response=validated_responses[stakeholder],
            scenario_analysis=scenario_analysis,
            top_k=top_k,
            save_result=True,
        )

        stakeholder_evaluations.append(evaluation)

    print("Generating overall evaluation...")

    overall_evaluation = generate_overall_evaluation(
        scenario_text=cleaned_scenario_text,
        evaluations=stakeholder_evaluations,
    )

    save_overall_evaluation(
        scenario_id=cleaned_scenario_id,
        overall_evaluation=overall_evaluation,
    )

    return (
        stakeholder_evaluations,
        overall_evaluation,
    )