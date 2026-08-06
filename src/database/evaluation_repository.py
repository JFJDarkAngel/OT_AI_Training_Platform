import json
import sqlite3
from typing import Any

from src.database.connection import get_connection
from src.evaluation.models import (
    EvaluationReference,
    StakeholderEvaluation,
)


ALLOWED_STAKEHOLDERS = {
    "ot_cybersecurity",
    "maintenance",
    "operations",
    "production",
}


def validate_stakeholder(
    stakeholder: str,
) -> str:
    """
    Validate and normalize a stakeholder name.
    """

    cleaned_stakeholder = stakeholder.strip().lower()

    if not cleaned_stakeholder:
        raise ValueError("Stakeholder cannot be empty.")

    if cleaned_stakeholder not in ALLOWED_STAKEHOLDERS:
        raise ValueError(
            f"Invalid stakeholder: {cleaned_stakeholder}. "
            f"Allowed values: {sorted(ALLOWED_STAKEHOLDERS)}"
        )

    return cleaned_stakeholder


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


def save_evaluation(
    scenario_id: str,
    evaluation: StakeholderEvaluation,
) -> None:
    """
    Save or update one stakeholder evaluation.
    """

    cleaned_scenario_id = scenario_id.strip()

    if not cleaned_scenario_id:
        raise ValueError("Scenario ID cannot be empty.")

    cleaned_stakeholder = validate_stakeholder(
        evaluation.stakeholder
    )

    correct_actions_json = json.dumps(
        evaluation.correct_actions,
        ensure_ascii=False,
    )

    missing_actions_json = json.dumps(
        evaluation.missing_actions,
        ensure_ascii=False,
    )

    incorrect_actions_json = json.dumps(
        evaluation.incorrect_actions,
        ensure_ascii=False,
    )

    recommendations_json = json.dumps(
        evaluation.recommendations,
        ensure_ascii=False,
    )

    references_json = json.dumps(
        [
            reference.model_dump()
            for reference in evaluation.references
        ],
        ensure_ascii=False,
    )

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO evaluations (
                scenario_id,
                stakeholder,
                score,
                feedback,
                correct_actions,
                missing_actions,
                incorrect_actions,
                recommendations,
                references_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT (
                scenario_id,
                stakeholder
            )
            DO UPDATE SET
                score = excluded.score,
                feedback = excluded.feedback,
                correct_actions = excluded.correct_actions,
                missing_actions = excluded.missing_actions,
                incorrect_actions = excluded.incorrect_actions,
                recommendations = excluded.recommendations,
                references_json = excluded.references_json,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                cleaned_scenario_id,
                cleaned_stakeholder,
                evaluation.score,
                evaluation.feedback.strip(),
                correct_actions_json,
                missing_actions_json,
                incorrect_actions_json,
                recommendations_json,
                references_json,
            ),
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def _row_to_evaluation(
    row: sqlite3.Row,
) -> StakeholderEvaluation:
    """
    Convert one SQLite row into StakeholderEvaluation.
    """

    references_data = parse_json_list(
        row["references_json"]
    )

    references = [
        EvaluationReference.model_validate(
            reference
        )
        for reference in references_data
        if isinstance(
            reference,
            dict,
        )
    ]

    return StakeholderEvaluation(
        stakeholder=row["stakeholder"],
        score=row["score"],
        feedback=row["feedback"],
        correct_actions=parse_json_list(
            row["correct_actions"]
        ),
        missing_actions=parse_json_list(
            row["missing_actions"]
        ),
        incorrect_actions=parse_json_list(
            row["incorrect_actions"]
        ),
        recommendations=parse_json_list(
            row["recommendations"]
        ),
        references=references,
    )


def get_evaluation(
    scenario_id: str,
    stakeholder: str,
) -> StakeholderEvaluation | None:
    """
    Retrieve one stakeholder evaluation.
    """

    cleaned_scenario_id = scenario_id.strip()

    if not cleaned_scenario_id:
        raise ValueError("Scenario ID cannot be empty.")

    cleaned_stakeholder = validate_stakeholder(
        stakeholder
    )

    connection = get_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                stakeholder,
                score,
                feedback,
                correct_actions,
                missing_actions,
                incorrect_actions,
                recommendations,
                references_json
            FROM evaluations
            WHERE scenario_id = ?
              AND stakeholder = ?
            """,
            (
                cleaned_scenario_id,
                cleaned_stakeholder,
            ),
        )

        row = cursor.fetchone()

    finally:
        connection.close()

    if row is None:
        return None

    return _row_to_evaluation(
        row
    )


def get_all_evaluations(
    scenario_id: str,
) -> list[StakeholderEvaluation]:
    """
    Retrieve all saved stakeholder evaluations
    for one scenario.
    """

    cleaned_scenario_id = scenario_id.strip()

    if not cleaned_scenario_id:
        raise ValueError("Scenario ID cannot be empty.")

    connection = get_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                stakeholder,
                score,
                feedback,
                correct_actions,
                missing_actions,
                incorrect_actions,
                recommendations,
                references_json
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

        rows = cursor.fetchall()

    finally:
        connection.close()

    return [
        _row_to_evaluation(
            row
        )
        for row in rows
    ]