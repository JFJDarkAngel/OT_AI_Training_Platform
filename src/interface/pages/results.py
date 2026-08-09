from html import escape
from pathlib import Path

import streamlit as st

from src.database.evaluation_repository import get_all_evaluations
from src.database.scenario_repository import (
    get_scenario_analysis,
    get_scenario_by_id,
)
from src.evaluation.evaluation_service import get_saved_overall_evaluation
from src.reporting.report_generator import generate_report


DISPLAY = {
    "maintenance": "Maintenance",
    "operations": "Operations",
    "production": "Production",
    "ot_cybersecurity": "OT Cybersecurity",
}


def _go_to(page_name: str) -> None:
    st.session_state["page"] = page_name
    st.rerun()


def _score_band(score: float) -> tuple[str, str]:
    if score >= 80:
        return "Strong", "score-good"
    if score >= 60:
        return "Needs Improvement", "score-warning"
    return "High Attention", "score-bad"


def _display(value) -> str:
    if value is None:
        return "Unknown"

    text = str(value).strip()

    if not text:
        return "Unknown"

    return text.replace("_", " ").title()


def _priority_label(index: int) -> str:
    if index == 1:
        return "Priority 1"
    if index == 2:
        return "Priority 2"
    if index == 3:
        return "Priority 3"
    return f"Priority {index}"


def _load_results(scenario_id: str):
    evaluations = st.session_state.get("stakeholder_evaluations")
    overall = st.session_state.get("overall_evaluation")

    if not evaluations:
        evaluations = get_all_evaluations(scenario_id)

    if overall is None:
        overall = get_saved_overall_evaluation(scenario_id)

    return evaluations, overall


def render_results() -> None:
    scenario_id = st.session_state.get("active_scenario_id")

    if not scenario_id:
        st.warning("No active scenario was found.")
        if st.button("Go to Dashboard", type="primary"):
            _go_to("dashboard")
        return

    scenario = get_scenario_by_id(scenario_id)
    analysis_row = get_scenario_analysis(scenario_id)

    if scenario is None:
        st.error("The selected scenario could not be found.")
        return

    try:
        evaluations, overall = _load_results(scenario_id)
    except Exception as error:
        st.error(f"Could not load evaluation results: {error}")
        return

    if not evaluations or overall is None:
        st.warning("This scenario does not have a complete evaluation yet.")
        if st.button("Go to Evaluation", type="primary"):
            _go_to("evaluation")
        return

    analysis = dict(analysis_row) if analysis_row is not None else {}

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

    back_col, dash_col, _ = st.columns([1.2, 1.1, 4])

    with back_col:
        if st.button("← Evaluation", use_container_width=True):
            _go_to("evaluation")

    with dash_col:
        if st.button("Dashboard", use_container_width=True):
            _go_to("dashboard")

    st.markdown('<div class="page-title">Evaluation Results</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">'
        'Final team-level assessment with stakeholder performance, prioritized recommendations, '
        'supporting references, and report export.'
        '</div>',
        unsafe_allow_html=True,
    )

    overall_score = float(overall.overall_score)
    band_label, band_class = _score_band(overall_score)

    top_left, top_mid, top_right = st.columns([1.15, 1.4, 1.1])

    with top_left:
        st.markdown(
            f"""
            <div class="results-overall-card">
                <div class="results-card-label">Overall Score</div>
                <div class="results-overall-score">{overall_score:.1f}</div>
                <div class="results-score-unit">/ 100</div>
                <div class="results-score-band {band_class}">{escape(band_label)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with top_mid:
        st.markdown(
            f"""
            <div class="results-info-card">
                <div class="results-card-label">Scenario Information</div>
                <div class="results-scenario-title">{escape(str(scenario["scenario_title"]))}</div>
                <div class="results-scenario-id">{escape(str(scenario_id))}</div>
                <div class="results-mini-grid">
                    <div><span>Severity</span><strong>{escape(_display(analysis.get("severity")))}</strong></div>
                    <div><span>Asset / Area</span><strong>{escape(_display(analysis.get("asset_area")))}</strong></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with top_right:
        st.markdown(
            """
            <div class="results-info-card">
                <div class="results-card-label">Report</div>
                <div class="results-report-title">Evaluation Report</div>
                <div class="results-report-note">
                    Generate a PDF containing the scenario, stakeholder responses,
                    evaluation findings, references, and overall assessment.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        try:
            report_path = generate_report(scenario_id)
            report_bytes = Path(report_path).read_bytes()

            st.download_button(
                "Download Report",
                data=report_bytes,
                file_name=f"{scenario_id}_report.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
            )

        except Exception as error:
            st.error(f"Report could not be generated: {error}")

    st.write("")

    st.markdown('<div class="section-title">Involved Stakeholders</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">'
        'Individual role performance contributing to the overall team score.'
        '</div>',
        unsafe_allow_html=True,
    )

    evaluation_map = {
        evaluation.stakeholder: evaluation
        for evaluation in evaluations
    }

    score_columns = st.columns(4)

    for column, stakeholder in zip(score_columns, DISPLAY):
        evaluation = evaluation_map.get(stakeholder)

        if evaluation is None:
            continue

        score = float(evaluation.score)
        label, css_class = _score_band(score)

        with column:
            st.markdown(
                f"""
                <div class="stakeholder-result-card">
                    <div class="stakeholder-result-name">{DISPLAY[stakeholder]}</div>
                    <div class="stakeholder-result-score">{score:.1f}<span>/100</span></div>
                    <div class="results-score-band {css_class}">{escape(label)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")

    left, right = st.columns([1.55, 1], gap="large")

    with left:
        st.markdown(
            f"""
            <div class="panel-card">
                <div class="section-title">Evaluation Summary</div>
                <div class="results-copy">
                    {escape(overall.executive_summary)}
                </div>
                <div class="results-divider"></div>
                <div class="section-title" style="font-size:.9rem;">Overall Feedback</div>
                <div class="results-copy">
                    {escape(overall.overall_feedback)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            """
            <div class="panel-card">
                <div class="section-title">Operational Snapshot</div>
            """,
            unsafe_allow_html=True,
        )

        snapshot = [
            ("PLC", analysis.get("plc_status")),
            ("HMI", analysis.get("hmi_status")),
            ("Network", analysis.get("network_status")),
            ("Process State", analysis.get("last_known_state")),
            (
                "Active Alarms",
                "Unknown"
                if analysis.get("active_alarms") is None
                else analysis.get("active_alarms"),
            ),
        ]

        for label, value in snapshot:
            st.markdown(
                f"""
                <div class="results-snapshot-row">
                    <span>{escape(label)}</span>
                    <strong>{escape(_display(value))}</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    st.markdown('<div class="section-title">Prioritized Recommendations</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">'
        'Recommendations are shown in the order returned by the overall evaluator.'
        '</div>',
        unsafe_allow_html=True,
    )

    if overall.final_recommendations:
        for index, recommendation in enumerate(overall.final_recommendations, start=1):
            st.markdown(
                f"""
                <div class="recommendation-row">
                    <div class="recommendation-priority">{escape(_priority_label(index))}</div>
                    <div class="recommendation-text">{escape(str(recommendation))}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No final recommendations were recorded.")

    st.write("")
    st.markdown('<div class="section-title">Detailed Stakeholder Evaluation</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">'
        'Open a stakeholder to review findings, recommendations, and supporting references.'
        '</div>',
        unsafe_allow_html=True,
    )

    for stakeholder in DISPLAY:
        evaluation = evaluation_map.get(stakeholder)

        if evaluation is None:
            continue

        with st.expander(
            f"{DISPLAY[stakeholder]} — {float(evaluation.score):.1f}/100"
        ):
            st.markdown("**Feedback**")
            st.write(evaluation.feedback)

            a, b, c = st.columns(3)

            with a:
                st.markdown("**Correct Actions**")
                if evaluation.correct_actions:
                    for item in evaluation.correct_actions:
                        st.write(f"✓ {item}")
                else:
                    st.caption("None recorded.")

            with b:
                st.markdown("**Missing Actions**")
                if evaluation.missing_actions:
                    for item in evaluation.missing_actions:
                        st.write(f"• {item}")
                else:
                    st.caption("None recorded.")

            with c:
                st.markdown("**Incorrect / Unsafe Actions**")
                if evaluation.incorrect_actions:
                    for item in evaluation.incorrect_actions:
                        st.write(f"• {item}")
                else:
                    st.caption("None recorded.")

            st.markdown("**Role Recommendations**")
            if evaluation.recommendations:
                for item in evaluation.recommendations:
                    st.write(f"• {item}")
            else:
                st.caption("None recorded.")

            st.markdown("**References**")
            if evaluation.references:
                for reference in evaluation.references:
                    st.write(
                        f"• {reference.document_title} — page {reference.page_number} "
                        f"({reference.file_name}, {reference.chunk_id})"
                    )
                    if reference.relevance:
                        st.caption(reference.relevance)
            else:
                st.caption("No references were recorded.")

    st.write("")
    done_col, _ = st.columns([1.45, 4])

    with done_col:
        if st.button("Finish & Return to Dashboard", type="primary", use_container_width=True):
            st.session_state["evaluation_complete"] = False
            st.session_state.pop("stakeholder_evaluations", None)
            st.session_state.pop("overall_evaluation", None)
            _go_to("dashboard")
