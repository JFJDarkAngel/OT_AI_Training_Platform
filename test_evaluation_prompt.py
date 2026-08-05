from src.prompts.evaluation_prompt import (
    build_evaluation_input,
    build_evaluation_instructions,
)


def main() -> None:
    scenario = (
        "PLC-02 stopped communicating with the HMI while "
        "Conveyor 2 remained in operation."
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

    user_response = (
        "I will inspect the PLC-connected equipment and "
        "restart the conveyor immediately."
    )

    retrieved_chunks = [
        {
            "chunk_id": "DOC-001-P16-C2",
            "text": (
                "Restore equipment using controlled restart "
                "hold points and verify readiness."
            ),
            "metadata": {
                "title": (
                    "Mining Company Business Continuity Plan"
                ),
                "file_name": (
                    "mining_business_continuity_plan.pdf"
                ),
                "page_number": 16,
            },
            "distance": 0.45,
        }
    ]

    instructions = build_evaluation_instructions(
        stakeholder="maintenance"
    )

    evaluation_input = build_evaluation_input(
        scenario_text=scenario,
        stakeholder="maintenance",
        user_response=user_response,
        retrieved_chunks=retrieved_chunks,
        scenario_analysis=scenario_analysis,
    )

    print("\n" + "=" * 70)
    print("EVALUATION INSTRUCTIONS")
    print("=" * 70)
    print(instructions)

    print("\n" + "=" * 70)
    print("EVALUATION INPUT")
    print("=" * 70)
    print(evaluation_input)


if __name__ == "__main__":
    main()