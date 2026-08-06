import sqlite3

from src.database.connection import get_connection


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


def save_response(
    scenario_id: str,
    stakeholder: str,
    answer_text: str,
) -> None:
    """
    Save or update one stakeholder response for a scenario.
    """

    cleaned_scenario_id = scenario_id.strip()
    cleaned_stakeholder = validate_stakeholder(
        stakeholder
    )
    cleaned_answer = answer_text.strip()

    if not cleaned_scenario_id:
        raise ValueError("Scenario ID cannot be empty.")

    if not cleaned_answer:
        raise ValueError("Answer text cannot be empty.")

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO responses (
                scenario_id,
                stakeholder,
                answer_text
            )
            VALUES (?, ?, ?)

            ON CONFLICT (
                scenario_id,
                stakeholder
            )
            DO UPDATE SET
                answer_text = excluded.answer_text,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                cleaned_scenario_id,
                cleaned_stakeholder,
                cleaned_answer,
            ),
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_response(
    scenario_id: str,
    stakeholder: str,
) -> sqlite3.Row | None:
    """
    Retrieve one stakeholder response for a scenario.
    """

    cleaned_scenario_id = scenario_id.strip()
    cleaned_stakeholder = validate_stakeholder(
        stakeholder
    )

    if not cleaned_scenario_id:
        raise ValueError("Scenario ID cannot be empty.")

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                response_id,
                scenario_id,
                stakeholder,
                answer_text,
                created_at,
                updated_at
            FROM responses
            WHERE scenario_id = ?
              AND stakeholder = ?
            """,
            (
                cleaned_scenario_id,
                cleaned_stakeholder,
            ),
        )

        return cursor.fetchone()

    finally:
        connection.close()


def get_all_responses(
    scenario_id: str,
) -> list[sqlite3.Row]:
    """
    Retrieve all stakeholder responses for one scenario.
    """

    cleaned_scenario_id = scenario_id.strip()

    if not cleaned_scenario_id:
        raise ValueError("Scenario ID cannot be empty.")

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                response_id,
                scenario_id,
                stakeholder,
                answer_text,
                created_at,
                updated_at
            FROM responses
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

        return cursor.fetchall()

    finally:
        connection.close()