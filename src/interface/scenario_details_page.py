import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from src.database.connection import get_connection
from src.database.evaluation_repository import (
    get_all_evaluations,
)
from src.database.response_repository import (
    get_all_responses,
)
from src.database.scenario_repository import (
    get_scenario_analysis,
    get_scenario_by_id,
)
from src.reporting.report_generator import generate_report


STAKEHOLDER_ORDER = (
    "maintenance",
    "operations",
    "production",
    "ot_cybersecurity",
)


STAKEHOLDER_NAMES = {
    "maintenance": "Maintenance",
    "operations": "Operations",
    "production": "Production",
    "ot_cybersecurity": "OT Cybersecurity",
}


def row_value(
    row: Any,
    key: str,
    default: Any = None,
) -> Any:
    """
    Safely retrieve a value from sqlite3.Row or dictionary.
    """

    if row is None:
        return default

    try:
        value = row[key]
    except (KeyError, IndexError, TypeError):
        return default

    return default if value is None else value


def format_datetime(
    value: Any,
) -> str:
    """
    Convert an SQLite timestamp into readable text.
    """

    if not value:
        return "Unknown"

    text = str(value).strip()

    for date_format in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S.%f",
    ):
        try:
            parsed_date = datetime.strptime(
                text,
                date_format,
            )

            return parsed_date.strftime(
                "%d %b %Y - %I:%M %p"
            )

        except ValueError:
            continue

    return text


def parse_json_list(
    value: Any,
) -> list[Any]:
    """
    Convert a saved JSON string into a list.
    """

    if not value:
        return []

    if isinstance(value, list):
        return value

    try:
        parsed_value = json.loads(
            str(value)
        )

    except json.JSONDecodeError:
        return [str(value)]

    if isinstance(parsed_value, list):
        return parsed_value

    return [parsed_value]


def get_saved_report_path(
    scenario_id: str,
) -> Path | None:
    """
    Retrieve the saved PDF report path for a scenario.
    """

    connection = get_connection()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT report_path
            FROM reports
            WHERE scenario_id = ?
            """,
            (scenario_id,),
        )

        row = cursor.fetchone()

    finally:
        connection.close()

    if row is None:
        return None

    report_path_value = row["report_path"]

    if not report_path_value:
        return None

    report_path = Path(
        report_path_value
    )

    if not report_path.exists():
        return None

    return report_path


def render_text_list(
    title: str,
    items: list[str],
    empty_text: str = "None recorded.",
) -> None:
    """
    Render a list of evaluation items.
    """

    st.markdown(f"**{title}**")

    if not items:
        st.caption(empty_text)
        return

    for item in items:
        st.markdown(f"- {item}")


def render_operational_summary(
    analysis: Any,
) -> None:
    """
    Display the saved operational summary.
    """

    first_row = st.columns(4)

    first_items = (
        (
            "Asset / Area",
            row_value(
                analysis,
                "asset_area",
                "Unknown",
            ),
        ),
        (
            "Severity",
            row_value(
                analysis,
                "severity",
                "unknown",
            ),
        ),
        (
            "PLC Status",
            row_value(
                analysis,
                "plc_status",
                "unknown",
            ),
        ),
        (
            "HMI Status",
            row_value(
                analysis,
                "hmi_status",
                "unknown",
            ),
        ),
    )

    for column, (
        label,
        value,
    ) in zip(
        first_row,
        first_items,
    ):
        with column:
            st.metric(
                label,
                str(value).title(),
            )

    second_row = st.columns(3)

    second_items = (
        (
            "Network Status",
            row_value(
                analysis,
                "network_status",
                "unknown",
            ),
        ),
        (
            "Last Known State",
            row_value(
                analysis,
                "last_known_state",
                "unknown",
            ),
        ),
        (
            "Active Alarms",
            row_value(
                analysis,
                "active_alarms",
                "Unknown",
            ),
        ),
    )

    for column, (
        label,
        value,
    ) in zip(
        second_row,
        second_items,
    ):
        with column:
            st.metric(
                label,
                str(value).title(),
            )


def render_responses(
    response_rows: list[Any],
) -> None:
    """
    Display all saved stakeholder responses.
    """

    responses_map: dict[str, str] = {}

    for response in response_rows:
        stakeholder = str(
            row_value(
                response,
                "stakeholder",
                "",
            )
        )

        answer_text = str(
            row_value(
                response,
                "answer_text",
                "",
            )
        )

        if stakeholder:
            responses_map[
                stakeholder
            ] = answer_text

    if not responses_map:
        st.info(
            "No stakeholder responses were saved."
        )
        return

    for stakeholder in STAKEHOLDER_ORDER:
        answer_text = responses_map.get(
            stakeholder
        )

        if not answer_text:
            continue

        display_name = STAKEHOLDER_NAMES[
            stakeholder
        ]

        with st.expander(
            f"{display_name} Response",
            expanded=False,
        ):
            st.write(answer_text)


def render_evaluations(
    evaluations: list[Any],
) -> None:
    """
    Display all saved stakeholder evaluations.
    """

    if not evaluations:
        st.info(
            "No stakeholder evaluations were saved."
        )
        return

    evaluation_map = {
        evaluation.stakeholder: evaluation
        for evaluation in evaluations
    }

    for stakeholder in STAKEHOLDER_ORDER:
        evaluation = evaluation_map.get(
            stakeholder
        )

        if evaluation is None:
            continue

        display_name = STAKEHOLDER_NAMES[
            stakeholder
        ]

        with st.expander(
            (
                f"{display_name} Evaluation "
                f"— {evaluation.score:.1f}/100"
            ),
            expanded=False,
        ):
            st.metric(
                "Score",
                f"{evaluation.score:.1f}/100",
            )

            st.markdown("### Feedback")
            st.write(
                evaluation.feedback
            )

            detail_columns = st.columns(2)

            with detail_columns[0]:
                render_text_list(
                    "Correct Actions",
                    evaluation.correct_actions,
                )

                render_text_list(
                    "Missing Actions",
                    evaluation.missing_actions,
                )

            with detail_columns[1]:
                render_text_list(
                    "Incorrect Actions",
                    evaluation.incorrect_actions,
                )

                render_text_list(
                    "Recommendations",
                    evaluation.recommendations,
                )

            st.markdown("### References")

            if not evaluation.references:
                st.caption(
                    "No references were recorded."
                )

            else:
                for reference in evaluation.references:
                    st.markdown(
                        (
                            f"**{reference.document_title}**  \n"
                            f"File: `{reference.file_name}`  \n"
                            f"Page: {reference.page_number}  \n"
                            f"Chunk: `{reference.chunk_id}`  \n"
                            f"Relevance: {reference.relevance}"
                        )
                    )

                    st.divider()


def render_report_section(
    scenario_id: str,
    overall_score: Any,
) -> None:
    """
    Generate or download the PDF report.
    """

    st.markdown("## PDF Report")

    report_path = get_saved_report_path(
        scenario_id
    )

    session_report_path = (
        st.session_state.get(
            "details_report_path"
        )
    )

    if session_report_path:
        candidate_path = Path(
            session_report_path
        )

        if candidate_path.exists():
            report_path = candidate_path

    action_columns = st.columns(
        [1, 2],
    )

    with action_columns[0]:
        generate_clicked = st.button(
            (
                "Regenerate PDF Report"
                if report_path
                else "Generate PDF Report"
            ),
            type="primary",
            use_container_width=True,
            disabled=(
                overall_score is None
            ),
            key=(
                "details_generate_report_"
                f"{scenario_id}"
            ),
        )

    if generate_clicked:
        try:
            with st.spinner(
                "Generating the PDF report..."
            ):
                generated_path = generate_report(
                    scenario_id
                )

            st.session_state[
                "details_report_path"
            ] = str(
                generated_path
            )

            st.rerun()

        except Exception as error:
            st.error(
                "The PDF report could not be generated."
            )

            st.exception(error)

    with action_columns[1]:
        if report_path is not None:
            pdf_bytes = report_path.read_bytes()

            st.download_button(
                label="Download PDF Report",
                data=pdf_bytes,
                file_name=report_path.name,
                mime="application/pdf",
                use_container_width=True,
                key=(
                    "details_download_report_"
                    f"{scenario_id}"
                ),
            )

        elif overall_score is None:
            st.info(
                "Complete the evaluation before "
                "generating the report."
            )

        else:
            st.info(
                "Generate the report to enable download."
            )


def show_scenario_details_page(
    scenario_id: str,
) -> None:
    """
    Display complete information for one saved scenario.
    """

    cleaned_scenario_id = scenario_id.strip()

    if not cleaned_scenario_id:
        st.error(
            "Scenario ID cannot be empty."
        )
        return

    try:
        scenario = get_scenario_by_id(
            cleaned_scenario_id
        )

        analysis = get_scenario_analysis(
            cleaned_scenario_id
        )

        responses = get_all_responses(
            cleaned_scenario_id
        )

        evaluations = get_all_evaluations(
            cleaned_scenario_id
        )

    except Exception as error:
        st.error(
            "The scenario details could not be loaded."
        )

        st.exception(error)
        return

    if scenario is None:
        st.error(
            f"Scenario was not found: "
            f"{cleaned_scenario_id}"
        )
        return

    scenario_title = str(
        row_value(
            scenario,
            "scenario_title",
            "Untitled Scenario",
        )
    )

    scenario_text = str(
        row_value(
            scenario,
            "scenario_text",
            "",
        )
    )

    status = str(
        row_value(
            scenario,
            "status",
            "unknown",
        )
    )

    overall_score = row_value(
        scenario,
        "overall_score",
    )

    executive_summary = str(
        row_value(
            scenario,
            "executive_summary",
            "",
        )
    )

    overall_feedback = str(
        row_value(
            scenario,
            "overall_feedback",
            "",
        )
    )

    final_recommendations = (
        parse_json_list(
            row_value(
                scenario,
                "overall_recommendations",
            )
        )
    )

    created_at = format_datetime(
        row_value(
            scenario,
            "created_at",
        )
    )

    updated_at = format_datetime(
        row_value(
            scenario,
            "updated_at",
        )
    )

    header_columns = st.columns(
        [1, 5],
    )

    with header_columns[0]:
        if st.button(
            "← Back",
            use_container_width=True,
            key=(
                "details_back_"
                f"{cleaned_scenario_id}"
            ),
        ):
            st.session_state[
                "scenario_history_view"
            ] = "list"

            st.session_state[
                "history_selected_scenario_id"
            ] = None

            st.rerun()

    with header_columns[1]:
        st.title(
            "Scenario Details"
        )

        st.caption(
            scenario_title
        )

    information_columns = st.columns(5)

    information_values = (
        (
            "Scenario ID",
            cleaned_scenario_id,
        ),
        (
            "Status",
            status.title(),
        ),
        (
            "Created",
            created_at,
        ),
        (
            "Last Updated",
            updated_at,
        ),
        (
            "Overall Score",
            (
                f"{float(overall_score):.1f}/100"
                if overall_score is not None
                else "Not evaluated"
            ),
        ),
    )

    for column, (
        label,
        value,
    ) in zip(
        information_columns,
        information_values,
    ):
        with column:
            st.metric(
                label,
                value,
            )

    st.markdown("## Incident Scenario")

    with st.container(
        border=True
    ):
        st.write(
            scenario_text
        )

    st.markdown(
        "## Operational Summary"
    )

    if analysis is None:
        st.info(
            "No operational summary was saved."
        )

    else:
        render_operational_summary(
            analysis
        )

    st.markdown(
        "## Stakeholder Responses"
    )

    render_responses(
        responses
    )

    st.markdown(
        "## Overall Evaluation"
    )

    if overall_score is None:
        st.info(
            "This scenario has not been evaluated."
        )

    else:
        score_columns = st.columns(
            [1, 3],
        )

        with score_columns[0]:
            st.metric(
                "Overall Score",
                f"{float(overall_score):.1f}/100",
            )

        with score_columns[1]:
            with st.container(
                border=True
            ):
                st.markdown(
                    "### Executive Summary"
                )

                st.write(
                    executive_summary
                    or "Not available."
                )

        with st.container(
            border=True
        ):
            st.markdown(
                "### Overall Feedback"
            )

            st.write(
                overall_feedback
                or "Not available."
            )

        st.markdown(
            "### Final Recommendations"
        )

        if not final_recommendations:
            st.info(
                "No final recommendations "
                "were recorded."
            )

        else:
            for index, recommendation in enumerate(
                final_recommendations,
                start=1,
            ):
                st.markdown(
                    f"{index}. {recommendation}"
                )

    st.markdown(
        "## Stakeholder Evaluation Details"
    )

    render_evaluations(
        evaluations
    )

    render_report_section(
        scenario_id=cleaned_scenario_id,
        overall_score=overall_score,
    )