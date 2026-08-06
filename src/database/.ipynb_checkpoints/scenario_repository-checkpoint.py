import sqlite3
from typing import Any

from src.database.connection import get_connection


ALLOWED_SCENARIO_STATUSES = {
    "draft",
    "evaluated",
}


def save_scenario(
    scenario_id: str,
    scenario_title: str,
    scenario_text: str,
) -> None:
    """
    Save a new scenario into the database.
    """

    cleaned_scenario_id = scenario_id.strip()
    cleaned_title = scenario_title.strip()
    cleaned_text = scenario_text.strip()

    if not cleaned_scenario_id:
        raise ValueError("Scenario ID cannot be empty.")

    if not cleaned_title:
        raise ValueError("Scenario title cannot be empty.")

    if not cleaned_text:
        raise ValueError("Scenario text cannot be empty.")

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO scenarios (
                scenario_id,
                scenario_title,
                scenario_text,
                status
            )
            VALUES (?, ?, ?, 'draft')
            """,
            (
                cleaned_scenario_id,
                cleaned_title,
                cleaned_text,
            ),
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def save_scenario_analysis(
    scenario_id: str,
    analysis_data: dict[str, Any],
) -> None:
    """
    Save or update the operational summary for a scenario.
    """

    cleaned_scenario_id = scenario_id.strip()

    if not cleaned_scenario_id:
        raise ValueError("Scenario ID cannot be empty.")

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO scenario_analysis (
                scenario_id,
                asset_area,
                severity,
                plc_status,
                hmi_status,
                network_status,
                last_known_state,
                active_alarms
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(scenario_id)
            DO UPDATE SET
                asset_area = excluded.asset_area,
                severity = excluded.severity,
                plc_status = excluded.plc_status,
                hmi_status = excluded.hmi_status,
                network_status = excluded.network_status,
                last_known_state = excluded.last_known_state,
                active_alarms = excluded.active_alarms,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                cleaned_scenario_id,
                analysis_data.get(
                    "asset_area",
                    "Unknown",
                ),
                analysis_data.get(
                    "severity",
                    "unknown",
                ),
                analysis_data.get(
                    "plc_status",
                    "unknown",
                ),
                analysis_data.get(
                    "hmi_status",
                    "unknown",
                ),
                analysis_data.get(
                    "network_status",
                    "unknown",
                ),
                analysis_data.get(
                    "last_known_state",
                    "unknown",
                ),
                analysis_data.get(
                    "active_alarms"
                ),
            ),
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_scenario_by_id(
    scenario_id: str,
):
    """
    Retrieve one scenario by its ID.
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
            SELECT *
            FROM scenarios
            WHERE scenario_id = ?
            """,
            (cleaned_scenario_id,),
        )

        return cursor.fetchone()

    finally:
        connection.close()


def get_scenario_analysis(
    scenario_id: str,
):
    """
    Retrieve the saved operational summary for a scenario.
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
            SELECT *
            FROM scenario_analysis
            WHERE scenario_id = ?
            """,
            (cleaned_scenario_id,),
        )

        return cursor.fetchone()

    finally:
        connection.close()


def get_all_scenarios() -> list[sqlite3.Row]:
    """
    Retrieve all scenarios for the Scenario History page.

    Includes the saved operational severity and report path.
    Newest scenarios are returned first.
    """

    connection = get_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                s.scenario_id,
                s.scenario_title,
                s.scenario_text,
                s.status,
                s.overall_score,
                s.created_at,
                s.updated_at,
                COALESCE(
                    sa.severity,
                    'unknown'
                ) AS severity,
                sa.asset_area,
                r.report_path,
                r.generated_at AS report_generated_at
            FROM scenarios AS s

            LEFT JOIN scenario_analysis AS sa
                ON sa.scenario_id = s.scenario_id

            LEFT JOIN reports AS r
                ON r.scenario_id = s.scenario_id

            ORDER BY
                s.created_at DESC,
                s.scenario_id DESC
            """
        )

        return cursor.fetchall()

    finally:
        connection.close()


def search_scenarios(
    search_text: str,
) -> list[sqlite3.Row]:
    """
    Search scenarios by Scenario ID or scenario title.
    """

    cleaned_search = search_text.strip()

    if not cleaned_search:
        return get_all_scenarios()

    search_pattern = f"%{cleaned_search}%"

    connection = get_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                s.scenario_id,
                s.scenario_title,
                s.scenario_text,
                s.status,
                s.overall_score,
                s.created_at,
                s.updated_at,
                COALESCE(
                    sa.severity,
                    'unknown'
                ) AS severity,
                sa.asset_area,
                r.report_path,
                r.generated_at AS report_generated_at
            FROM scenarios AS s

            LEFT JOIN scenario_analysis AS sa
                ON sa.scenario_id = s.scenario_id

            LEFT JOIN reports AS r
                ON r.scenario_id = s.scenario_id

            WHERE
                s.scenario_id LIKE ?
                OR s.scenario_title LIKE ?

            ORDER BY
                s.created_at DESC,
                s.scenario_id DESC
            """,
            (
                search_pattern,
                search_pattern,
            ),
        )

        return cursor.fetchall()

    finally:
        connection.close()


def filter_scenarios_by_status(
    status: str,
) -> list[sqlite3.Row]:
    """
    Retrieve scenarios matching one status.

    Allowed statuses:
    - draft
    - evaluated
    """

    cleaned_status = status.strip().lower()

    if cleaned_status not in ALLOWED_SCENARIO_STATUSES:
        raise ValueError(
            f"Invalid scenario status: {cleaned_status}. "
            f"Allowed values: "
            f"{sorted(ALLOWED_SCENARIO_STATUSES)}"
        )

    connection = get_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                s.scenario_id,
                s.scenario_title,
                s.scenario_text,
                s.status,
                s.overall_score,
                s.created_at,
                s.updated_at,
                COALESCE(
                    sa.severity,
                    'unknown'
                ) AS severity,
                sa.asset_area,
                r.report_path,
                r.generated_at AS report_generated_at
            FROM scenarios AS s

            LEFT JOIN scenario_analysis AS sa
                ON sa.scenario_id = s.scenario_id

            LEFT JOIN reports AS r
                ON r.scenario_id = s.scenario_id

            WHERE LOWER(s.status) = ?

            ORDER BY
                s.created_at DESC,
                s.scenario_id DESC
            """,
            (cleaned_status,),
        )

        return cursor.fetchall()

    finally:
        connection.close()


def get_scenario_history(
    search_text: str = "",
    status: str = "all",
) -> list[sqlite3.Row]:
    """
    Retrieve scenarios using optional search and status filters.

    This is the main function used by the Scenario History page.

    Supported status values:
    - all
    - draft
    - evaluated
    """

    cleaned_search = search_text.strip()
    cleaned_status = status.strip().lower()

    if cleaned_status not in {
        "all",
        *ALLOWED_SCENARIO_STATUSES,
    }:
        raise ValueError(
            f"Invalid scenario status filter: "
            f"{cleaned_status}"
        )

    query = """
        SELECT
            s.scenario_id,
            s.scenario_title,
            s.scenario_text,
            s.status,
            s.overall_score,
            s.created_at,
            s.updated_at,
            COALESCE(
                sa.severity,
                'unknown'
            ) AS severity,
            sa.asset_area,
            r.report_path,
            r.generated_at AS report_generated_at
        FROM scenarios AS s

        LEFT JOIN scenario_analysis AS sa
            ON sa.scenario_id = s.scenario_id

        LEFT JOIN reports AS r
            ON r.scenario_id = s.scenario_id

        WHERE 1 = 1
    """

    parameters: list[str] = []

    if cleaned_search:
        search_pattern = f"%{cleaned_search}%"

        query += """
            AND (
                s.scenario_id LIKE ?
                OR s.scenario_title LIKE ?
            )
        """

        parameters.extend(
            [
                search_pattern,
                search_pattern,
            ]
        )

    if cleaned_status != "all":
        query += """
            AND LOWER(s.status) = ?
        """

        parameters.append(
            cleaned_status
        )

    query += """
        ORDER BY
            s.created_at DESC,
            s.scenario_id DESC
    """

    connection = get_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    try:
        cursor.execute(
            query,
            parameters,
        )

        return cursor.fetchall()

    finally:
        connection.close()


def get_scenario_count(
    status: str = "all",
) -> int:
    """
    Count scenarios, optionally filtered by status.
    """

    cleaned_status = status.strip().lower()

    if cleaned_status not in {
        "all",
        *ALLOWED_SCENARIO_STATUSES,
    }:
        raise ValueError(
            f"Invalid scenario status filter: "
            f"{cleaned_status}"
        )

    connection = get_connection()
    cursor = connection.cursor()

    try:
        if cleaned_status == "all":
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM scenarios
                """
            )

        else:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM scenarios
                WHERE LOWER(status) = ?
                """,
                (cleaned_status,),
            )

        result = cursor.fetchone()

        return int(result[0]) if result else 0

    finally:
        connection.close()