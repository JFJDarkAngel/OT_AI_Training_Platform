from src.database.connection import get_connection


ALLOWED_STAKEHOLDERS = {
    "ot_cybersecurity",
    "maintenance",
    "operations",
    "production",
}


def save_response(
    scenario_id: str,
    stakeholder: str,
    answer_text: str,
) -> None:
    """
    Save or update one stakeholder response for a scenario.
    """

    if stakeholder not in ALLOWED_STAKEHOLDERS:
        raise ValueError(
            f"Invalid stakeholder: {stakeholder}. "
            f"Allowed values: {sorted(ALLOWED_STAKEHOLDERS)}"
        )

    if not answer_text.strip():
        raise ValueError("Answer text cannot be empty.")

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO responses (
            scenario_id,
            stakeholder,
            answer_text
        )
        VALUES (?, ?, ?)

        ON CONFLICT (scenario_id, stakeholder)
        DO UPDATE SET
            answer_text = excluded.answer_text,
            created_at = CURRENT_TIMESTAMP
        """,
        (
            scenario_id,
            stakeholder,
            answer_text.strip(),
        ),
    )

    connection.commit()
    connection.close()

    print(f"{stakeholder} response saved successfully.")


def get_response(
    scenario_id: str,
    stakeholder: str,
):
    """
    Retrieve one stakeholder response for a scenario.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM responses
        WHERE scenario_id = ?
          AND stakeholder = ?
        """,
        (
            scenario_id,
            stakeholder,
        ),
    )

    response = cursor.fetchone()
    connection.close()

    return response


def get_all_responses(scenario_id: str):
    """
    Retrieve all stakeholder responses for one scenario.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM responses
        WHERE scenario_id = ?
        ORDER BY stakeholder
        """,
        (scenario_id,),
    )

    responses = cursor.fetchall()
    connection.close()

    return responses