from html import escape
from pathlib import Path

import streamlit as st

from src.database.scenario_repository import (
    get_scenario_analysis,
    get_scenario_by_id,
    get_scenario_count,
    get_scenario_history,
)
from src.reporting.report_generator import generate_report


def _go_to(page_name: str) -> None:
    st.session_state["page"] = page_name
    st.rerun()


def _display(value) -> str:
    if value is None:
        return "Unknown"

    text = str(value).strip()

    if not text:
        return "Unknown"

    return text.replace("_", " ").title()


def _load_scenario_into_session(scenario_id: str) -> str:
    scenario = get_scenario_by_id(scenario_id)
    analysis_row = get_scenario_analysis(scenario_id)

    if scenario is None:
        raise ValueError("Scenario could not be found.")

    analysis = (
        dict(analysis_row)
        if analysis_row is not None
        else {}
    )

    st.session_state["active_scenario_id"] = scenario_id
    st.session_state["active_scenario_title"] = scenario["scenario_title"]
    st.session_state["active_scenario_text"] = scenario["scenario_text"]
    st.session_state["active_scenario_analysis"] = analysis

    status = str(scenario["status"]).strip().lower()

    if status == "evaluated":
        return "results"

    return "hmi_visualization"


def render_scenario_history() -> None:
    st.markdown(
        """
        <div class="app-header">
            <div class="brand-wrap">
                <div class="brand-icon">🛡️</div>
                <div>
                    <div class="brand-title">AI-Assisted OT Incident Response</div>
                    <div class="brand-subtitle">Industrial incident-response evaluation platform</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    back_col, new_col, _ = st.columns([1.15, 1.35, 4.5])

    with back_col:
        if st.button(
            "← Dashboard",
            use_container_width=True,
        ):
            _go_to("dashboard")

    with new_col:
        if st.button(
            "＋ New Scenario",
            type="primary",
            use_container_width=True,
        ):
            _go_to("new_scenario")

    st.markdown(
        '<div class="page-title">Scenario History</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="page-subtitle">'
        'Search, filter, reopen, and review previously saved incident-response scenarios.'
        '</div>',
        unsafe_allow_html=True,
    )

    total = get_scenario_count("all")
    evaluated = get_scenario_count("evaluated")
    drafts = get_scenario_count("draft")

    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric("Total Scenarios", total)

    with m2:
        st.metric("Evaluated", evaluated)

    with m3:
        st.metric("Drafts", drafts)

    st.write("")

    search_col, filter_col = st.columns([2.5, 1])

    with search_col:
        search_text = st.text_input(
            "Search scenarios",
            placeholder="Search by Scenario ID or title",
        )

    with filter_col:
        status_filter = st.selectbox(
            "Status",
            options=[
                "all",
                "draft",
                "evaluated",
            ],
            format_func=lambda value: value.title(),
        )

    try:
        rows = get_scenario_history(
            search_text=search_text,
            status=status_filter,
        )
    except Exception as error:
        st.error(f"Could not load scenario history: {error}")
        return

    st.caption(
        f"{len(rows)} scenario{'s' if len(rows) != 1 else ''} shown"
    )

    if not rows:
        st.info("No scenarios match the current search and filter.")
        return

    for row in rows:
        scenario_id = str(row["scenario_id"])
        status = str(row["status"]).strip().lower()
        severity = _display(row["severity"])
        score = row["overall_score"]

        score_text = (
            "—"
            if score is None
            else f"{float(score):.1f}/100"
        )

        history_html = (
            '<div class="history-card">'
            '<div class="history-card-top">'
            '<div>'
            f'<div class="history-title">{escape(str(row["scenario_title"]))}</div>'
            f'<div class="history-id">{escape(scenario_id)}</div>'
            '</div>'
            '<div class="history-status-wrap">'
            f'<span class="history-pill">{escape(status.title())}</span>'
            '</div>'
            '</div>'
            '<div class="history-meta-grid">'
            '<div>'
            '<span>Severity</span>'
            f'<strong>{escape(severity)}</strong>'
            '</div>'
            '<div>'
            '<span>Score</span>'
            f'<strong>{escape(score_text)}</strong>'
            '</div>'
            '<div>'
            '<span>Asset / Area</span>'
            f'<strong>{escape(_display(row["asset_area"]))}</strong>'
            '</div>'
            '<div>'
            '<span>Created</span>'
            f'<strong>{escape(str(row["created_at"]))}</strong>'
            '</div>'
            '</div>'
            '</div>'
        )

        st.markdown(
            history_html,
            unsafe_allow_html=True,
        )

        open_col, report_col, spacer = st.columns([1.35, 1.35, 4])

        with open_col:
            open_label = (
                "Open Results"
                if status == "evaluated"
                else "Continue Scenario"
            )

            if st.button(
                open_label,
                key=f"open_{scenario_id}",
                type="primary",
                use_container_width=True,
            ):
                try:
                    page = _load_scenario_into_session(
                        scenario_id
                    )

                    if page == "results":
                        st.session_state.pop(
                            "stakeholder_evaluations",
                            None,
                        )
                        st.session_state.pop(
                            "overall_evaluation",
                            None,
                        )

                    _go_to(page)

                except Exception as error:
                    st.error(
                        f"Could not open scenario: {error}"
                    )

        with report_col:
            if status == "evaluated":
                try:
                    report_path_value = row["report_path"]
                except Exception:
                    report_path_value = None

                if report_path_value:
                    path = Path(
                        str(report_path_value)
                    )

                    if path.exists():
                        st.download_button(
                            "Download Report",
                            data=path.read_bytes(),
                            file_name=f"{scenario_id}_report.pdf",
                            mime="application/pdf",
                            key=f"download_{scenario_id}",
                            use_container_width=True,
                        )
                    else:
                        if st.button(
                            "Generate Report",
                            key=f"generate_{scenario_id}",
                            use_container_width=True,
                        ):
                            try:
                                generated = generate_report(
                                    scenario_id
                                )

                                st.download_button(
                                    "Download Generated Report",
                                    data=Path(generated).read_bytes(),
                                    file_name=f"{scenario_id}_report.pdf",
                                    mime="application/pdf",
                                    key=f"generated_download_{scenario_id}",
                                    use_container_width=True,
                                )

                            except Exception as error:
                                st.error(
                                    f"Could not generate report: {error}"
                                )

                else:
                    if st.button(
                        "Generate Report",
                        key=f"generate_{scenario_id}",
                        use_container_width=True,
                    ):
                        try:
                            generated = generate_report(
                                scenario_id
                            )

                            st.success(
                                "Report generated. Click the button below to download it."
                            )

                            st.download_button(
                                "Download Generated Report",
                                data=Path(generated).read_bytes(),
                                file_name=f"{scenario_id}_report.pdf",
                                mime="application/pdf",
                                key=f"generated_download_{scenario_id}",
                                use_container_width=True,
                            )

                        except Exception as error:
                            st.error(
                                f"Could not generate report: {error}"
                            )

        st.write("")