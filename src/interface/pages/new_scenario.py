from html import escape

import streamlit as st

from src.database.scenario_repository import (
    save_scenario,
    save_scenario_analysis,
)
from src.scenario_analysis.analyzer import analyze_scenario
from src.utils.scenario_id import generate_scenario_id


def _go_to(page_name: str) -> None:
    st.session_state["page"] = page_name
    st.rerun()


def _reset_form() -> None:
    st.session_state.pop("scenario_title_input", None)
    st.session_state.pop("scenario_text_input", None)
    st.session_state.pop("new_scenario_preview", None)


def _analysis_to_dict(analysis) -> dict:
    if hasattr(analysis, "model_dump"):
        return analysis.model_dump()

    return {
        "asset_area": getattr(analysis, "asset_area", "Unknown"),
        "severity": getattr(analysis, "severity", "unknown"),
        "plc_status": getattr(analysis, "plc_status", "unknown"),
        "hmi_status": getattr(analysis, "hmi_status", "unknown"),
        "network_status": getattr(analysis, "network_status", "unknown"),
        "last_known_state": getattr(analysis, "last_known_state", "unknown"),
        "active_alarms": getattr(analysis, "active_alarms", None),
    }


def _summary_value(value) -> str:
    if value is None:
        return "Unknown"
    text = str(value).strip()
    return text.replace("_", " ").title() if text else "Unknown"


def render_new_scenario() -> None:
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

    back_col, _ = st.columns([1.15, 5])
    with back_col:
        if st.button("← Dashboard", use_container_width=True):
            _go_to("dashboard")

    st.markdown('<div class="page-title">New Scenario</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">'
        'Enter an OT incident scenario. The platform will analyze the scenario '
        'and prepare the operational summary before stakeholder evaluation.'
        '</div>',
        unsafe_allow_html=True,
    )

    if "new_scenario_id" not in st.session_state:
        st.session_state["new_scenario_id"] = generate_scenario_id()

    scenario_id = st.session_state["new_scenario_id"]
    left, right = st.columns([2.1, 1], gap="large")

    with left:
        st.markdown(
            """
            <div class="section-title">Scenario Information</div>
            <div class="section-note">
                Describe the incident clearly enough for the AI analysis and stakeholder response workflow.
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.text_input("Scenario ID", value=scenario_id, disabled=True)

        scenario_title = st.text_input(
            "Scenario Title",
            placeholder="Example: PLC Communication Failure in Tank Farm",
            key="scenario_title_input",
        )

        scenario_text = st.text_area(
            "Incident Scenario",
            placeholder=(
                "Describe what happened, the affected area or equipment, "
                "observed alarms or failures, operational impact, and any known system state..."
            ),
            height=280,
            key="scenario_text_input",
        )

        if st.button("Analyze Scenario", type="primary", use_container_width=True):
            cleaned_title = scenario_title.strip()
            cleaned_text = scenario_text.strip()

            if not cleaned_title:
                st.warning("Please enter a scenario title.")
            elif not cleaned_text:
                st.warning("Please enter the incident scenario.")
            else:
                try:
                    with st.spinner("Analyzing the OT incident scenario..."):
                        analysis = analyze_scenario(cleaned_text)

                    st.session_state["new_scenario_preview"] = {
                        "scenario_id": scenario_id,
                        "scenario_title": cleaned_title,
                        "scenario_text": cleaned_text,
                        "analysis": _analysis_to_dict(analysis),
                    }
                    st.success("Scenario analysis completed.")
                except Exception as error:
                    st.error(f"Scenario analysis failed: {error}")

    with right:
        st.markdown(
            """
            <div class="panel-card">
                <div class="section-title">What happens next?</div>
                <div class="section-note">
                    The AI extracts a concise operational summary from the scenario.
                    Nothing is saved until you review and confirm it.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="panel-card">
                <div class="section-title">Evaluation Roles</div>
                <div class="section-note">
                    Maintenance<br><br>
                    Operations<br><br>
                    Production<br><br>
                    OT Cybersecurity
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    preview = st.session_state.get("new_scenario_preview")
    if not preview:
        return

    analysis = preview["analysis"]

    st.write("")
    st.markdown('<div class="section-title">Scenario Summary</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">'
        'Review the AI-extracted operational summary before saving the scenario.'
        '</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    summary_items = [
        ("Asset / Area", _summary_value(analysis.get("asset_area"))),
        ("Severity", _summary_value(analysis.get("severity"))),
        ("PLC Status", _summary_value(analysis.get("plc_status"))),
        ("HMI Status", _summary_value(analysis.get("hmi_status"))),
        ("Network Status", _summary_value(analysis.get("network_status"))),
        ("Last Known State", _summary_value(analysis.get("last_known_state"))),
        (
            "Active Alarms",
            "Unknown" if analysis.get("active_alarms") is None else str(analysis.get("active_alarms")),
        ),
    ]

    summary_columns = [c1, c2, c3, c4]
    for index, (label, value) in enumerate(summary_items):
        with summary_columns[index % 4]:
            st.markdown(
                f"""
                <div class="metric-card" style="margin-bottom:1rem;">
                    <div class="metric-label">{escape(label)}</div>
                    <div class="metric-value" style="font-size:1.15rem;">{escape(value)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        f"""
        <div class="panel-card">
            <div class="section-title">{escape(preview["scenario_title"])}</div>
            <div class="section-note">{escape(preview["scenario_id"])}</div>
            <div style="color:#263348; line-height:1.65;">
                {escape(preview["scenario_text"])}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    save_col, clear_col, _ = st.columns([1.3, 1, 3.5])

    with save_col:
        if st.button("Save & View HMI", type="primary", use_container_width=True):
            try:
                save_scenario(
                    scenario_id=preview["scenario_id"],
                    scenario_title=preview["scenario_title"],
                    scenario_text=preview["scenario_text"],
                )
                save_scenario_analysis(
                    scenario_id=preview["scenario_id"],
                    analysis_data=analysis,
                )

                st.session_state["active_scenario_id"] = preview["scenario_id"]
                st.session_state["active_scenario_title"] = preview["scenario_title"]
                st.session_state["active_scenario_text"] = preview["scenario_text"]
                st.session_state["active_scenario_analysis"] = analysis

                st.session_state["new_scenario_id"] = generate_scenario_id()
                _reset_form()
                _go_to("hmi_visualization")

            except Exception as error:
                st.error(f"Could not save the scenario: {error}")

    with clear_col:
        if st.button("Clear", use_container_width=True):
            _reset_form()
            st.session_state["new_scenario_id"] = generate_scenario_id()
            st.rerun()
