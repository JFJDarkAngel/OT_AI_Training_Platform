from src.evaluation.models import (
    OverallEvaluation,
    StakeholderEvaluation,
    StakeholderScoreSummary,
)
from src.llm.client import (
    TEXT_MODEL,
    get_openai_client,
)


REQUIRED_STAKEHOLDERS = {
    "maintenance",
    "operations",
    "production",
    "ot_cybersecurity",
}


STAKEHOLDER_ORDER = (
    "maintenance",
    "operations",
    "production",
    "ot_cybersecurity",
)


OVERALL_INSTRUCTIONS = """
You are the senior evaluator for an industrial OT incident-response
training platform.

You will receive the completed evaluations of four stakeholders:

- Maintenance
- Operations
- Production
- OT Cybersecurity

Your task is to assess the team's combined incident-response
performance.

Important rules:

1. Do not change the supplied stakeholder scores.

2. Do not recalculate or modify the supplied overall score.

3. Assess coordination between the four stakeholders.

4. Identify conflicts, gaps, unsafe dependencies, missing approvals,
   and weaknesses in recovery readiness.

5. Consider:
   - operational safety,
   - cyber containment,
   - equipment readiness,
   - controlled restart,
   - production recovery,
   - communication,
   - authorization,
   - evidence preservation,
   - and cross-team coordination.

6. The executive summary must be one concise professional paragraph.

7. The overall feedback must clearly explain the team's main
   strengths, weaknesses, and coordination gaps.

8. Return no more than seven final recommendations.

9. Each final recommendation must be practical, concise, and
   applicable to the team as a whole.

10. Do not invent new document references or technical events.

11. Base the overall assessment only on the four supplied
    stakeholder evaluations.
""".strip()


def validate_four_evaluations(
    evaluations: list[StakeholderEvaluation],
) -> dict[str, StakeholderEvaluation]:
    """
    Validate that exactly one evaluation exists
    for each required stakeholder.
    """

    if len(evaluations) != 4:
        raise ValueError(
            "Overall evaluation requires exactly four "
            "stakeholder evaluations."
        )

    evaluation_map: dict[
        str,
        StakeholderEvaluation,
    ] = {}

    for evaluation in evaluations:
        stakeholder = evaluation.stakeholder

        if stakeholder not in REQUIRED_STAKEHOLDERS:
            raise ValueError(
                f"Unexpected stakeholder evaluation: {stakeholder}"
            )

        if stakeholder in evaluation_map:
            raise ValueError(
                f"Duplicate evaluation found for: {stakeholder}"
            )

        evaluation_map[stakeholder] = evaluation

    missing_stakeholders = (
        REQUIRED_STAKEHOLDERS
        - set(evaluation_map)
    )

    if missing_stakeholders:
        raise ValueError(
            "Missing stakeholder evaluations: "
            f"{sorted(missing_stakeholders)}"
        )

    return evaluation_map


def calculate_overall_score(
    evaluations: list[StakeholderEvaluation],
) -> float:
    """
    Calculate the arithmetic average of stakeholder scores.
    """

    if not evaluations:
        raise ValueError(
            "Evaluations cannot be empty."
        )

    average = sum(
        evaluation.score
        for evaluation in evaluations
    ) / len(evaluations)

    return round(
        average,
        2,
    )


def format_list_items(
    items: list[str],
) -> str:
    """
    Convert a list of text items into prompt-ready bullets.
    """

    cleaned_items = [
        str(item).strip()
        for item in items
        if str(item).strip()
    ]

    if not cleaned_items:
        return "- None"

    return "\n".join(
        f"- {item}"
        for item in cleaned_items
    )


def format_stakeholder_evaluation(
    evaluation: StakeholderEvaluation,
) -> str:
    """
    Convert one stakeholder evaluation into prompt-ready text.
    """

    return f"""
STAKEHOLDER: {evaluation.stakeholder}
SCORE: {evaluation.score}

CORRECT ACTIONS:
{format_list_items(evaluation.correct_actions)}

MISSING ACTIONS:
{format_list_items(evaluation.missing_actions)}

INCORRECT ACTIONS:
{format_list_items(evaluation.incorrect_actions)}

FEEDBACK:
{evaluation.feedback.strip()}

STAKEHOLDER RECOMMENDATIONS:
{format_list_items(evaluation.recommendations)}
""".strip()


def build_overall_input(
    scenario_text: str,
    evaluations: list[StakeholderEvaluation],
    overall_score: float,
) -> str:
    """
    Build the complete input for the overall evaluator.
    """

    cleaned_scenario = scenario_text.strip()

    if not cleaned_scenario:
        raise ValueError(
            "Scenario text cannot be empty."
        )

    if not evaluations:
        raise ValueError(
            "Evaluations cannot be empty."
        )

    formatted_evaluations = "\n\n".join(
        format_stakeholder_evaluation(
            evaluation
        )
        for evaluation in evaluations
    )

    score_lines = "\n".join(
        (
            f"- {evaluation.stakeholder}: "
            f"{evaluation.score}"
        )
        for evaluation in evaluations
    )

    return f"""
INCIDENT SCENARIO
=================
{cleaned_scenario}


FIXED STAKEHOLDER SCORES
========================
{score_lines}

FIXED OVERALL SCORE
===================
{overall_score}


STAKEHOLDER EVALUATIONS
=======================
{formatted_evaluations}


OVERALL EVALUATION TASK
=======================
Create the final team-level evaluation.

Return:

- overall_score
  Use exactly: {overall_score}

- stakeholder_scores
  Copy the four supplied stakeholder scores exactly.

- executive_summary
  One concise professional paragraph.

- overall_feedback
  Explain team strengths, weaknesses, coordination gaps,
  safety concerns, and recovery readiness.

- final_recommendations
  Maximum seven concise recommendations for the whole team.

Do not alter any supplied score.
""".strip()


def generate_overall_evaluation(
    scenario_text: str,
    evaluations: list[StakeholderEvaluation],
) -> OverallEvaluation:
    """
    Generate the overall team evaluation using the
    four stakeholder evaluations.
    """

    evaluation_map = validate_four_evaluations(
        evaluations
    )

    ordered_evaluations = [
        evaluation_map[stakeholder]
        for stakeholder in STAKEHOLDER_ORDER
    ]

    calculated_score = calculate_overall_score(
        ordered_evaluations
    )

    stakeholder_scores = [
        StakeholderScoreSummary(
            stakeholder=evaluation.stakeholder,
            score=evaluation.score,
        )
        for evaluation in ordered_evaluations
    ]

    overall_input = build_overall_input(
        scenario_text=scenario_text,
        evaluations=ordered_evaluations,
        overall_score=calculated_score,
    )

    client = get_openai_client()

    response = client.responses.parse(
        model=TEXT_MODEL,
        instructions=OVERALL_INSTRUCTIONS,
        input=overall_input,
        text_format=OverallEvaluation,
        store=False,
    )

    overall_evaluation = response.output_parsed

    if overall_evaluation is None:
        raise ValueError(
            "OpenAI did not return a valid overall evaluation."
        )

    return overall_evaluation.model_copy(
        update={
            "overall_score": calculated_score,
            "stakeholder_scores": stakeholder_scores,
        }
    )