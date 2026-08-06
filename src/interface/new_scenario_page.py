from html import escape
from textwrap import dedent

import streamlit as st

from src.database.scenario_repository import (
    save_scenario,
    save_scenario_analysis,
)
from src.interface.evaluation_page import (
    show_evaluation_page,
)
from src.interface.report_page import (
    show_report_page,
)
from src.interface.responses_page import (
    show_responses_page,
)
from src.scenario_analysis.analyzer import analyze_scenario
from src.utils.scenario_id import generate_scenario_id


MAX_SCENARIO_LENGTH = 2000


def inject_new_scenario_styles() -> None:
    """
    Add styling for the New Scenario workflow.
    """

    st.markdown(
        dedent(
            """
            <style>
            .block-container {
                padding-top: 1.5rem;
                padding-bottom: 2rem;
                max-width: 1500px;
            }

            .new-scenario-title {
                font-size: 2.5rem;
                line-height: 1.2;
                font-weight: 800;
                color: #0d1f3c;
                margin: 0;
            }

            .page-subtitle {
                color: #64748b;
                font-size: 0.95rem;
                margin-top: 0.35rem;
            }

            .stepper-container {
                display: flex;
                align-items: center;
                gap: 0.65rem;
                margin-top: 1.1rem;
                margin-bottom: 1.6rem;
                flex-wrap: wrap;
            }

            .step-item {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                color: #64748b;
                font-size: 0.95rem;
                font-weight: 600;
            }

            .step-item.active {
                color: #1759c7;
            }

            .step-item.completed {
                color: #15803d;
            }

            .step-number {
                width: 28px;
                height: 28px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                background: #d7deea;
                color: #ffffff;
                font-weight: 700;
                font-size: 0.85rem;
            }

            .step-item.active .step-number {
                background: #1759c7;
            }

            .step-item.completed .step-number {
                background: #22a447;
            }

            .step-arrow {
                color: #9aa8bc;
                font-size: 1.2rem;
            }

            .tips-card {
                background: #ffffff;
                border: 1px solid #dce6f2;
                border-radius: 18px;
                padding: 1.2rem;
                box-shadow:
                    0 8px 22px rgba(15, 40, 75, 0.05);
                margin-bottom: 1rem;
            }

            .tips-title {
                color: #1759c7;
                font-size: 1.05rem;
                font-weight: 800;
                margin-bottom: 1rem;
            }

            .tip-row {
                display: flex;
                gap: 0.75rem;
                margin-bottom: 1rem;
            }

            .tip-icon {
                width: 42px;
                height: 42px;
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1rem;
                font-weight: 800;
                flex-shrink: 0;
            }

            .tip-icon.green {
                background: #e8f7ed;
                color: #1f9d4d;
            }

            .tip-icon.orange {
                background: #fff3e6;
                color: #e57a00;
            }

            .tip-icon.purple {
                background: #f1eaff;
                color: #6c3bd1;
            }

            .tip-icon.blue {
                background: #eaf3ff;
                color: #1759c7;
            }

            .tip-heading {
                font-size: 0.93rem;
                color: #13233f;
                font-weight: 750;
                margin-bottom: 0.2rem;
            }

            .tip-text {
                font-size: 0.84rem;
                line-height: 1.5;
                color: #53657f;
            }

            .example-title {
                color: #1759c7;
                font-size: 1rem;
                font-weight: 800;
                margin-bottom: 0.7rem;
            }

            .example-text {
                color: #33435f;
                font-style: italic;
                line-height: 1.6;
                font-size: 0.9rem;
            }

            .next-info-card {
                background:
                    linear-gradient(
                        90deg,
                        #edf5ff 0%,
                        #f8fbff 100%
                    );
                border: 1px solid #cfe0f6;
                border-radius: 14px;
                padding: 1rem 1.2rem;
                margin-top: 1rem;
                margin-bottom: 1rem;
            }

            .next-info-title {
                color: #1759c7;
                font-weight: 800;
                margin-bottom: 0.45rem;
            }

            .next-info-text {
                color: #45617f;
                font-size: 0.9rem;
                margin-bottom: 0.55rem;
            }

            .next-info-items {
                display: flex;
                gap: 1rem;
                flex-wrap: wrap;
                color: #24486f;
                font-size: 0.85rem;
            }

            .required-star {
                color: #dc2626;
            }

            .scenario-created-banner {
                background:
                    linear-gradient(
                        90deg,
                        #ecfdf3 0%,
                        #f5fff8 100%
                    );
                border: 1px solid #b9ebc9;
                border-radius: 14px;
                padding: 1rem 1.2rem;
                margin-bottom: 1rem;
                color: #166534;
            }

            .scenario-created-title {
                font-weight: 800;
                margin-bottom: 0.25rem;
            }

            .scenario-summary-card {
                background: #ffffff;
                border: 1px solid #dce6f2;
                border-radius: 16px;
                padding: 1.15rem;
                min-height: 145px;
                box-shadow:
                    0 8px 20px rgba(15, 40, 75, 0.05);
            }

            .summary-label {
                font-size: 0.82rem;
                color: #64748b;
                margin-bottom: 0.45rem;
            }

            .summary-value {
                font-size: 1.15rem;
                font-weight: 800;
                color: #142b4c;
                overflow-wrap: anywhere;
            }

            .summary-value.high,
            .summary-value.critical,
            .summary-value.offline,
            .summary-value.down {
                color: #dc2626;
            }

            .summary-value.medium,
            .summary-value.degraded {
                color: #d97706;
            }

            .summary-value.low,
            .summary-value.online,
            .summary-value.up,
            .summary-value.running {
                color: #169447;
            }

            .scenario-details-card {
                background: #ffffff;
                border: 1px solid #dce6f2;
                border-radius: 18px;
                padding: 1.3rem;
                margin-bottom: 1rem;
            }

            .section-heading {
                color: #102749;
                font-size: 1.2rem;
                font-weight: 800;
                margin-bottom: 0.65rem;
            }

            .scenario-text-display {
                color: #40536d;
                line-height: 1.7;
                white-space: pre-wrap;
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
            </style>
            """
        ),
        unsafe_allow_html=True,
    )


def initialize_workflow_state() -> None:
    """
    Initialize values used by the New Scenario workflow.
    """

    defaults = {
        "workflow_step": 1,
        "scenario_title_input": "",
        "scenario_text_input": "",
        "current_scenario_id": None,
        "current_scenario_title": "",
        "current_scenario_text": "",
        "scenario_analysis": None,
        "stakeholder_responses": None,
        "stakeholder_evaluations": None,
        "overall_evaluation": None,
        "evaluation_completed": False,
        "generated_report_path": None,
        "report_generated": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_stepper(
    active_step: int,
) -> None:
    """
    Render the five-step workflow indicator.
    """

    steps = [
        (1, "Scenario"),
        (2, "Operational Summary"),
        (3, "Responses"),
        (4, "Evaluation"),
        (5, "Report"),
    ]

    html_parts = [
        '<div class="stepper-container">'
    ]

    for index, (step_number, step_name) in enumerate(steps):
        if step_number < active_step:
            status_class = "completed"
        elif step_number == active_step:
            status_class = "active"
        else:
            status_class = ""

        html_parts.append(
            f'<div class="step-item {status_class}">'
            f'<div class="step-number">{step_number}</div>'
            f'<div>{escape(step_name)}</div>'
            '</div>'
        )

        if index < len(steps) - 1:
            html_parts.append(
                '<div class="step-arrow">›</div>'
            )

    html_parts.append("</div>")

    st.markdown(
        "".join(html_parts),
        unsafe_allow_html=True,
    )


def render_tips_panel() -> None:
    """
    Render writing tips and an example scenario.
    """

    tips_html = (
        '<div class="tips-card">'
        '<div class="tips-title">'
        'Tips for writing a good scenario'
        '</div>'

        '<div class="tip-row">'
        '<div class="tip-icon green">✓</div>'
        '<div>'
        '<div class="tip-heading">Be Specific</div>'
        '<div class="tip-text">'
        'Include asset names, locations, systems affected, '
        'and visible error messages.'
        '</div>'
        '</div>'
        '</div>'

        '<div class="tip-row">'
        '<div class="tip-icon orange">!</div>'
        '<div>'
        '<div class="tip-heading">Include Context</div>'
        '<div class="tip-text">'
        'Mention what was happening before the incident '
        'and any unusual conditions.'
        '</div>'
        '</div>'
        '</div>'

        '<div class="tip-row">'
        '<div class="tip-icon purple">S</div>'
        '<div>'
        '<div class="tip-heading">Think Stakeholders</div>'
        '<div class="tip-text">'
        'Consider what information each stakeholder group '
        'would need.'
        '</div>'
        '</div>'
        '</div>'

        '<div class="tip-row">'
        '<div class="tip-icon blue">OT</div>'
        '<div>'
        '<div class="tip-heading">Realistic &amp; Relevant</div>'
        '<div class="tip-text">'
        'Base the scenario on realistic industrial '
        'environments and credible threats.'
        '</div>'
        '</div>'
        '</div>'

        '</div>'
    )

    st.markdown(
        tips_html,
        unsafe_allow_html=True,
    )

    example_html = (
        '<div class="tips-card">'
        '<div class="example-title">Example Scenario</div>'
        '<div class="example-text">'
        '“PLC-02 controlling the transfer pump stopped '
        'responding at 14:32 while the tank level was rising. '
        'The HMI shows communication timeout and the network '
        'switch shows link down.”'
        '</div>'
        '</div>'
    )

    st.markdown(
        example_html,
        unsafe_allow_html=True,
    )


def clear_scenario_form() -> None:
    """
    Clear the scenario form and workflow values.
    """

    st.session_state["scenario_title_input"] = ""
    st.session_state["scenario_text_input"] = ""
    st.session_state["current_scenario_id"] = None
    st.session_state["current_scenario_title"] = ""
    st.session_state["current_scenario_text"] = ""
    st.session_state["scenario_analysis"] = None
    st.session_state["stakeholder_responses"] = None
    st.session_state["stakeholder_evaluations"] = None
    st.session_state["overall_evaluation"] = None
    st.session_state["evaluation_completed"] = False
    st.session_state["generated_report_path"] = None
    st.session_state["report_generated"] = False
    st.session_state["workflow_step"] = 1

    response_keys = [
        "response_ot_cybersecurity",
        "response_maintenance",
        "response_operations",
        "response_production",
    ]

    for key in response_keys:
        st.session_state[key] = ""


def start_another_scenario() -> None:
    """
    Reset the workflow so another scenario can be created.
    """

    clear_scenario_form()
    st.rerun()


def create_and_analyze_scenario(
    scenario_title: str,
    scenario_text: str,
) -> None:
    """
    Save a scenario, analyze it, and store its data
    in Streamlit session state.
    """

    scenario_id = generate_scenario_id()

    save_scenario(
        scenario_id=scenario_id,
        scenario_title=scenario_title,
        scenario_text=scenario_text,
    )

    overview = analyze_scenario(
        scenario_text=scenario_text
    )

    analysis_data = overview.model_dump()

    save_scenario_analysis(
        scenario_id=scenario_id,
        analysis_data=analysis_data,
    )

    st.session_state["current_scenario_id"] = scenario_id
    st.session_state["current_scenario_title"] = scenario_title
    st.session_state["current_scenario_text"] = scenario_text
    st.session_state["scenario_analysis"] = analysis_data
    st.session_state["stakeholder_responses"] = None
    st.session_state["stakeholder_evaluations"] = None
    st.session_state["overall_evaluation"] = None
    st.session_state["evaluation_completed"] = False
    st.session_state["generated_report_path"] = None
    st.session_state["report_generated"] = False
    st.session_state["workflow_step"] = 2


def render_summary_card(
    label: str,
    value: object,
) -> None:
    """
    Render one operational-summary card.
    """

    display_value = (
        "Unknown"
        if value is None or value == ""
        else str(value)
    )

    normalized_class = (
        display_value
        .strip()
        .lower()
        .replace(" ", "-")
    )

    card_html = (
        '<div class="scenario-summary-card">'
        f'<div class="summary-label">{escape(label)}</div>'
        f'<div class="summary-value {escape(normalized_class)}">'
        f'{escape(display_value)}'
        '</div>'
        '</div>'
    )

    st.markdown(
        card_html,
        unsafe_allow_html=True,
    )


def show_scenario_form() -> None:
    """
    Render workflow step 1: scenario creation.
    """

    content_columns = st.columns(
        [3.4, 1.3],
        gap="large",
    )

    with content_columns[0]:
        with st.container(border=True):
            st.markdown(
                "### Scenario Title "
                '<span class="required-star">*</span>',
                unsafe_allow_html=True,
            )

            scenario_title = st.text_input(
                "Scenario Title",
                key="scenario_title_input",
                placeholder=(
                    "Enter a clear and descriptive title "
                    "for the scenario"
                ),
                label_visibility="collapsed",
            )

            st.caption(
                "Example: PLC Communication Failure "
                "in Tank Farm"
            )

            st.write("")

            st.markdown(
                "### Incident Scenario "
                '<span class="required-star">*</span>',
                unsafe_allow_html=True,
            )

            scenario_text = st.text_area(
                "Incident Scenario",
                key="scenario_text_input",
                placeholder=(
                    "Describe the incident in detail including "
                    "what happened, where, when, and any relevant "
                    "conditions..."
                ),
                height=230,
                max_chars=MAX_SCENARIO_LENGTH,
                label_visibility="collapsed",
            )

            character_count = len(
                scenario_text
            )

            st.caption(
                f"{character_count} / "
                f"{MAX_SCENARIO_LENGTH} characters"
            )

            st.caption(
                "Provide enough details for the AI to generate "
                "an accurate operational summary."
            )

            next_info_html = (
                '<div class="next-info-card">'
                '<div class="next-info-title">'
                'What happens next?'
                '</div>'
                '<div class="next-info-text">'
                'Once you create the scenario, the system will '
                'automatically:'
                '</div>'
                '<div class="next-info-items">'
                '<span>✓ Generate a unique Scenario ID</span>'
                '<span>✓ Save to database</span>'
                '<span>✓ Analyze the incident</span>'
                '<span>✓ Save the operational summary</span>'
                '</div>'
                '</div>'
            )

            st.markdown(
                next_info_html,
                unsafe_allow_html=True,
            )

            button_columns = st.columns(
                [1, 3]
            )

            with button_columns[0]:
                if st.button(
                    "Clear",
                    use_container_width=True,
                    key="clear_scenario_button",
                ):
                    clear_scenario_form()
                    st.rerun()

            with button_columns[1]:
                create_clicked = st.button(
                    "Create Scenario",
                    type="primary",
                    use_container_width=True,
                    key="create_scenario_button",
                )

            if create_clicked:
                cleaned_title = scenario_title.strip()
                cleaned_text = scenario_text.strip()

                if not cleaned_title:
                    st.error(
                        "Please enter a scenario title."
                    )

                elif not cleaned_text:
                    st.error(
                        "Please enter the incident scenario."
                    )

                elif len(cleaned_text) < 40:
                    st.warning(
                        "Please provide more details in the "
                        "incident scenario."
                    )

                else:
                    try:
                        with st.spinner(
                            "Creating and analyzing "
                            "the scenario..."
                        ):
                            create_and_analyze_scenario(
                                scenario_title=cleaned_title,
                                scenario_text=cleaned_text,
                            )

                        st.rerun()

                    except Exception as error:
                        st.error(
                            "The scenario could not be created."
                        )

                        st.exception(error)

    with content_columns[1]:
        render_tips_panel()


def show_operational_summary() -> None:
    """
    Render workflow step 2: operational summary.
    """

    scenario_id = st.session_state[
        "current_scenario_id"
    ]

    scenario_title = st.session_state[
        "current_scenario_title"
    ]

    scenario_text = st.session_state[
        "current_scenario_text"
    ]

    analysis = (
        st.session_state["scenario_analysis"]
        or {}
    )

    banner_html = (
        '<div class="scenario-created-banner">'
        '<div class="scenario-created-title">'
        'Scenario created and analyzed successfully'
        '</div>'
        f'<div>Scenario ID: '
        f'<b>{escape(str(scenario_id))}</b></div>'
        '</div>'
    )

    st.markdown(
        banner_html,
        unsafe_allow_html=True,
    )

    details_html = (
        '<div class="scenario-details-card">'
        '<div class="section-heading">'
        f'{escape(str(scenario_title))}'
        '</div>'
        '<div class="scenario-text-display">'
        f'{escape(str(scenario_text))}'
        '</div>'
        '</div>'
    )

    st.markdown(
        details_html,
        unsafe_allow_html=True,
    )

    st.markdown(
        "### Operational Summary"
    )

    first_row = st.columns(4)

    with first_row[0]:
        render_summary_card(
            "Asset / Area",
            analysis.get("asset_area"),
        )

    with first_row[1]:
        render_summary_card(
            "Severity",
            analysis.get("severity"),
        )

    with first_row[2]:
        render_summary_card(
            "PLC Status",
            analysis.get("plc_status"),
        )

    with first_row[3]:
        render_summary_card(
            "HMI Status",
            analysis.get("hmi_status"),
        )

    second_row = st.columns(3)

    with second_row[0]:
        render_summary_card(
            "Network Status",
            analysis.get("network_status"),
        )

    with second_row[1]:
        render_summary_card(
            "Last Known State",
            analysis.get("last_known_state"),
        )

    with second_row[2]:
        render_summary_card(
            "Active Alarms",
            analysis.get("active_alarms"),
        )

    st.write("")

    action_columns = st.columns(
        [1, 1, 2]
    )

    with action_columns[0]:
        if st.button(
            "Edit Scenario",
            use_container_width=True,
            key="edit_created_scenario",
        ):
            st.session_state["workflow_step"] = 1
            st.rerun()

    with action_columns[1]:
        if st.button(
            "Start Another",
            use_container_width=True,
            key="start_another_scenario",
        ):
            start_another_scenario()

    with action_columns[2]:
        if st.button(
            "Continue to Stakeholder Responses",
            type="primary",
            use_container_width=True,
            key="continue_to_responses",
        ):
            st.session_state["workflow_step"] = 3
            st.rerun()



def show_new_scenario_page() -> None:
    """
    Render the complete New Scenario workflow.
    """

    inject_new_scenario_styles()
    initialize_workflow_state()

    active_step = int(
        st.session_state.get(
            "workflow_step",
            1,
        )
    )

    header_columns = st.columns(
        [5, 1]
    )

    with header_columns[0]:
        st.markdown(
            '<div class="new-scenario-title">'
            'Create New Incident Scenario'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="page-subtitle">'
            'Create, analyze, and evaluate an industrial '
            'OT incident scenario.'
            '</div>',
            unsafe_allow_html=True,
        )

    with header_columns[1]:
        if st.button(
            "← Back to Home",
            use_container_width=True,
            key="back_to_home_button",
        ):
            st.session_state["current_page"] = "Home"
            st.rerun()

    render_stepper(
        active_step=active_step
    )

    if active_step == 1:
        show_scenario_form()

    elif active_step == 2:
        show_operational_summary()

    elif active_step == 3:
        show_responses_page()

    elif active_step == 4:
        show_evaluation_page()

    elif active_step == 5:
        show_report_page()

    else:
        st.error(
            "Invalid workflow step."
        )

        if st.button(
            "Restart Workflow",
            key="restart_invalid_workflow",
        ):
            clear_scenario_form()
            st.rerun()