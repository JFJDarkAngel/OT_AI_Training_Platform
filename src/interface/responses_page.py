from html import escape
from textwrap import dedent

import streamlit as st

from src.database.response_repository import save_response


MAX_RESPONSE_LENGTH = 2000


STAKEHOLDERS = [
    {
        "key": "ot_cybersecurity",
        "title": "OT Cybersecurity Response",
        "description": (
            "Detect and contain the threat, isolate affected assets, "
            "preserve evidence, and coordinate cyber recovery."
        ),
        "accent": "blue",
        "icon": "shield-lock",
    },
    {
        "key": "maintenance",
        "title": "Maintenance Response",
        "description": (
            "Inspect equipment, diagnose root cause, repair faults, "
            "and verify equipment readiness."
        ),
        "accent": "green",
        "icon": "tools",
    },
    {
        "key": "operations",
        "title": "Operations Response",
        "description": (
            "Monitor the process, apply approved manual controls, "
            "coordinate safe operation, and support controlled recovery."
        ),
        "accent": "orange",
        "icon": "diagram-3",
    },
    {
        "key": "production",
        "title": "Production Response",
        "description": (
            "Assess production impact, adjust priorities, plan capacity, "
            "and coordinate a safe return to production."
        ),
        "accent": "purple",
        "icon": "bar-chart",
    },
]


def inject_response_styles() -> None:
    """
    Add styling for the stakeholder responses page.
    """

    st.markdown(
        dedent(
            """
            <style>
            .responses-title {
                font-size: 2.4rem;
                font-weight: 800;
                color: #0d1f3c;
                margin-bottom: 0.3rem;
            }

            .responses-subtitle {
                color: #64748b;
                font-size: 0.95rem;
                margin-bottom: 1.1rem;
            }

            .scenario-header-card {
                background: #ffffff;
                border: 1px solid #dce6f2;
                border-radius: 16px;
                padding: 1rem 1.2rem;
                margin-bottom: 1rem;
                box-shadow:
                    0 8px 20px rgba(15, 40, 75, 0.05);
            }

            .scenario-header-grid {
                display: grid;
                grid-template-columns: 1fr 2fr;
                gap: 1rem;
            }

            .scenario-header-label {
                font-size: 0.78rem;
                color: #64748b;
                margin-bottom: 0.3rem;
            }

            .scenario-header-value {
                font-weight: 800;
                color: #142b4c;
                overflow-wrap: anywhere;
            }

            .summary-panel {
                background: #ffffff;
                border: 1px solid #dce6f2;
                border-radius: 16px;
                padding: 1rem 1.2rem;
                margin-bottom: 1rem;
            }

            .summary-panel-title {
                font-size: 1.05rem;
                font-weight: 800;
                color: #102749;
                margin-bottom: 0.8rem;
            }

            .summary-grid {
                display: grid;
                grid-template-columns:
                    repeat(7, minmax(100px, 1fr));
                gap: 0.75rem;
            }

            .summary-item {
                border-right: 1px solid #e2e8f0;
                padding-right: 0.7rem;
            }

            .summary-item:last-child {
                border-right: none;
            }

            .summary-label {
                color: #64748b;
                font-size: 0.76rem;
                margin-bottom: 0.3rem;
            }

            .summary-value {
                color: #142b4c;
                font-size: 0.92rem;
                font-weight: 800;
                overflow-wrap: anywhere;
            }

            .summary-status {
                margin-top: 0.2rem;
                font-size: 0.73rem;
                color: #64748b;
            }

            .response-section-card {
                background: #ffffff;
                border: 1px solid #dce6f2;
                border-radius: 16px;
                padding: 1.2rem;
                margin-bottom: 1rem;
                box-shadow:
                    0 8px 20px rgba(15, 40, 75, 0.04);
            }

            .stakeholder-title {
                font-size: 1rem;
                font-weight: 800;
                margin-bottom: 0.3rem;
            }

            .stakeholder-title.blue {
                color: #1759c7;
            }

            .stakeholder-title.green {
                color: #15803d;
            }

            .stakeholder-title.orange {
                color: #d97706;
            }

            .stakeholder-title.purple {
                color: #6d28d9;
            }

            .stakeholder-description {
                font-size: 0.84rem;
                color: #53657f;
                line-height: 1.5;
            }

            .guidelines-card {
                background: #ffffff;
                border: 1px solid #f0dfd1;
                border-radius: 16px;
                padding: 1rem;
                margin-bottom: 1rem;
            }

            .guidelines-title {
                color: #c2410c;
                font-size: 1rem;
                font-weight: 800;
                margin-bottom: 0.9rem;
            }

            .guideline-item {
                margin-bottom: 0.95rem;
            }

            .guideline-heading {
                font-weight: 800;
                color: #142b4c;
                font-size: 0.9rem;
                margin-bottom: 0.2rem;
            }

            .guideline-text {
                color: #53657f;
                font-size: 0.82rem;
                line-height: 1.45;
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

            @media (max-width: 1100px) {
                .summary-grid {
                    grid-template-columns:
                        repeat(2, minmax(130px, 1fr));
                }

                .scenario-header-grid {
                    grid-template-columns: 1fr;
                }
            }
            </style>
            """
        ),
        unsafe_allow_html=True,
    )


def initialize_response_state() -> None:
    """
    Initialize response text values in session state.
    """

    for stakeholder in STAKEHOLDERS:
        key = f"response_{stakeholder['key']}"

        if key not in st.session_state:
            st.session_state[key] = ""


def safe_value(
    value: object,
) -> str:
    """
    Convert a summary value into display text.
    """

    if value is None:
        return "Unknown"

    text = str(value).strip()

    return text if text else "Unknown"


def render_scenario_header(
    scenario_id: str,
    scenario_title: str,
) -> None:
    """
    Render Scenario ID and title.
    """

    html = (
        '<div class="scenario-header-card">'
        '<div class="scenario-header-grid">'
        '<div>'
        '<div class="scenario-header-label">Scenario ID</div>'
        f'<div class="scenario-header-value">'
        f'{escape(scenario_id)}</div>'
        '</div>'
        '<div>'
        '<div class="scenario-header-label">Scenario Title</div>'
        f'<div class="scenario-header-value">'
        f'{escape(scenario_title)}</div>'
        '</div>'
        '</div>'
        '</div>'
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


def render_operational_summary(
    analysis: dict,
) -> None:
    """
    Render the saved scenario operational summary.
    """

    fields = [
        ("Asset / Area", analysis.get("asset_area")),
        ("Severity", analysis.get("severity")),
        ("PLC Status", analysis.get("plc_status")),
        ("HMI Status", analysis.get("hmi_status")),
        ("Network", analysis.get("network_status")),
        (
            "Last Known State",
            analysis.get("last_known_state"),
        ),
        ("Active Alarms", analysis.get("active_alarms")),
    ]

    html_parts = [
        '<div class="summary-panel">',
        '<div class="summary-panel-title">',
        'Scenario Summary',
        '</div>',
        '<div class="summary-grid">',
    ]

    for label, value in fields:
        display_value = safe_value(value)

        html_parts.extend(
            [
                '<div class="summary-item">',
                f'<div class="summary-label">'
                f'{escape(label)}</div>',
                f'<div class="summary-value">'
                f'{escape(display_value)}</div>',
                '</div>',
            ]
        )

    html_parts.extend(
        [
            '</div>',
            '</div>',
        ]
    )

    st.markdown(
        "".join(html_parts),
        unsafe_allow_html=True,
    )


def render_guidelines() -> None:
    """
    Render response-writing guidance.
    """

    items = [
        (
            "Be Specific",
            "Provide clear, concrete actions instead of "
            "general statements.",
        ),
        (
            "Follow the Timeline",
            "Describe actions in the correct sequence based "
            "on how the incident develops.",
        ),
        (
            "Think as a Team",
            "Explain how your actions coordinate with the "
            "other stakeholder groups.",
        ),
        (
            "Focus on Safety",
            "Prioritize personnel safety, environmental "
            "protection, and asset integrity.",
        ),
        (
            "Use Best Practices",
            "Align responses with approved procedures, "
            "industry standards, and incident-response practice.",
        ),
    ]

    html_parts = [
        '<div class="guidelines-card">',
        '<div class="guidelines-title">',
        'Response Guidelines',
        '</div>',
    ]

    for heading, text in items:
        html_parts.extend(
            [
                '<div class="guideline-item">',
                f'<div class="guideline-heading">'
                f'{escape(heading)}</div>',
                f'<div class="guideline-text">'
                f'{escape(text)}</div>',
                '</div>',
            ]
        )

    html_parts.append("</div>")

    st.markdown(
        "".join(html_parts),
        unsafe_allow_html=True,
    )


def save_all_responses(
    scenario_id: str,
) -> None:
    """
    Save all four stakeholder responses.
    """

    for stakeholder in STAKEHOLDERS:
        response_key = (
            f"response_{stakeholder['key']}"
        )

        answer_text = st.session_state[
            response_key
        ].strip()

        save_response(
            scenario_id=scenario_id,
            stakeholder=stakeholder["key"],
            answer_text=answer_text,
        )


def show_responses_page() -> None:
    """
    Render workflow step 3: stakeholder responses.
    """

    inject_response_styles()
    initialize_response_state()

    scenario_id = st.session_state.get(
        "current_scenario_id"
    )

    scenario_title = st.session_state.get(
        "current_scenario_title",
        "",
    )

    analysis = st.session_state.get(
        "scenario_analysis"
    ) or {}

    if not scenario_id:
        st.error(
            "No active scenario was found. "
            "Create a scenario first."
        )
        return

    st.markdown(
        '<div class="responses-title">'
        'Stakeholder Responses'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="responses-subtitle">'
        'Provide the actions and decisions each stakeholder '
        'team would take in response to this incident.'
        '</div>',
        unsafe_allow_html=True,
    )

    render_scenario_header(
        scenario_id=scenario_id,
        scenario_title=scenario_title,
    )

    render_operational_summary(
        analysis=analysis
    )

    layout_columns = st.columns(
        [3.5, 1.2],
        gap="large",
    )

    with layout_columns[0]:
        st.markdown(
            "### Stakeholder Responses"
        )

        st.caption(
            "Write the actions and decisions for each "
            "stakeholder area."
        )

        for index, stakeholder in enumerate(
            STAKEHOLDERS,
            start=1,
        ):
            response_key = (
                f"response_{stakeholder['key']}"
            )

            left_column, right_column = st.columns(
                [1.1, 3.1],
                gap="large",
            )

            with left_column:
                st.markdown(
                    (
                        f'<div class="stakeholder-title '
                        f'{stakeholder["accent"]}">'
                        f'{index}. '
                        f'{escape(stakeholder["title"])}'
                        '</div>'
                    ),
                    unsafe_allow_html=True,
                )

                st.markdown(
                    (
                        '<div class="stakeholder-description">'
                        f'{escape(stakeholder["description"])}'
                        '</div>'
                    ),
                    unsafe_allow_html=True,
                )

            with right_column:
                response_text = st.text_area(
                    stakeholder["title"],
                    key=response_key,
                    placeholder=(
                        "Type your response here..."
                    ),
                    height=145,
                    max_chars=MAX_RESPONSE_LENGTH,
                    label_visibility="collapsed",
                )

                st.caption(
                    f"{len(response_text)} / "
                    f"{MAX_RESPONSE_LENGTH} characters"
                )

            if index < len(STAKEHOLDERS):
                st.divider()

    with layout_columns[1]:
        render_guidelines()

    st.write("")

    button_columns = st.columns(
        [1, 1, 2]
    )

    with button_columns[0]:
        if st.button(
            "Back to Summary",
            use_container_width=True,
            key="responses_back_button",
        ):
            st.session_state["workflow_step"] = 2
            st.rerun()

    with button_columns[1]:
        if st.button(
            "Save Draft",
            use_container_width=True,
            key="save_response_draft_button",
        ):
            non_empty_count = 0

            try:
                for stakeholder in STAKEHOLDERS:
                    response_key = (
                        f"response_{stakeholder['key']}"
                    )

                    answer_text = st.session_state[
                        response_key
                    ].strip()

                    if answer_text:
                        save_response(
                            scenario_id=scenario_id,
                            stakeholder=stakeholder["key"],
                            answer_text=answer_text,
                        )

                        non_empty_count += 1

                if non_empty_count == 0:
                    st.warning(
                        "Write at least one response before "
                        "saving a draft."
                    )
                else:
                    st.success(
                        f"Saved {non_empty_count} response(s)."
                    )

            except Exception as error:
                st.error(
                    "The response draft could not be saved."
                )
                st.exception(error)

    with button_columns[2]:
        submit_clicked = st.button(
            "Submit Responses for Evaluation",
            type="primary",
            use_container_width=True,
            key="submit_responses_button",
        )

    if submit_clicked:
        empty_stakeholders = []

        for stakeholder in STAKEHOLDERS:
            response_key = (
                f"response_{stakeholder['key']}"
            )

            if not st.session_state[
                response_key
            ].strip():
                empty_stakeholders.append(
                    stakeholder["title"]
                )

        if empty_stakeholders:
            st.error(
                "Please complete all four stakeholder "
                "responses before evaluation."
            )

            for stakeholder_name in empty_stakeholders:
                st.write(f"- {stakeholder_name}")

        else:
            try:
                with st.spinner(
                    "Saving stakeholder responses..."
                ):
                    save_all_responses(
                        scenario_id=scenario_id
                    )

                    st.session_state[
                        "stakeholder_responses"
                    ] = {
                        stakeholder["key"]:
                        st.session_state[
                            f"response_{stakeholder['key']}"
                        ].strip()
                        for stakeholder in STAKEHOLDERS
                    }

                    st.session_state[
                        "workflow_step"
                    ] = 4

                st.success(
                    "All responses were saved successfully."
                )

                st.rerun()

            except Exception as error:
                st.error(
                    "The stakeholder responses could not "
                    "be saved."
                )
                st.exception(error)