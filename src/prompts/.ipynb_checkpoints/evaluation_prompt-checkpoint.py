from typing import Any

from src.prompts.stakeholder_responsibilities import (
    format_stakeholder_responsibilities,
    normalize_stakeholder,
)


def format_scenario_analysis(
    scenario_analysis: dict[str, Any] | None,
) -> str:
    """
    Convert saved scenario analysis into prompt-ready text.
    """

    if not scenario_analysis:
        return "Scenario operational summary: Not available."

    active_alarms = scenario_analysis.get("active_alarms")

    if active_alarms is None:
        active_alarms_text = "Unknown"
    else:
        active_alarms_text = str(active_alarms)

    return (
        "Scenario operational summary:\n"
        f"- Asset / Area: "
        f"{scenario_analysis.get('asset_area', 'Unknown')}\n"
        f"- Severity: "
        f"{scenario_analysis.get('severity', 'unknown')}\n"
        f"- PLC Status: "
        f"{scenario_analysis.get('plc_status', 'unknown')}\n"
        f"- HMI Status: "
        f"{scenario_analysis.get('hmi_status', 'unknown')}\n"
        f"- Network Status: "
        f"{scenario_analysis.get('network_status', 'unknown')}\n"
        f"- Last Known State: "
        f"{scenario_analysis.get('last_known_state', 'unknown')}\n"
        f"- Active Alarms: {active_alarms_text}"
    )


def format_rag_context(
    retrieved_chunks: list[dict[str, Any]],
) -> str:
    """
    Convert retrieved RAG chunks into prompt-ready references.
    """

    if not retrieved_chunks:
        return (
            "No document references were retrieved. "
            "Do not invent references."
        )

    formatted_chunks: list[str] = []

    for index, chunk in enumerate(
        retrieved_chunks,
        start=1,
    ):
        metadata = chunk.get("metadata") or {}

        chunk_id = str(
            chunk.get("chunk_id", "Unknown")
        )

        document_title = str(
            metadata.get("title", "Unknown")
        )

        file_name = str(
            metadata.get("file_name", "Unknown")
        )

        page_number = metadata.get(
            "page_number",
            "Unknown",
        )

        text = str(
            chunk.get("text", "")
        ).strip()

        formatted_chunks.append(
            "\n".join(
                [
                    f"[REFERENCE {index}]",
                    f"Chunk ID: {chunk_id}",
                    f"Document title: {document_title}",
                    f"File name: {file_name}",
                    f"Page number: {page_number}",
                    "Source text:",
                    text,
                ]
            )
        )

    return "\n\n".join(formatted_chunks)


def build_evaluation_instructions(
    stakeholder: str,
) -> str:
    """
    Create the fixed evaluator instructions.
    """

    cleaned_stakeholder = normalize_stakeholder(
        stakeholder
    )

    return f"""
You are an evaluator for an industrial OT incident-response
training platform.

Evaluate only the response written for this stakeholder:
{cleaned_stakeholder}

Important evaluation rules:

1. Evaluate the response against:
   - the incident scenario,
   - the stakeholder's assigned responsibilities,
   - and the supplied RAG document references.

2. Do not evaluate the stakeholder for actions that primarily
   belong to another role, unless coordination is clearly required.

3. Identify:
   - correct actions actually stated by the user,
   - important missing actions,
   - unsafe, incorrect, premature, contradictory, or
     role-inappropriate actions.

4. Score the response from 0 to 100.

5. Base the score on:
   - role relevance,
   - safety,
   - completeness,
   - technical correctness,
   - coordination,
   - recovery readiness,
   - and support from the supplied references.

6. Do not assume the user performed an action that was not written
   in the response.

7. Do not invent procedures, document titles, page numbers,
   file names, or chunk IDs.

8. References may only use the exact references supplied in the
   RAG context.

9. Include only references that genuinely support the evaluation.

10. If no supplied reference supports a claim, do not create a
    reference for that claim.

11. Keep the evaluation concise and professional.

12. Limit the output as follows:
    - correct_actions: maximum 5 items,
    - missing_actions: maximum 5 items,
    - incorrect_actions: maximum 5 items,
    - recommendations: maximum 5 items,
    - feedback: one concise paragraph, maximum 120 words.

13. Each action or recommendation must be one concise sentence.

14. Prioritize important findings over minor details.

15. Do not repeat the same point in more than one list unless it is
    necessary to explain a safety issue.

16. Return the stakeholder value exactly as:
    "{cleaned_stakeholder}"
""".strip()


def build_evaluation_input(
    scenario_text: str,
    stakeholder: str,
    user_response: str,
    retrieved_chunks: list[dict[str, Any]],
    scenario_analysis: dict[str, Any] | None = None,
) -> str:
    """
    Build the complete input sent to the evaluation model.
    """

    cleaned_scenario = scenario_text.strip()
    cleaned_response = user_response.strip()

    if not cleaned_scenario:
        raise ValueError(
            "Scenario text cannot be empty."
        )

    if not cleaned_response:
        raise ValueError(
            "Stakeholder response cannot be empty."
        )

    cleaned_stakeholder = normalize_stakeholder(
        stakeholder
    )

    responsibility_text = (
        format_stakeholder_responsibilities(
            cleaned_stakeholder
        )
    )

    analysis_text = format_scenario_analysis(
        scenario_analysis
    )

    rag_context = format_rag_context(
        retrieved_chunks
    )

    return f"""
INCIDENT SCENARIO
=================
{cleaned_scenario}


OPERATIONAL SUMMARY
===================
{analysis_text}


STAKEHOLDER ROLE
================
{responsibility_text}


USER RESPONSE
=============
{cleaned_response}


RETRIEVED DOCUMENT REFERENCES
=============================
{rag_context}


EVALUATION TASK
===============
Evaluate the user's response for the selected stakeholder.

Return only a structured evaluation containing:

- stakeholder

- score
  - A number from 0 to 100.

- correct_actions
  - Maximum 5 items.
  - Include only actions explicitly stated by the user.
  - Each item must be one concise sentence.

- missing_actions
  - Maximum 5 items.
  - Include only the most important missing actions.
  - Each item must be one concise sentence.

- incorrect_actions
  - Maximum 5 items.
  - Include only unsafe, incorrect, premature,
    contradictory, or role-inappropriate actions.
  - Each item must be one concise sentence.

- feedback
  - One concise professional paragraph.
  - Maximum 120 words.
  - Explain the main strengths, weaknesses, and safety concerns.

- recommendations
  - Maximum 5 practical recommendations.
  - Each recommendation must be one concise sentence.
  - Avoid repeating items already listed as missing actions.

- references
  - Use only the supplied RAG references.
  - Include only references that genuinely support the evaluation.
  - Do not invent document titles, file names, page numbers,
    or chunk IDs.

Every returned reference must exactly match one supplied RAG
reference, including its document title, file name, page number,
and chunk ID.

IMPORTANT:
- Do not generate unnecessary detail.
- Prioritize quality over quantity.
- Avoid repeated or overlapping points.
- Keep the evaluation concise, clear, and suitable for the
  interface and final report.
""".strip()