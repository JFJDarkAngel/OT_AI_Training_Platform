from src.database.connection import get_connection


def save_scenario(scenario_id, scenario_title, scenario_text):
    """
    Save a new scenario into the database.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO scenarios (
            scenario_id,
            scenario_title,
            scenario_text
        )
        VALUES (?, ?, ?)
        """,
        (
            scenario_id,
            scenario_title,
            scenario_text,
        ),
    )

    connection.commit()
    connection.close()

    print("Scenario saved successfully.")


def get_scenario_by_id(scenario_id):
    """
    Retrieve one scenario by its ID.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM scenarios
        WHERE scenario_id = ?
        """,
        (scenario_id,),
    )

    scenario = cursor.fetchone()
    connection.close()

    return scenario