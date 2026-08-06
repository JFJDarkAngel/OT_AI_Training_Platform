from html import escape
from textwrap import dedent
from typing import Any

import streamlit as st

from src.evaluation.evaluation_service import (
    evaluate_complete_scenario,
)
from src.evaluation.models import (
    OverallEvaluation,
    StakeholderEvaluation,
)


STAKEHOLDER_DISPLAY_NAMES = {
    "maintenance": "Maintenance",
    "operations": "Operations",
    "production": "Production",
    "ot_cybersecurity": "OT Cybersecurity",
}

STAKEHOLDER_ORDER = (
    "maintenance",
    "operations",
    "production",
    "ot_cybersecurity",
)


def inject_evaluation_styles() -> None:
    """
    Add styling for the Evaluation page.
    """

    st.markdown(
        dedent(
            """
            <style>
            .evaluation-title {
                font-size: 2.4rem;
                font-weight: 800;
                color: #0d1f3c;
                margin-bottom: 0.3rem;
            }

            .evaluation-subtitle {
                color: #64748b;
                font-size: 0.95rem;
                margin-bottom: 1.2rem;
            }

            .evaluation-context-card {
                background: #ffffff;
                border: 1px solid #dce6f2;
                border-radius: 16px;
                padding: 1rem 1.2rem;
                margin-bottom: 1rem;
                box-shadow:
                    0 8px 20px rgba(15, 40, 75, 0.05);
            }

            .evaluation-context-grid {
                display: grid;
                grid-template-columns: 1fr 2fr;
                gap: 1rem;
            }

            .context-label {
                font-size: 0.78rem;
                color: #64748b;
                margin-bottom: 0.3rem;
            }

            .context-value {
                color: #142b4c;
                font-weight: 800;
                overflow-wrap: anywhere;
            }

            .evaluation-ready-card {
                background:
                    linear-gradient(
                        90deg,
                        #edf5ff 0%,
                        #f8fbff 100%
                    );
                border: 1px solid #cfe0f6;
                border-radius: 16px;
                padding: 1.2rem;
                margin-bottom: 1rem;
            }

            .evaluation-ready-title {
                color: #1759c7;
                font-size: 1.05rem;
                font-weight: 800;
                margin-bottom: 0.55rem;
            }

            .evaluation-ready-text {
                color: #45617f;
                font-size: 0.9rem;
                line-height: 1.6;
            }

            .overall-score-card {
                background:
                    linear-gradient(
                        135deg,
                        #1f63d7 0%,
                        #1548a8 100%
                    );
                border-radius: 20px;
                padding: 1.6rem;
                color: #ffffff;
                text-align: center;
                box-shadow:
                    0 12px 28px rgba(21, 72, 168, 0.25);
                min-height: 190px;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }

            .overall-score-label {
                font-size: 0.95rem;
                opacity: 0.9;
                margin-bottom: 0.5rem;
            }

            .overall-score-value {
                font-size: 3.4rem;
                font-weight: 900;
                line-height: 1;
            }

            .overall-score-note {
                margin-top: 0.65rem;
                font-size: 0.82rem;
                opacity: 0.82;
            }

            .overall-summary-card {
                background: #ffffff;
                border: 1px solid #dce6f2;
                border-radius: 18px;
                padding: 1.3rem;
                min-height: 190px;
                box-shadow:
                    0 8px 20px rgba(15, 40, 75, 0.05);
            }

            .section-title {
                color: #102749;
                font-size: 1.1rem;
                font-weight: 800;
                margin-bottom: 0.65rem;
            }

            .section-text {
                color: #40536d;
                line-height: 1.7;
                font-size: 0.92rem;
                white-space: pre-wrap;
            }

            .score-card {
                background: #ffffff;
                border: 1px solid #dce6f2;
                border-radius: 16px;
                padding: 1.1rem;
                min-height: 130px;
                box-shadow:
                    0 8px 20px rgba(15, 40, 75, 0.05);
            }

            .score-card-label {
                color: #64748b;
                font-size: 0.8rem;
                margin-bottom: 0.4rem;
            }

            .score-card-value {
                color: #1759c7;
                font-size: 2rem;
                font-weight: 900;
            }

            .stakeholder-evaluation-card {
                background: #ffffff;
                border: 1px solid #dce6f2;
                border-radius: 18px;
                padding: 1.3rem;
                margin-bottom: 1rem;
                box-shadow:
                    0 8px 22px rgba(15, 40, 75, 0.05);
            }

            .stakeholder-evaluation-title {
                color: #102749;
                font-size: 1.25rem;
                font-weight: 800;
                margin-bottom: 0.3rem;
            }

            .stakeholder-evaluation-score {
                color: #1759c7;
                font-size: 1rem;
                font-weight: 800;
                margin-bottom: 0.8rem;
            }

            .list-section {
                margin-top: 0.85rem;
                margin-bottom: 0.85rem;
            }

            .list-heading {
                color: #142b4c;
                font-weight: 800;
                font-size: 0.93rem;
                margin-bottom: 0.4rem;
            }

            .evaluation-list {
                margin: 0;
                padding-left: 1.2rem;
                color: #40536d;
                line-height: 1.6;
                font-size: 0.88rem;
            }

            .feedback-card {
                background: #f8fbff;
                border: 1px solid #d9e7f8;
                border-radius: 13px;
                padding: 0.9rem 1rem;
                color: #40536d;
                line-height: 1.65;
                font-size: 0.88rem;
                margin-top: 0.75rem;
            }

            .reference-card {
                background: #f8fafc;
                border-left: 4px solid #1759c7;
                border-radius: 8px;
                padding: 0.75rem 0.9rem;
                margin-bottom: 0.55rem;
                color: #40536d;
                font-size: 0.82rem;
                line-height: 1.5;
            }

            .overall-feedback-card {
                background: #ffffff;
                border: 1px solid #dce6f2;
                border-radius: 18px;
                padding: 1.3rem;
                margin-top: 1rem;
                margin-bottom: 1rem;
            }

            .recommendation-item {
                background: #f8fbff;
                border: 1px solid #d9e7f8;
                border-radius: 12px;
                padding: 0.8rem 0.95rem;
                margin-bottom: 0.65rem;
                color: #40536d;
                font-size: 0.88rem;
                line-height: 1.5;
            }

            div.stButton > button {
                border-radius: 12px;
                min-height: 48px;
                font-weight: 700;
            }

            div.stButton > button[kind="primary"] {
                background:
                    linear-gradient(
                        135deg,
                        #2364d9,
                        #174caf
                    );
                color: #ffffff;
                border: none;
            }

            @media (max-width: 1000px) {
                .evaluation-context-grid {
                    grid-template-columns: 1fr;
                }
            }
            </style>
            """
        ),
        unsafe_allow_html=True,
    )


def initialize_evaluation_state() -> None:
    """
    Initialize values used by the Evaluation page.
    """

    defaults = {
        "stakeholder_evaluations": None,
        "overall_evaluation": None,
        "evaluation_completed": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_context_card(
    scenario_id: str,
    scenario_title: str,
) -> None:
    """
    Display active scenario information.
    """

    html = (
        '<div class="evaluation-context-card">'
        '<div class="evaluation-context-grid">'
        '<div>'
        '<div class="context-label">Scenario ID</div>'
        f'<div class="context-value">'
        f'{escape(scenario_id)}</div>'
        '</div>'
        '<div>'
        '<div class="context-label">Scenario Title</div>'
        f'<div class="context-value">'
        f'{escape(scenario_title)}</div>'
        '</div>'
        '</div>'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


def render_text_list(
    heading: str,
    items: list[str],
    empty_text: str,
) -> None:
    """
    Display one evaluation list.
    """

    if items:
        list_items = "".join(
            f"<li>{escape(str(item))}</li>"
            for item in items
        )

        content = (
            '<div class="list-section">'
            f'<div class="list-heading">'
            f'{escape(heading)}</div>'
            f'<ul class="evaluation-list">{list_items}</ul>'
            '</div>'
        )

    else:
        content = (
            '<div class="list-section">'
            f'<div class="list-heading">'
            f'{escape(heading)}</div>'
            f'<div class="section-text">'
            f'{escape(empty_text)}</div>'
            '</div>'
        )

    st.markdown(
        content,
        unsafe_allow_html=True,
    )


def render_references(
    evaluation: StakeholderEvaluation,
) -> None:
    """
    Display references used by one stakeholder evaluation.
    """

    st.markdown(
        '<div class="list-heading">References</div>',
        unsafe_allow_html=True,
    )

    if not evaluation.references:
        st.markdown(
            '<div class="section-text">'
            'No supporting references were recorded.'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    for reference in evaluation.references:
        reference_html = (
            '<div class="reference-card">'
            f'<b>{escape(reference.document_title)}</b><br>'
            f'File: {escape(reference.file_name)}<br>'
            f'Page: {reference.page_number}<br>'
            f'Chunk: {escape(reference.chunk_id)}<br>'
            f'Relevance: {escape(reference.relevance)}'
            '</div>'
        )

        st.markdown(
            reference_html,
            unsafe_allow_html=True,
        )


def render_stakeholder_evaluation(
    evaluation: StakeholderEvaluation,
) -> None:
    """
    Display one complete stakeholder evaluation.
    """

    display_name = STAKEHOLDER_DISPLAY_NAMES.get(
        evaluation.stakeholder,
        evaluation.stakeholder.replace("_", " ").title(),
    )

    st.markdown(
        (
            '<div class="stakeholder-evaluation-card">'
            '<div class="stakeholder-evaluation-title">'
            f'{escape(display_name)} Evaluation'
            '</div>'
            '<div class="stakeholder-evaluation-score">'
            f'Score: {evaluation.score:.1f} / 100'
            '</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )

    detail_columns = st.columns(
        2,
        gap="large",
    )

    with detail_columns[0]:
        render_text_list(
            heading="Correct Actions",
            items=evaluation.correct_actions,
            empty_text="No correct actions were identified.",
        )

        render_text_list(
            heading="Missing Actions",
            items=evaluation.missing_actions,
            empty_text="No missing actions were identified.",
        )

    with detail_columns[1]:
        render_text_list(
            heading="Incorrect Actions",
            items=evaluation.incorrect_actions,
            empty_text="No incorrect actions were identified.",
        )

        render_text_list(
            heading="Recommendations",
            items=evaluation.recommendations,
            empty_text="No stakeholder recommendations were recorded.",
        )

    feedback_html = (
        '<div class="list-heading">Feedback</div>'
        '<div class="feedback-card">'
        f'{escape(evaluation.feedback)}'
        '</div>'
    )

    st.markdown(
        feedback_html,
        unsafe_allow_html=True,
    )

    st.write("")

    render_references(
        evaluation=evaluation
    )


def run_complete_evaluation() -> None:
    """
    Run and save the four stakeholder evaluations
    and overall evaluation.
    """

    scenario_id = st.session_state.get(
        "current_scenario_id"
    )

    scenario_text = st.session_state.get(
        "current_scenario_text",
        "",
    )

    scenario_analysis = st.session_state.get(
        "scenario_analysis"
    )

    stakeholder_responses = (
        st.session_state.get(
            "stakeholder_responses"
        )
        or {}
    )

    if not scenario_id:
        raise ValueError(
            "No active Scenario ID was found."
        )

    if not scenario_text.strip():
        raise ValueError(
            "The active scenario text was not found."
        )

    required_stakeholders = set(
        STAKEHOLDER_ORDER
    )

    if set(stakeholder_responses) != required_stakeholders:
        raise ValueError(
            "The four stakeholder responses "
            "were not found in session state."
        )

    stakeholder_evaluations, overall_evaluation = (
        evaluate_complete_scenario(
            scenario_id=scenario_id,
            scenario_text=scenario_text,
            stakeholder_responses=stakeholder_responses,
            scenario_analysis=scenario_analysis,
            top_k=5,
        )
    )

    st.session_state["stakeholder_evaluations"] = (
        stakeholder_evaluations
    )

    st.session_state["overall_evaluation"] = (
        overall_evaluation
    )

    st.session_state["evaluation_completed"] = True


def render_score_cards(
    overall_evaluation: OverallEvaluation,
) -> None:
    """
    Display stakeholder scores.
    """

    score_map = {
        item.stakeholder: item.score
        for item in overall_evaluation.stakeholder_scores
    }

    columns = st.columns(4)

    for column, stakeholder in zip(
        columns,
        STAKEHOLDER_ORDER,
    ):
        display_name = STAKEHOLDER_DISPLAY_NAMES[
            stakeholder
        ]

        score = score_map.get(
            stakeholder,
            0,
        )

        with column:
            st.markdown(
                (
                    '<div class="score-card">'
                    '<div class="score-card-label">'
                    f'{escape(display_name)}'
                    '</div>'
                    '<div class="score-card-value">'
                    f'{score:.1f}'
                    '</div>'
                    '</div>'
                ),
                unsafe_allow_html=True,
            )


def render_overall_result(
    overall_evaluation: OverallEvaluation,
) -> None:
    """
    Display overall evaluation information.
    """

    overall_columns = st.columns(
        [1, 3],
        gap="large",
    )

    with overall_columns[0]:
        st.markdown(
            (
                '<div class="overall-score-card">'
                '<div class="overall-score-label">'
                'Overall Score'
                '</div>'
                '<div class="overall-score-value">'
                f'{overall_evaluation.overall_score:.1f}'
                '</div>'
                '<div class="overall-score-note">'
                'Out of 100'
                '</div>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )

    with overall_columns[1]:
        st.markdown(
            (
                '<div class="overall-summary-card">'
                '<div class="section-title">'
                'Executive Summary'
                '</div>'
                '<div class="section-text">'
                f'{escape(overall_evaluation.executive_summary)}'
                '</div>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )

    st.write("")

    render_score_cards(
        overall_evaluation=overall_evaluation
    )

    st.markdown(
        (
            '<div class="overall-feedback-card">'
            '<div class="section-title">'
            'Overall Feedback'
            '</div>'
            '<div class="section-text">'
            f'{escape(overall_evaluation.overall_feedback)}'
            '</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        "### Final Recommendations"
    )

    if overall_evaluation.final_recommendations:
        for index, recommendation in enumerate(
            overall_evaluation.final_recommendations,
            start=1,
        ):
            st.markdown(
                (
                    '<div class="recommendation-item">'
                    f'<b>{index}.</b> '
                    f'{escape(recommendation)}'
                    '</div>'
                ),
                unsafe_allow_html=True,
            )

    else:
        st.info(
            "No final recommendations were recorded."
        )


def show_evaluation_page() -> None:
    """
    Render workflow step 4: Evaluation.
    """

    inject_evaluation_styles()
    initialize_evaluation_state()

    scenario_id = st.session_state.get(
        "current_scenario_id"
    )

    scenario_title = st.session_state.get(
        "current_scenario_title",
        "",
    )

    if not scenario_id:
        st.error(
            "No active scenario was found. "
            "Create a scenario first."
        )
        return

    st.markdown(
        '<div class="evaluation-title">'
        'AI Evaluation'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="evaluation-subtitle">'
        'Evaluate all four stakeholder responses using '
        'the scenario, role responsibilities, and retrieved '
        'OT document references.'
        '</div>',
        unsafe_allow_html=True,
    )

    render_context_card(
        scenario_id=scenario_id,
        scenario_title=scenario_title,
    )

    evaluation_completed = bool(
        st.session_state.get(
            "evaluation_completed"
        )
    )

    if not evaluation_completed:
        st.markdown(
            (
                '<div class="evaluation-ready-card">'
                '<div class="evaluation-ready-title">'
                'Ready to evaluate'
                '</div>'
                '<div class="evaluation-ready-text">'
                'The platform will evaluate Maintenance, '
                'Operations, Production, and OT Cybersecurity '
                'individually. It will then calculate the fixed '
                'overall score and generate a team-level '
                'assessment. This process may take several minutes.'
                '</div>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )

        action_columns = st.columns(
            [1, 2]
        )

        with action_columns[0]:
            if st.button(
                "Back to Responses",
                use_container_width=True,
                key="evaluation_back_button",
            ):
                st.session_state["workflow_step"] = 3
                st.rerun()

        with action_columns[1]:
            run_clicked = st.button(
                "Run AI Evaluation",
                type="primary",
                use_container_width=True,
                key="run_ai_evaluation_button",
            )

        if run_clicked:
            try:
                with st.spinner(
                    "Evaluating the four stakeholder "
                    "responses and generating the overall result..."
                ):
                    run_complete_evaluation()

                st.rerun()

            except Exception as error:
                st.error(
                    "The evaluation could not be completed."
                )

                st.exception(error)

        return

    stakeholder_evaluations = (
        st.session_state.get(
            "stakeholder_evaluations"
        )
        or []
    )

    overall_evaluation = st.session_state.get(
        "overall_evaluation"
    )

    if not stakeholder_evaluations or overall_evaluation is None:
        st.error(
            "The evaluation state is incomplete. "
            "Please run the evaluation again."
        )

        if st.button(
            "Reset Evaluation",
            key="reset_incomplete_evaluation",
        ):
            st.session_state["evaluation_completed"] = False
            st.session_state["stakeholder_evaluations"] = None
            st.session_state["overall_evaluation"] = None
            st.rerun()

        return

    render_overall_result(
        overall_evaluation=overall_evaluation
    )

    st.markdown(
        "## Stakeholder Evaluation Details"
    )

    evaluation_map: dict[
        str,
        StakeholderEvaluation,
    ] = {
        evaluation.stakeholder: evaluation
        for evaluation in stakeholder_evaluations
    }

    for stakeholder in STAKEHOLDER_ORDER:
        evaluation = evaluation_map.get(
            stakeholder
        )

        if evaluation is None:
            continue

        with st.expander(
            (
                f"{STAKEHOLDER_DISPLAY_NAMES[stakeholder]} "
                f"— {evaluation.score:.1f}/100"
            ),
            expanded=False,
        ):
            render_stakeholder_evaluation(
                evaluation=evaluation
            )

    st.write("")

    action_columns = st.columns(
        [1, 1, 2]
    )

    with action_columns[0]:
        if st.button(
            "Back to Responses",
            use_container_width=True,
            key="evaluation_results_back_button",
        ):
            st.session_state["workflow_step"] = 3
            st.rerun()

    with action_columns[1]:
        if st.button(
            "Run Again",
            use_container_width=True,
            key="run_evaluation_again_button",
        ):
            st.session_state["evaluation_completed"] = False
            st.session_state["stakeholder_evaluations"] = None
            st.session_state["overall_evaluation"] = None
            st.rerun()

    with action_columns[2]:
        if st.button(
            "Continue to Report",
            type="primary",
            use_container_width=True,
            key="continue_to_report_button",
        ):
            st.session_state["workflow_step"] = 5
            st.rerun()