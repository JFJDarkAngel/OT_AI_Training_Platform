from src.database.connection import get_connection
from src.database.evaluation_repository import (
    get_all_evaluations,
    get_evaluation,
    save_evaluation,
)
from src.evaluation.models import (
    EvaluationReference,
    StakeholderEvaluation,
)
from src.utils.scenario_id import generate_scenario_id


def create_test_scenario() -> str:
    """
    Create a scenario required by the foreign key.
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
            "Evaluation Repository Test",
            (
                "PLC-02 lost communication while "
                "Conveyor 2 remained in operation."
            ),
        ),
    )

    connection.commit()
    connection.close()

    return scenario_id


def main() -> None:
    scenario_id = create_test_scenario()

    evaluation = StakeholderEvaluation(
        stakeholder="maintenance",
        score=82,
        correct_actions=[
            "Inspect the PLC-connected equipment.",
            "Verify equipment readiness before restart.",
        ],
        missing_actions=[
            "Coordinate restart approval with Operations.",
        ],
        incorrect_actions=[
            "Restarting before completing all checks.",
        ],
        feedback=(
            "The response includes important inspection actions, "
            "but coordination and restart authorization are incomplete."
        ),
        recommendations=[
            "Document all inspection results.",
            "Coordinate with Operations before restart.",
        ],
        references=[
            EvaluationReference(
                document_title=(
                    "SIMATIC PCS 7 Engineering System Manual"
                ),
                file_name="simatic_pcs7_manual.pdf",
                page_number=120,
                chunk_id="DOC-005-P120-C1",
                relevance=(
                    "Supports equipment diagnosis and "
                    "restart verification."
                ),
            )
        ],
    )

    save_evaluation(
        scenario_id=scenario_id,
        evaluation=evaluation,
    )

    print("Evaluation saved successfully.")

    saved_evaluation = get_evaluation(
        scenario_id=scenario_id,
        stakeholder="maintenance",
    )

    if saved_evaluation is None:
        raise ValueError(
            "The saved evaluation could not be retrieved."
        )

    print("\nRetrieved Evaluation:")
    print(f"Scenario ID: {scenario_id}")
    print(f"Stakeholder: {saved_evaluation.stakeholder}")
    print(f"Score: {saved_evaluation.score}")
    print(f"Correct Actions: {saved_evaluation.correct_actions}")
    print(f"Missing Actions: {saved_evaluation.missing_actions}")
    print(
        f"Incorrect Actions: "
        f"{saved_evaluation.incorrect_actions}"
    )
    print(f"Feedback: {saved_evaluation.feedback}")
    print(
        f"Recommendations: "
        f"{saved_evaluation.recommendations}"
    )
    print(
        f"References count: "
        f"{len(saved_evaluation.references)}"
    )

    all_evaluations = get_all_evaluations(scenario_id)

    print(
        f"\nTotal saved evaluations: "
        f"{len(all_evaluations)}"
    )


if __name__ == "__main__":
    main()