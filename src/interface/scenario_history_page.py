from datetime import datetime
from html import escape
from math import ceil
from textwrap import dedent
from typing import Any

import streamlit as st

from src.database.scenario_repository import (
    get_scenario_history,
)
from src.interface.scenario_details_page import (
    show_scenario_details_page,
)


PAGE_SIZE = 8


STATUS_OPTIONS = {
    "All Status": "all",
    "Draft": "draft",
    "Evaluated": "evaluated",
}


STATUS_DISPLAY_NAMES = {
    "draft": "In Progress",
    "evaluated": "Completed",
}


def inject_history_styles() -> None:
    """
    Add styling for the Scenario History page.
    """

    st.markdown(
        dedent(
            """
            <style>
            .history-page-title {
                margin: 0;
                color: #0d1f3c;
                font-size: 2.45rem;
                line-height: 1.2;
                font-weight: 850;
            }

            .history-page-subtitle {
                margin-top: 0.4rem;
                margin-bottom: 1.5rem;
                color: #64748b;
                font-size: 0.96rem;
            }

            .history-guide-card {
                background: #ffffff;
                border: 1px solid #dce6f2;
                border-radius: 16px;
                padding: 1rem 1.15rem;
                min-height: 112px;
                box-shadow:
                    0 8px 20px rgba(15, 40, 75, 0.04);
                text-align: center;
            }

            .history-guide-icon {
                color: #1759c7;
                font-size: 1.55rem;
                font-weight: 900;
                margin-bottom: 0.45rem;
            }

            .history-guide-label {
                color: #142b4c;
                font-size: 0.82rem;
                font-weight: 750;
                line-height: 1.35;
            }

            .history-panel {
                background: #ffffff;
                border: 1px solid #dce6f2;
                border-radius: 18px;
                padding: 1.25rem;
                margin-top: 1.1rem;
                box-shadow:
                    0 10px 28px rgba(15, 40, 75, 0.05);
            }

            .history-summary-card {
                background: #ffffff;
                border: 1px solid #dce6f2;
                border-radius: 15px;
                padding: 0.95rem 1rem;
                min-height: 105px;
                box-shadow:
                    0 6px 16px rgba(15, 40, 75, 0.04);
            }

            .history-summary-label {
                color: #64748b;
                font-size: 0.78rem;
                margin-bottom: 0.35rem;
            }

            .history-summary-value {
                color: #1759c7;
                font-size: 1.65rem;
                line-height: 1.1;
                font-weight: 850;
            }

            .history-table-header {
                background: #f5f8fc;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 0.85rem 0.95rem;
                margin-top: 1rem;
                margin-bottom: 0.35rem;
                color: #142b4c;
                font-size: 0.84rem;
                font-weight: 800;
            }

            .history-row-card {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                padding: 0.75rem 0.85rem;
                margin-bottom: 0.4rem;
                min-height: 72px;
                box-shadow:
                    0 4px 14px rgba(15, 40, 75, 0.025);
            }

            .history-row-title {
                color: #142b4c;
                font-size: 0.9rem;
                font-weight: 780;
                line-height: 1.35;
                overflow-wrap: anywhere;
            }

            .history-row-id {
                color: #64748b;
                font-size: 0.72rem;
                margin-top: 0.18rem;
                overflow-wrap: anywhere;
            }

            .history-row-text {
                color: #40536d;
                font-size: 0.82rem;
                line-height: 1.35;
            }

            .history-status {
                display: inline-block;
                border-radius: 8px;
                padding: 0.3rem 0.58rem;
                font-size: 0.75rem;
                font-weight: 800;
            }

            .history-status.draft {
                background: #eaf3ff;
                color: #1759c7;
            }

            .history-status.evaluated {
                background: #eaf8ef;
                color: #15803d;
            }

            .history-status.unknown {
                background: #f1f5f9;
                color: #64748b;
            }

            .history-severity {
                display: inline-block;
                border-radius: 8px;
                padding: 0.3rem 0.58rem;
                font-size: 0.75rem;
                font-weight: 800;
                text-transform: capitalize;
            }

            .history-severity.low {
                background: #eaf8ef;
                color: #15803d;
            }

            .history-severity.medium {
                background: #fff6e8;
                color: #d97706;
            }

            .history-severity.high {
                background: #fff0f0;
                color: #dc2626;
            }

            .history-severity.critical {
                background: #fee2e2;
                color: #991b1b;
            }

            .history-severity.unknown {
                background: #f1f5f9;
                color: #64748b;
            }

            .history-score {
                color: #1759c7;
                font-size: 0.95rem;
                font-weight: 850;
            }

            .history-empty-card {
                background: #f8fbff;
                border: 1px dashed #bfd2eb;
                border-radius: 16px;
                padding: 2rem;
                text-align: center;
                margin-top: 1rem;
            }

            .history-empty-title {
                color: #142b4c;
                font-size: 1.05rem;
                font-weight: 800;
                margin-bottom: 0.35rem;
            }

            .history-empty-text {
                color: #64748b;
                font-size: 0.88rem;
            }

            .pagination-text {
                color: #64748b;
                font-size: 0.82rem;
                text-align: center;
                padding-top: 0.8rem;
            }

            div.stButton > button {
                border-radius: 10px;
                min-height: 42px;
                font-weight: 700;
            }

            @media (max-width: 1050px) {
                .history-page-title {
                    font-size: 2rem;
                }
            }
            </style>
            """
        ),
        unsafe_allow_html=True,
    )


def initialize_history_state() -> None:
    """
    Initialize Scenario History session-state values.
    """

    defaults = {
        "history_search": "",
        "history_status_filter": "All Status",
        "history_page_number": 1,
        "history_selected_scenario_id": None,
        "scenario_history_view": "list",
        "details_report_path": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def row_value(
    row: Any,
    key: str,
    default: Any = None,
) -> Any:
    """
    Safely retrieve a value from sqlite3.Row or dictionary.
    """

    try:
        value = row[key]

    except (
        KeyError,
        IndexError,
        TypeError,
    ):
        return default

    return default if value is None else value


def format_datetime(
    value: Any,
) -> str:
    """
    Convert an SQLite date value into readable text.
    """

    if value is None:
        return "Unknown"

    text = str(value).strip()

    if not text:
        return "Unknown"

    formats = (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S.%f",
    )

    for date_format in formats:
        try:
            parsed_date = datetime.strptime(
                text,
                date_format,
            )

            return parsed_date.strftime(
                "%d %b %Y  %I:%M %p"
            )

        except ValueError:
            continue

    return text


def normalize_status(
    status: Any,
) -> str:
    """
    Normalize the scenario status for styling.
    """

    normalized = str(
        status or "unknown"
    ).strip().lower()

    if normalized in {
        "draft",
        "evaluated",
    }:
        return normalized

    return "unknown"


def status_display_name(
    status: Any,
) -> str:
    """
    Return a readable status label.
    """

    normalized = normalize_status(
        status
    )

    return STATUS_DISPLAY_NAMES.get(
        normalized,
        "Unknown",
    )


def normalize_severity(
    severity: Any,
) -> str:
    """
    Normalize the scenario severity.
    """

    normalized = str(
        severity or "unknown"
    ).strip().lower()

    if normalized in {
        "low",
        "medium",
        "high",
        "critical",
    }:
        return normalized

    return "unknown"


def render_page_header() -> None:
    """
    Render the page title and feature cards.
    """

    header_columns = st.columns(
        [2.5, 2],
        gap="large",
    )

    with header_columns[0]:
        st.markdown(
            (
                '<div class="history-page-title">'
                'Scenario History'
                '</div>'
            ),
            unsafe_allow_html=True,
        )

        st.markdown(
            (
                '<div class="history-page-subtitle">'
                'View and explore all previously created '
                'industrial incident scenarios.'
                '</div>'
            ),
            unsafe_allow_html=True,
        )

    with header_columns[1]:
        st.markdown(
            "**You can view**"
        )

        guide_columns = st.columns(4)

        guide_items = (
            ("▤", "Scenario Details"),
            ("♙", "Stakeholder Responses"),
            ("↗", "Evaluation Results"),
            ("▣", "PDF Report"),
        )

        for column, (
            icon,
            label,
        ) in zip(
            guide_columns,
            guide_items,
        ):
            with column:
                st.markdown(
                    (
                        '<div class="history-guide-card">'
                        '<div class="history-guide-icon">'
                        f'{escape(icon)}'
                        '</div>'
                        '<div class="history-guide-label">'
                        f'{escape(label)}'
                        '</div>'
                        '</div>'
                    ),
                    unsafe_allow_html=True,
                )


def render_summary_cards(
    scenarios: list[Any],
) -> None:
    """
    Render Scenario History summary metrics.
    """

    total_count = len(
        scenarios
    )

    draft_count = sum(
        1
        for row in scenarios
        if normalize_status(
            row_value(
                row,
                "status",
            )
        ) == "draft"
    )

    evaluated_count = sum(
        1
        for row in scenarios
        if normalize_status(
            row_value(
                row,
                "status",
            )
        ) == "evaluated"
    )

    report_count = sum(
        1
        for row in scenarios
        if row_value(
            row,
            "report_path",
        )
    )

    metric_columns = st.columns(4)

    metric_values = (
        (
            "Matching Scenarios",
            total_count,
        ),
        (
            "In Progress",
            draft_count,
        ),
        (
            "Completed",
            evaluated_count,
        ),
        (
            "Reports Available",
            report_count,
        ),
    )

    for column, (
        label,
        value,
    ) in zip(
        metric_columns,
        metric_values,
    ):
        with column:
            st.markdown(
                (
                    '<div class="history-summary-card">'
                    '<div class="history-summary-label">'
                    f'{escape(label)}'
                    '</div>'
                    '<div class="history-summary-value">'
                    f'{value}'
                    '</div>'
                    '</div>'
                ),
                unsafe_allow_html=True,
            )


def render_table_header() -> None:
    """
    Render the Scenario History table header.
    """

    header_columns = st.columns(
        [
            3.4,
            1.65,
            1.15,
            1.05,
            0.9,
            0.7,
        ],
        gap="small",
    )

    labels = (
        "Scenario Title",
        "Date Created",
        "Status",
        "Severity",
        "Score",
        "Actions",
    )

    for column, label in zip(
        header_columns,
        labels,
    ):
        with column:
            st.markdown(
                (
                    '<div class="history-table-header">'
                    f'{escape(label)}'
                    '</div>'
                ),
                unsafe_allow_html=True,
            )


def render_scenario_row(
    scenario: Any,
) -> None:
    """
    Render one Scenario History row.
    """

    scenario_id = str(
        row_value(
            scenario,
            "scenario_id",
            "Unknown",
        )
    )

    scenario_title = str(
        row_value(
            scenario,
            "scenario_title",
            "Untitled Scenario",
        )
    )

    created_at = format_datetime(
        row_value(
            scenario,
            "created_at",
        )
    )

    status = normalize_status(
        row_value(
            scenario,
            "status",
        )
    )

    severity = normalize_severity(
        row_value(
            scenario,
            "severity",
        )
    )

    overall_score = row_value(
        scenario,
        "overall_score",
    )

    row_columns = st.columns(
        [
            3.4,
            1.65,
            1.15,
            1.05,
            0.9,
            0.7,
        ],
        gap="small",
        vertical_alignment="center",
    )

    with row_columns[0]:
        st.markdown(
            (
                '<div class="history-row-card">'
                '<div class="history-row-title">'
                f'▤ &nbsp;{escape(scenario_title)}'
                '</div>'
                '<div class="history-row-id">'
                f'{escape(scenario_id)}'
                '</div>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )

    with row_columns[1]:
        st.markdown(
            (
                '<div class="history-row-card">'
                '<div class="history-row-text">'
                f'{escape(created_at)}'
                '</div>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )

    with row_columns[2]:
        st.markdown(
            (
                '<div class="history-row-card">'
                f'<span class="history-status {status}">'
                f'{escape(status_display_name(status))}'
                '</span>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )

    with row_columns[3]:
        st.markdown(
            (
                '<div class="history-row-card">'
                f'<span class="history-severity {severity}">'
                f'{escape(severity.title())}'
                '</span>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )

    with row_columns[4]:
        score_text = (
            f"{float(overall_score):.1f}"
            if overall_score is not None
            else "—"
        )

        st.markdown(
            (
                '<div class="history-row-card">'
                '<div class="history-score">'
                f'{escape(score_text)}'
                '</div>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )

    with row_columns[5]:
        if st.button(
            "›",
            key=(
                "view_scenario_"
                f"{scenario_id}"
            ),
            help="View scenario details",
            use_container_width=True,
        ):
            st.session_state[
                "history_selected_scenario_id"
            ] = scenario_id

            st.session_state[
                "scenario_history_view"
            ] = "details"

            st.session_state[
                "details_report_path"
            ] = None

            st.rerun()


def render_empty_state() -> None:
    """
    Render an empty result state.
    """

    st.markdown(
        (
            '<div class="history-empty-card">'
            '<div class="history-empty-title">'
            'No scenarios were found'
            '</div>'
            '<div class="history-empty-text">'
            'Try changing the search text or status filter.'
            '</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )


def show_scenario_history_page() -> None:
    """
    Render the Scenario History list or Scenario Details page.
    """

    inject_history_styles()
    initialize_history_state()

    history_view = st.session_state.get(
        "scenario_history_view",
        "list",
    )

    if history_view == "details":
        selected_scenario_id = (
            st.session_state.get(
                "history_selected_scenario_id"
            )
        )

        if not selected_scenario_id:
            st.session_state[
                "scenario_history_view"
            ] = "list"

            st.rerun()

        show_scenario_details_page(
            scenario_id=selected_scenario_id
        )

        return

    render_page_header()

    st.markdown(
        '<div class="history-panel">',
        unsafe_allow_html=True,
    )

    filter_columns = st.columns(
        [
            3,
            1.4,
            1,
        ],
        gap="large",
    )

    with filter_columns[0]:
        search_text = st.text_input(
            "Search scenarios",
            key="history_search",
            placeholder=(
                "Search by Scenario ID or title..."
            ),
            label_visibility="collapsed",
        )

    with filter_columns[1]:
        selected_status_label = st.selectbox(
            "Status",
            options=list(
                STATUS_OPTIONS.keys()
            ),
            key="history_status_filter",
            label_visibility="collapsed",
        )

    with filter_columns[2]:
        if st.button(
            "Clear Filters",
            use_container_width=True,
            key="clear_history_filters",
        ):
            st.session_state[
                "history_search"
            ] = ""

            st.session_state[
                "history_status_filter"
            ] = "All Status"

            st.session_state[
                "history_page_number"
            ] = 1

            st.rerun()

    selected_status = STATUS_OPTIONS[
        selected_status_label
    ]

    try:
        scenarios = get_scenario_history(
            search_text=search_text,
            status=selected_status,
        )

    except Exception as error:
        st.error(
            "The scenario history could not be loaded."
        )

        st.exception(error)

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

        return

    render_summary_cards(
        scenarios=scenarios
    )

    if not scenarios:
        render_empty_state()

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )

        return

    total_pages = max(
        1,
        ceil(
            len(scenarios)
            / PAGE_SIZE
        ),
    )

    current_page = int(
        st.session_state.get(
            "history_page_number",
            1,
        )
    )

    if current_page > total_pages:
        current_page = total_pages

        st.session_state[
            "history_page_number"
        ] = current_page

    if current_page < 1:
        current_page = 1

        st.session_state[
            "history_page_number"
        ] = current_page

    start_index = (
        current_page - 1
    ) * PAGE_SIZE

    end_index = (
        start_index
        + PAGE_SIZE
    )

    visible_scenarios = scenarios[
        start_index:end_index
    ]

    render_table_header()

    for scenario in visible_scenarios:
        render_scenario_row(
            scenario=scenario
        )

    pagination_columns = st.columns(
        [
            1,
            2,
            1,
        ]
    )

    with pagination_columns[0]:
        previous_clicked = st.button(
            "← Previous",
            disabled=(
                current_page <= 1
            ),
            use_container_width=True,
            key="history_previous_page",
        )

        if previous_clicked:
            st.session_state[
                "history_page_number"
            ] = current_page - 1

            st.rerun()

    with pagination_columns[1]:
        first_item = (
            start_index + 1
        )

        last_item = min(
            end_index,
            len(scenarios),
        )

        st.markdown(
            (
                '<div class="pagination-text">'
                f'Showing {first_item}–{last_item} '
                f'of {len(scenarios)} scenarios'
                '<br>'
                f'Page {current_page} of {total_pages}'
                '</div>'
            ),
            unsafe_allow_html=True,
        )

    with pagination_columns[2]:
        next_clicked = st.button(
            "Next →",
            disabled=(
                current_page >= total_pages
            ),
            use_container_width=True,
            key="history_next_page",
        )

        if next_clicked:
            st.session_state[
                "history_page_number"
            ] = current_page + 1

            st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )