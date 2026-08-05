from src.evaluation.models import StakeholderEvaluation
from src.evaluation.overall_evaluator import (
    generate_overall_evaluation,
)


def main() -> None:
    scenario_text = (
        "Conveyor 2 stopped sending data to the HMI. "
        "PLC-02 is offline while the HMI remains online. "
        "Three communication alarms are active. "
        "The conveyor was running before communication was lost."
    )

    evaluations = [
        StakeholderEvaluation(
            stakeholder="maintenance",
            score=45,
            correct_actions=[
                "Inspected the PLC-connected equipment.",
                "Diagnosed electrical and communication connections.",
            ],
            missing_actions=[
                "Did not obtain Operations restart authorization.",
            ],
            incorrect_actions=[
                "Proposed an immediate restart.",
            ],
            feedback=(
                "The response included appropriate inspection tasks "
                "but proposed an unsafe and premature restart."
            ),
            recommendations=[
                "Complete safety checks before restart.",
                "Coordinate restart approval with Operations.",
            ],
            references=[],
        ),

        StakeholderEvaluation(
            stakeholder="operations",
            score=82,
            correct_actions=[
                "Placed the process in a safe state.",
                "Monitored alarms and process conditions.",
            ],
            missing_actions=[
                "Did not clearly define restart hold points.",
            ],
            incorrect_actions=[],
            feedback=(
                "The response demonstrated good process control "
                "and operational awareness."
            ),
            recommendations=[
                "Define controlled restart hold points.",
            ],
            references=[],
        ),

        StakeholderEvaluation(
            stakeholder="production",
            score=74,
            correct_actions=[
                "Assessed production impact.",
                "Prioritized critical production processes.",
            ],
            missing_actions=[
                "Did not define acceptable reduced capacity.",
            ],
            incorrect_actions=[],
            feedback=(
                "The response addressed production priorities but "
                "needed clearer recovery capacity limits."
            ),
            recommendations=[
                "Define acceptable reduced operating capacity.",
            ],
            references=[],
        ),

        StakeholderEvaluation(
            stakeholder="ot_cybersecurity",
            score=91,
            correct_actions=[
                "Preserved logs and forensic evidence.",
                "Isolated the affected network segment.",
                "Verified system integrity before reconnection.",
            ],
            missing_actions=[
                "Did not explicitly document recovery approval.",
            ],
            incorrect_actions=[],
            feedback=(
                "The response demonstrated strong containment, "
                "evidence preservation, and secure recovery actions."
            ),
            recommendations=[
                "Document formal recovery approval.",
            ],
            references=[],
        ),
    ]

    try:
        result = generate_overall_evaluation(
            scenario_text=scenario_text,
            evaluations=evaluations,
        )

        print("\nOverall evaluation completed successfully.")
        print(f"Overall Score: {result.overall_score}")

        print("\nStakeholder Scores:")
        for item in result.stakeholder_scores:
            print(
                f"- {item.stakeholder}: {item.score}"
            )

        print("\nExecutive Summary:")
        print(result.executive_summary)

        print("\nOverall Feedback:")
        print(result.overall_feedback)

        print("\nFinal Recommendations:")
        for recommendation in result.final_recommendations:
            print(f"- {recommendation}")

    except Exception as error:
        print("\nOverall evaluation failed.")
        print(f"Error type: {type(error).__name__}")
        print(f"Error: {error}")


if __name__ == "__main__":
    main()