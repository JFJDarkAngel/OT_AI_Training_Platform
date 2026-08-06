from src.database.connection import get_connection


def create_tables() -> None:
    """
    Create the main database tables used by the platform.
    """

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS scenarios (
                scenario_id TEXT PRIMARY KEY,
                scenario_title TEXT NOT NULL,
                scenario_text TEXT NOT NULL,

                status TEXT NOT NULL DEFAULT 'draft'
                    CHECK (
                        status IN (
                            'draft',
                            'evaluated'
                        )
                    ),

                overall_score REAL
                    CHECK (
                        overall_score IS NULL
                        OR (
                            overall_score >= 0
                            AND overall_score <= 100
                        )
                    ),

                executive_summary TEXT,
                overall_feedback TEXT,
                overall_recommendations TEXT,

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                updated_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS scenario_analysis (
                analysis_id INTEGER PRIMARY KEY AUTOINCREMENT,

                scenario_id TEXT NOT NULL UNIQUE,

                asset_area TEXT NOT NULL
                    DEFAULT 'Unknown',

                severity TEXT NOT NULL
                    DEFAULT 'unknown'
                    CHECK (
                        severity IN (
                            'low',
                            'medium',
                            'high',
                            'critical',
                            'unknown'
                        )
                    ),

                plc_status TEXT NOT NULL
                    DEFAULT 'unknown'
                    CHECK (
                        plc_status IN (
                            'online',
                            'offline',
                            'degraded',
                            'unknown'
                        )
                    ),

                hmi_status TEXT NOT NULL
                    DEFAULT 'unknown'
                    CHECK (
                        hmi_status IN (
                            'online',
                            'offline',
                            'degraded',
                            'unknown'
                        )
                    ),

                network_status TEXT NOT NULL
                    DEFAULT 'unknown'
                    CHECK (
                        network_status IN (
                            'up',
                            'down',
                            'degraded',
                            'unknown'
                        )
                    ),

                last_known_state TEXT NOT NULL
                    DEFAULT 'unknown'
                    CHECK (
                        last_known_state IN (
                            'running',
                            'stopped',
                            'idle',
                            'manual',
                            'unknown'
                        )
                    ),

                active_alarms INTEGER
                    CHECK (
                        active_alarms IS NULL
                        OR active_alarms >= 0
                    ),

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                updated_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

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

                stakeholder TEXT NOT NULL
                    CHECK (
                        stakeholder IN (
                            'maintenance',
                            'operations',
                            'production',
                            'ot_cybersecurity'
                        )
                    ),

                answer_text TEXT NOT NULL,

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                updated_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (scenario_id)
                    REFERENCES scenarios(scenario_id)
                    ON DELETE CASCADE,

                UNIQUE (
                    scenario_id,
                    stakeholder
                )
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS evaluations (
                evaluation_id INTEGER PRIMARY KEY AUTOINCREMENT,

                scenario_id TEXT NOT NULL,

                stakeholder TEXT NOT NULL
                    CHECK (
                        stakeholder IN (
                            'maintenance',
                            'operations',
                            'production',
                            'ot_cybersecurity'
                        )
                    ),

                score REAL NOT NULL
                    CHECK (
                        score >= 0
                        AND score <= 100
                    ),

                feedback TEXT NOT NULL,

                correct_actions TEXT NOT NULL
                    DEFAULT '[]',

                missing_actions TEXT NOT NULL
                    DEFAULT '[]',

                incorrect_actions TEXT NOT NULL
                    DEFAULT '[]',

                recommendations TEXT NOT NULL
                    DEFAULT '[]',

                references_json TEXT NOT NULL
                    DEFAULT '[]',

                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                updated_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (scenario_id)
                    REFERENCES scenarios(scenario_id)
                    ON DELETE CASCADE,

                UNIQUE (
                    scenario_id,
                    stakeholder
                )
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                report_id INTEGER PRIMARY KEY AUTOINCREMENT,

                scenario_id TEXT NOT NULL UNIQUE,

                report_path TEXT NOT NULL,

                generated_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (scenario_id)
                    REFERENCES scenarios(scenario_id)
                    ON DELETE CASCADE
            )
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
                idx_scenarios_status
            ON scenarios(status)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
                idx_scenarios_created_at
            ON scenarios(created_at)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
                idx_responses_scenario_id
            ON responses(scenario_id)
            """
        )

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
                idx_evaluations_scenario_id
            ON evaluations(scenario_id)
            """
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

    print("Database tables created successfully.")


if __name__ == "__main__":
    create_tables()