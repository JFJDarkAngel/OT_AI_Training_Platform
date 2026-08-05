from src.database.connection import get_connection
from src.evaluation.evaluation_service import (
    evaluate_complete_scenario,
    get_saved_overall_evaluation,
)
from src.utils.scenario_id import generate_scenario_id


def create_test_scenario(
    scenario_text: str,
) -> str:
    """
    Create a scenario for the complete evaluation test.
    """

    scenario_id = generate_scenario_id()

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
            "Complete Evaluation Service Test",
            scenario_text,
        ),
    )

    connection.commit()
    connection.close()

    return scenario_id


def main() -> None:
    scenario_text = (
        "Conveyor 2 stopped sending data to the HMI. "
        "PLC-02 is offline while the HMI remains online. "
        "Three communication alarms are active. "
        "The conveyor was running before communication was lost."
    )

    scenario_analysis = {
        "asset_area": "Conveyor 2",
        "severity": "high",
        "plc_status": "offline",
        "hmi_status": "online",
        "network_status": "degraded",
        "last_known_state": "running",
        "active_alarms": 3,
    }

    stakeholder_responses = {
        "maintenance": (
            "Inspect the PLC-connected equipment, diagnose "
            "the communication failure, verify electrical "
            "connections, and coordinate equipment readiness "
            "with Operations before restart."
        ),

        "operations": (
            "Place the conveyor process in a safe state, "
            "monitor alarms and process variables, use approved "
            "manual controls if required, and coordinate a "
            "controlled restart after technical approval."
        ),

        "production": (
            "Assess the production impact, prioritize critical "
            "processes, establish reduced operating capacity, "
            "and authorize a gradual return to production only "
            "after safety and technical readiness are confirmed."
        ),

        "ot_cybersecurity": (
            "Investigate the communication loss, isolate affected "
            "network assets if needed, preserve logs and evidence, "
            "verify trusted configurations and communications, "
            "and monitor the network during recovery."
        ),
    }

    scenario_id = create_test_scenario(
        scenario_text=scenario_text
    )

    print(f"Scenario ID: {scenario_id}")
    print("Starting complete scenario evaluation...\n")

    try:
        evaluations, overall = evaluate_complete_scenario(
            scenario_id=scenario_id,
            scenario_text=scenario_text,
            stakeholder_responses=stakeholder_responses,
            scenario_analysis=scenario_analysis,
            top_k=5,
        )

        print("\nComplete evaluation finished successfully.")

        print("\nStakeholder Scores:")
        for evaluation in evaluations:
            print(
                f"- {evaluation.stakeholder}: "
                f"{evaluation.score}"
            )

        print(f"\nOverall Score: {overall.overall_score}")

        print("\nExecutive Summary:")
        print(overall.executive_summary)

        print("\nOverall Feedback:")
        print(overall.overall_feedback)

        print("\nFinal Recommendations:")
        for recommendation in overall.final_recommendations:
            print(f"- {recommendation}")

        saved_overall = get_saved_overall_evaluation(
            scenario_id=scenario_id
        )

        if saved_overall is None:
            raise ValueError(
                "Overall evaluation was not saved."
            )

        print(
            "\nOverall evaluation retrieved "
            "from SQLite successfully."
        )
        print(
            f"Saved Overall Score: "
            f"{saved_overall.overall_score}"
        )

    except Exception as error:
        print("\nComplete evaluation failed.")
        print(f"Error type: {type(error).__name__}")
        print(f"Error: {error}")


if __name__ == "__main__":
    main()