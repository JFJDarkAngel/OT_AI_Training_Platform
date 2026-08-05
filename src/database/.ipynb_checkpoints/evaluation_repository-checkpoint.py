import json
import sqlite3

from src.database.connection import get_connection
from src.evaluation.models import (
    EvaluationReference,
    StakeholderEvaluation,
)


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

    connection = get_connection()
    cursor = connection.cursor()

    try:
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

            ON CONFLICT(scenario_id, stakeholder)
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
                evaluation.stakeholder,
                evaluation.score,
                evaluation.feedback,
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

    references_data = json.loads(
        row["references_json"] or "[]"
    )

    references = [
        EvaluationReference.model_validate(reference)
        for reference in references_data
    ]

    return StakeholderEvaluation(
        stakeholder=row["stakeholder"],
        score=row["score"],
        feedback=row["feedback"],
        correct_actions=json.loads(
            row["correct_actions"] or "[]"
        ),
        missing_actions=json.loads(
            row["missing_actions"] or "[]"
        ),
        incorrect_actions=json.loads(
            row["incorrect_actions"] or "[]"
        ),
        recommendations=json.loads(
            row["recommendations"] or "[]"
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
    cleaned_stakeholder = stakeholder.strip().lower()

    if not cleaned_scenario_id:
        raise ValueError("Scenario ID cannot be empty.")

    if not cleaned_stakeholder:
        raise ValueError("Stakeholder cannot be empty.")

    connection = get_connection()
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

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
    connection.close()

    if row is None:
        return None

    return _row_to_evaluation(row)


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
        ORDER BY stakeholder
        """,
        (cleaned_scenario_id,),
    )

    rows = cursor.fetchall()
    connection.close()

    return [
        _row_to_evaluation(row)
        for row in rows
    ]