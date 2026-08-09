from html import escape

import streamlit as st

from src.database.response_repository import get_all_responses
from src.evaluation.evaluation_service import evaluate_complete_scenario


DISPLAY = {
    "maintenance": "Maintenance",
    "operations": "Operations",
    "production": "Production",
    "ot_cybersecurity": "OT Cybersecurity",
}


def _go_to(page_name: str) -> None:
    st.session_state["page"] = page_name
    st.rerun()


def _response_map(scenario_id: str) -> dict[str, str]:
    return {
        str(row["stakeholder"]): str(row["answer_text"])
        for row in get_all_responses(scenario_id)
    }


def render_evaluation() -> None:
    scenario_id = st.session_state.get("active_scenario_id")
    scenario_title = st.session_state.get("active_scenario_title")
    scenario_text = st.session_state.get("active_scenario_text")
    analysis = st.session_state.get("active_scenario_analysis") or {}

    if not scenario_id or not scenario_text:
        st.warning("No active scenario was found.")
        if st.button("Go to Dashboard", type="primary"):
            _go_to("dashboard")
        return

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
        if st.button("← Responses", use_container_width=True):
            _go_to("stakeholder_response")

    with dash_col:
        if st.button("Dashboard", use_container_width=True):
            _go_to("dashboard")

    st.markdown('<div class="page-title">AI Evaluation</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">'
        'Evaluate the four stakeholder responses using role responsibilities '
        'and stakeholder-relevant RAG evidence.'
        '</div>',
        unsafe_allow_html=True,
    )

    try:
        responses = _response_map(scenario_id)
    except Exception as error:
        st.error(f"Could not load responses: {error}")
        return

    missing = [
        stakeholder
        for stakeholder in DISPLAY
        if not responses.get(stakeholder, "").strip()
    ]

    if missing:
        st.warning(
            "Missing responses: "
            + ", ".join(DISPLAY[stakeholder] for stakeholder in missing)
        )
        if st.button("Return to Responses", type="primary"):
            _go_to("stakeholder_response")
        return

    st.markdown(
        f"""
        <div class="evaluation-ready-card">
            <div>
                <div class="evaluation-ready-title">Ready for evaluation</div>
                <div class="evaluation-ready-sub">{escape(str(scenario_title or scenario_id))}</div>
            </div>
            <div class="evaluation-ready-count">4 / 4 responses</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(4)

    for col, stakeholder in zip(cols, DISPLAY):
        with col:
            st.markdown(
                f"""
                <div class="evaluation-role-card">
                    <div class="evaluation-role-check">✓</div>
                    <div class="evaluation-role-name">{DISPLAY[stakeholder]}</div>
                    <div class="evaluation-role-status">Response saved</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")

    if not st.session_state.get("evaluation_complete", False):
        st.markdown(
            """
            <div class="panel-card">
                <div class="section-title">Evaluation Process</div>
                <div class="section-note">
                    The system evaluates each role separately, then produces the overall team assessment.
                </div>
                <div class="evaluation-process-row"><span>1</span> Retrieve stakeholder-relevant evidence</div>
                <div class="evaluation-process-row"><span>2</span> Evaluate all four role responses</div>
                <div class="evaluation-process-row"><span>3</span> Save scores, feedback, actions, and references</div>
                <div class="evaluation-process-row"><span>4</span> Generate the overall team evaluation</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        run_col, _ = st.columns([1.5, 4])

        with run_col:
            if st.button("Run AI Evaluation", type="primary", use_container_width=True):
                try:
                    progress = st.progress(10, text="Preparing evaluation...")

                    with st.spinner(
                        "Running RAG-assisted AI evaluation for all four stakeholders..."
                    ):
                        progress.progress(30, text="Evaluating stakeholder responses...")

                        stakeholder_evaluations, overall_evaluation = (
                            evaluate_complete_scenario(
                                scenario_id=scenario_id,
                                scenario_text=scenario_text,
                                stakeholder_responses=responses,
                                scenario_analysis=analysis,
                                top_k=5,
                            )
                        )

                        progress.progress(90, text="Preparing overall assessment...")

                    st.session_state["stakeholder_evaluations"] = stakeholder_evaluations
                    st.session_state["overall_evaluation"] = overall_evaluation
                    st.session_state["evaluation_complete"] = True

                    progress.progress(100, text="Evaluation complete.")
                    st.rerun()

                except Exception as error:
                    st.error(f"Evaluation failed: {error}")

        return

    evaluations = st.session_state.get("stakeholder_evaluations") or []
    overall = st.session_state.get("overall_evaluation")

    if not evaluations or overall is None:
        st.session_state["evaluation_complete"] = False
        st.error("Evaluation state is incomplete. Please run the evaluation again.")
        return

    st.success("Evaluation completed successfully.")

    score_cols = st.columns(5)

    with score_cols[0]:
        st.markdown(
            f"""
            <div class="evaluation-score-card overall">
                <div class="evaluation-score-label">Overall</div>
                <div class="evaluation-score-value">{float(overall.overall_score):.1f}</div>
                <div class="evaluation-score-unit">/ 100</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    for idx, evaluation in enumerate(evaluations, start=1):
        with score_cols[idx]:
            st.markdown(
                f"""
                <div class="evaluation-score-card">
                    <div class="evaluation-score-label">{DISPLAY[evaluation.stakeholder]}</div>
                    <div class="evaluation-score-value">{float(evaluation.score):.1f}</div>
                    <div class="evaluation-score-unit">/ 100</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")

    st.markdown(
        f"""
        <div class="panel-card">
            <div class="section-title">Executive Summary</div>
            <div style="color:#4F5D70;line-height:1.65;font-size:.9rem;">
                {escape(overall.executive_summary)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for evaluation in evaluations:
        with st.expander(
            f"{DISPLAY[evaluation.stakeholder]} — {evaluation.score:.1f}/100"
        ):
            st.write(evaluation.feedback)

            if evaluation.correct_actions:
                st.markdown("**Correct actions**")
                for item in evaluation.correct_actions:
                    st.write(f"✓ {item}")

            if evaluation.missing_actions:
                st.markdown("**Missing actions**")
                for item in evaluation.missing_actions:
                    st.write(f"• {item}")

            if evaluation.incorrect_actions:
                st.markdown("**Incorrect / unsafe actions**")
                for item in evaluation.incorrect_actions:
                    st.write(f"• {item}")

            if evaluation.recommendations:
                st.markdown("**Recommendations**")
                for item in evaluation.recommendations:
                    st.write(f"• {item}")

    next_col, _ = st.columns([1.55, 4])

    with next_col:
        if st.button("Continue to Results →", type="primary", use_container_width=True):
            _go_to("results")
