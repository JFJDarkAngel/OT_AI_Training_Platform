from html import escape
from pathlib import Path
from textwrap import dedent

import streamlit as st

from src.reporting.report_generator import generate_report


STAKEHOLDER_DISPLAY_NAMES = {
    "maintenance": "Maintenance",
    "operations": "Operations",
    "production": "Production",
    "ot_cybersecurity": "OT Cybersecurity",
}


def inject_report_styles() -> None:
    """
    Add styling for the final report page.
    """

    st.markdown(
        dedent(
            """
            <style>
            .report-title {
                font-size: 2.4rem;
                font-weight: 800;
                color: #0d1f3c;
                margin-bottom: 0.3rem;
            }

            .report-subtitle {
                color: #64748b;
                font-size: 0.95rem;
                margin-bottom: 1.2rem;
            }

            .report-context-card {
                background: #ffffff;
                border: 1px solid #dce6f2;
                border-radius: 16px;
                padding: 1rem 1.2rem;
                margin-bottom: 1rem;
                box-shadow:
                    0 8px 20px rgba(15, 40, 75, 0.05);
            }

            .report-context-grid {
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

            .report-score-card {
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
                min-height: 190px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                box-shadow:
                    0 12px 28px rgba(21, 72, 168, 0.25);
            }

            .report-score-label {
                font-size: 0.95rem;
                opacity: 0.9;
                margin-bottom: 0.5rem;
            }

            .report-score-value {
                font-size: 3.4rem;
                font-weight: 900;
                line-height: 1;
            }

            .report-score-note {
                margin-top: 0.65rem;
                font-size: 0.82rem;
                opacity: 0.82;
            }

            .report-summary-card {
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

            .stakeholder-score-card {
                background: #ffffff;
                border: 1px solid #dce6f2;
                border-radius: 16px;
                padding: 1.1rem;
                min-height: 125px;
                box-shadow:
                    0 8px 20px rgba(15, 40, 75, 0.05);
            }

            .stakeholder-score-label {
                color: #64748b;
                font-size: 0.8rem;
                margin-bottom: 0.4rem;
            }

            .stakeholder-score-value {
                color: #1759c7;
                font-size: 2rem;
                font-weight: 900;
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

            .report-ready-card {
                background:
                    linear-gradient(
                        90deg,
                        #ecfdf3 0%,
                        #f5fff8 100%
                    );
                border: 1px solid #b9ebc9;
                border-radius: 16px;
                padding: 1.2rem;
                margin-bottom: 1rem;
                color: #166534;
            }

            .report-ready-title {
                font-size: 1.05rem;
                font-weight: 800;
                margin-bottom: 0.4rem;
            }

            .report-ready-text {
                font-size: 0.9rem;
                line-height: 1.6;
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
                .report-context-grid {
                    grid-template-columns: 1fr;
                }
            }
            </style>
            """
        ),
        unsafe_allow_html=True,
    )


def initialize_report_state() -> None:
    """
    Initialize values used by the report page.
    """

    defaults = {
        "generated_report_path": None,
        "report_generated": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_context_card(
    scenario_id: str,
    scenario_title: str,
) -> None:
    """
    Display current scenario information.
    """

    html = (
        '<div class="report-context-card">'
        '<div class="report-context-grid">'
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


def render_report_preview() -> None:
    """
    Display the evaluation summary before PDF generation.
    """

    overall_evaluation = st.session_state.get(
        "overall_evaluation"
    )

    if overall_evaluation is None:
        st.error(
            "The overall evaluation was not found. "
            "Run the AI evaluation first."
        )
        return

    columns = st.columns(
        [1, 3],
        gap="large",
    )

    with columns[0]:
        st.markdown(
            (
                '<div class="report-score-card">'
                '<div class="report-score-label">'
                'Overall Score'
                '</div>'
                '<div class="report-score-value">'
                f'{overall_evaluation.overall_score:.1f}'
                '</div>'
                '<div class="report-score-note">'
                'Out of 100'
                '</div>'
                '</div>'
            ),
            unsafe_allow_html=True,
        )

    with columns[1]:
        st.markdown(
            (
                '<div class="report-summary-card">'
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

    score_map = {
        item.stakeholder: item.score
        for item in overall_evaluation.stakeholder_scores
    }

    stakeholder_columns = st.columns(4)

    stakeholder_order = (
        "maintenance",
        "operations",
        "production",
        "ot_cybersecurity",
    )

    for column, stakeholder in zip(
        stakeholder_columns,
        stakeholder_order,
    ):
        with column:
            display_name = STAKEHOLDER_DISPLAY_NAMES[
                stakeholder
            ]

            score = score_map.get(
                stakeholder,
                0,
            )

            st.markdown(
                (
                    '<div class="stakeholder-score-card">'
                    '<div class="stakeholder-score-label">'
                    f'{escape(display_name)}'
                    '</div>'
                    '<div class="stakeholder-score-value">'
                    f'{score:.1f}'
                    '</div>'
                    '</div>'
                ),
                unsafe_allow_html=True,
            )

    st.write("")

    st.markdown(
        '<div class="section-title">Overall Feedback</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        (
            '<div class="report-summary-card">'
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


def generate_pdf_report(
    scenario_id: str,
) -> Path:
    """
    Generate and store the PDF report.
    """

    report_path = generate_report(
        scenario_id=scenario_id
    )

    st.session_state["generated_report_path"] = str(
        report_path
    )

    st.session_state["report_generated"] = True

    return report_path


def render_download_section() -> None:
    """
    Display the generated PDF download controls.
    """

    report_path_value = st.session_state.get(
        "generated_report_path"
    )

    if not report_path_value:
        return

    report_path = Path(
        report_path_value
    )

    if not report_path.exists():
        st.error(
            "The generated report file could not be found."
        )
        return

    st.markdown(
        (
            '<div class="report-ready-card">'
            '<div class="report-ready-title">'
            'PDF report generated successfully'
            '</div>'
            '<div class="report-ready-text">'
            f'File: {escape(report_path.name)}'
            '</div>'
            '</div>'
        ),
        unsafe_allow_html=True,
    )

    pdf_bytes = report_path.read_bytes()

    st.download_button(
        label="Download PDF Report",
        data=pdf_bytes,
        file_name=report_path.name,
        mime="application/pdf",
        type="primary",
        use_container_width=True,
        key="download_generated_report",
    )


def show_report_page() -> None:
    """
    Render workflow step 5: Final Report.
    """

    inject_report_styles()
    initialize_report_state()

    scenario_id = st.session_state.get(
        "current_scenario_id"
    )

    scenario_title = st.session_state.get(
        "current_scenario_title",
        "",
    )

    evaluation_completed = bool(
        st.session_state.get(
            "evaluation_completed"
        )
    )

    if not scenario_id:
        st.error(
            "No active scenario was found."
        )
        return

    if not evaluation_completed:
        st.error(
            "The scenario must be evaluated before "
            "the report can be generated."
        )
        return

    st.markdown(
        '<div class="report-title">'
        'Final Evaluation Report'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="report-subtitle">'
        'Review the final evaluation and generate '
        'the complete PDF report.'
        '</div>',
        unsafe_allow_html=True,
    )

    render_context_card(
        scenario_id=scenario_id,
        scenario_title=scenario_title,
    )

    render_report_preview()

    st.write("")

    action_columns = st.columns(
        [1, 2]
    )

    with action_columns[0]:
        if st.button(
            "Back to Evaluation",
            use_container_width=True,
            key="report_back_button",
        ):
            st.session_state["workflow_step"] = 4
            st.rerun()

    with action_columns[1]:
        generate_clicked = st.button(
            "Generate PDF Report",
            type="primary",
            use_container_width=True,
            key="generate_pdf_report_button",
        )

    if generate_clicked:
        try:
            with st.spinner(
                "Generating the final PDF report..."
            ):
                generate_pdf_report(
                    scenario_id=scenario_id
                )

            st.rerun()

        except Exception as error:
            st.error(
                "The PDF report could not be generated."
            )

            st.exception(error)

    render_download_section()

    if st.session_state.get(
        "report_generated"
    ):
        st.write("")

        if st.button(
            "Finish and Return to Home",
            use_container_width=True,
            key="finish_report_workflow",
        ):
            st.session_state["current_page"] = "Home"
            st.rerun()