from src.database.connection import get_connection
from src.database.evaluation_repository import get_evaluation
from src.evaluation.evaluation_engine import (
    evaluate_stakeholder_response,
)
from src.utils.scenario_id import generate_scenario_id


def create_test_scenario(scenario_text: str) -> str:
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
            "Maintenance Evaluation Test",
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

    maintenance_response = (
        "I will inspect the PLC-connected equipment, "
        "check the electrical and communication connections, "
        "and diagnose the failure. After the inspection, "
        "I will restart the conveyor immediately without "
        "waiting for Operations approval."
    )

    scenario_id = create_test_scenario(
        scenario_text=scenario_text
    )

    print(f"Created Scenario ID: {scenario_id}")
    print("Running RAG and OpenAI evaluation...")

    try:
        evaluation = evaluate_stakeholder_response(
            scenario_id=scenario_id,
            scenario_text=scenario_text,
            stakeholder="maintenance",
            user_response=maintenance_response,
            scenario_analysis=scenario_analysis,
            top_k=5,
            save_result=True,
        )

        print("\nEvaluation completed successfully.")
        print(f"Stakeholder: {evaluation.stakeholder}")
        print(f"Score: {evaluation.score}")

        print("\nCorrect Actions:")
        for action in evaluation.correct_actions:
            print(f"- {action}")

        print("\nMissing Actions:")
        for action in evaluation.missing_actions:
            print(f"- {action}")

        print("\nIncorrect Actions:")
        for action in evaluation.incorrect_actions:
            print(f"- {action}")

        print("\nFeedback:")
        print(evaluation.feedback)

        print("\nRecommendations:")
        for recommendation in evaluation.recommendations:
            print(f"- {recommendation}")

        print("\nReferences:")
        for reference in evaluation.references:
            print(
                f"- {reference.document_title}, "
                f"page {reference.page_number}"
            )
            print(f"  File: {reference.file_name}")
            print(f"  Chunk: {reference.chunk_id}")
            print(f"  Relevance: {reference.relevance}")

        saved_evaluation = get_evaluation(
            scenario_id=scenario_id,
            stakeholder="maintenance",
        )

        if saved_evaluation is None:
            raise ValueError(
                "Evaluation was generated but not saved."
            )

        print("\nEvaluation retrieved from SQLite successfully.")
        print(f"Saved score: {saved_evaluation.score}")

    except Exception as error:
        print("\nEvaluation failed.")
        print(f"Error type: {type(error).__name__}")
        print(f"Error: {error}")


if __name__ == "__main__":
    main()