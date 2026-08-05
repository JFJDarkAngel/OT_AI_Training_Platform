from src.database.connection import get_connection


def migrate_evaluations_table() -> None:
    """
    Recreate the evaluations table using the final schema.

    This removes existing evaluation records only.
    Scenarios, responses, analysis, and reports are not deleted.
    """

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            DROP TABLE IF EXISTS evaluations
            """
        )

        cursor.execute(
            """
            CREATE TABLE evaluations (
                evaluation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                scenario_id TEXT NOT NULL,
                stakeholder TEXT NOT NULL,
                score REAL NOT NULL,
                feedback TEXT NOT NULL,
                correct_actions TEXT NOT NULL DEFAULT '[]',
                missing_actions TEXT NOT NULL DEFAULT '[]',
                incorrect_actions TEXT NOT NULL DEFAULT '[]',
                recommendations TEXT NOT NULL DEFAULT '[]',
                references_json TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (scenario_id)
                    REFERENCES scenarios(scenario_id)
                    ON DELETE CASCADE,

                UNIQUE (scenario_id, stakeholder)
            )
            """
        )

        connection.commit()

        print("Evaluations table migrated successfully.")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    migrate_evaluations_table()