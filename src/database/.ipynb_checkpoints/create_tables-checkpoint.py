from src.database.connection import get_connection


def create_tables() -> None:
    """
    Create the main database tables used by the platform.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS scenarios (
            scenario_id TEXT PRIMARY KEY,
            scenario_title TEXT NOT NULL,
            scenario_text TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'draft',
            overall_score REAL,
            executive_summary TEXT,
            overall_feedback TEXT,
            overall_recommendations TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS scenario_analysis (
            analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario_id TEXT NOT NULL UNIQUE,
            asset_area TEXT NOT NULL DEFAULT 'Unknown',
            severity TEXT NOT NULL DEFAULT 'unknown',
            plc_status TEXT NOT NULL DEFAULT 'unknown',
            hmi_status TEXT NOT NULL DEFAULT 'unknown',
            network_status TEXT NOT NULL DEFAULT 'unknown',
            last_known_state TEXT NOT NULL DEFAULT 'unknown',
            active_alarms INTEGER,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (scenario_id)
                REFERENCES scenarios(scenario_id)
                ON DELETE CASCADE
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS responses (
            response_id INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario_id TEXT NOT NULL,
            stakeholder TEXT NOT NULL,
            answer_text TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (scenario_id)
                REFERENCES scenarios(scenario_id)
                ON DELETE CASCADE,

            UNIQUE (scenario_id, stakeholder)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS evaluations (
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

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS reports (
            report_id INTEGER PRIMARY KEY AUTOINCREMENT,
            scenario_id TEXT NOT NULL UNIQUE,
            report_path TEXT NOT NULL,
            generated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (scenario_id)
                REFERENCES scenarios(scenario_id)
                ON DELETE CASCADE
        )
        """
    )

    connection.commit()
    connection.close()

    print("Database tables created successfully.")


if __name__ == "__main__":
    create_tables()