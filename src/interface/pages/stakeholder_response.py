from html import escape
import streamlit as st

from src.database.response_repository import save_response
from src.prompts.stakeholder_responsibilities import get_stakeholder_responsibilities

STAKEHOLDERS = ("maintenance", "operations", "production", "ot_cybersecurity")

ROLE_HINTS = {
    "maintenance": "Focus on equipment condition, diagnosis, repair, inspection, technical readiness, and safe restart support.",
    "operations": "Focus on safe process control, alarms, shutdown/startup actions, manual control, and stable operating conditions.",
    "production": "Focus on production impact, priorities, acceptable capacity, constraints, and controlled return to production.",
    "ot_cybersecurity": "Focus on detection, containment, evidence preservation, trusted restoration, communications integrity, and recovery monitoring.",
}

def _go_to(page_name: str) -> None:
    st.session_state["page"] = page_name
    st.rerun()

def _display_value(value) -> str:
    if value is None:
        return "Unknown"
    text = str(value).strip()
    return text.replace("_", " ").title() if text else "Unknown"

def _response_key(stakeholder: str) -> str:
    return f"response_{stakeholder}"

def render_stakeholder_response() -> None:
    scenario_id = st.session_state.get("active_scenario_id")
    scenario_title = st.session_state.get("active_scenario_title")
    scenario_text = st.session_state.get("active_scenario_text")
    analysis = st.session_state.get("active_scenario_analysis") or {}

    if not scenario_id or not scenario_text:
        st.warning("No active scenario was found. Please create a scenario first.")
        if st.button("Go to Dashboard", type="primary"):
            _go_to("dashboard")
        return

    st.markdown('''<div class="app-header"><div class="brand-wrap"><div class="brand-icon">🛡️</div>
    <div><div class="brand-title">AI-Assisted OT Incident Response</div>
    <div class="brand-subtitle">Industrial incident-response evaluation platform</div></div></div></div>''',
    unsafe_allow_html=True)

    nav1, nav2, _ = st.columns([1.1, 1.1, 4])
    with nav1:
        if st.button("← HMI View", use_container_width=True):
            _go_to("hmi_visualization")
    with nav2:
        if st.button("Dashboard", use_container_width=True):
            _go_to("dashboard")

    st.markdown('<div class="page-title">Stakeholder Responses</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Complete one stakeholder response at a time. Each role is evaluated against its own responsibilities.</div>',
                unsafe_allow_html=True)

    current_index = max(0, min(int(st.session_state.get("stakeholder_index", 0)), 3))
    stakeholder = STAKEHOLDERS[current_index]
    role_data = get_stakeholder_responsibilities(stakeholder)
    role_name = role_data["display_name"]

    st.progress((current_index + 1) / 4, text=f"Role {current_index + 1} of 4 — {role_name}")

    left, right = st.columns([2.05, 1], gap="large")

    with left:
        st.markdown(f'''<div class="panel-card" style="border-left:4px solid #2563EB;">
        <div class="metric-label">Current Stakeholder</div>
        <div style="font-size:1.25rem;font-weight:760;color:#172033;margin-bottom:.3rem;">{escape(role_name)}</div>
        <div class="section-note" style="margin-bottom:0;">{escape(role_data["purpose"])}</div></div>''',
        unsafe_allow_html=True)

        st.markdown('<div class="section-title">Your Response</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="section-note">{escape(ROLE_HINTS[stakeholder])}</div>',
                    unsafe_allow_html=True)

        response_text = st.text_area(
            f"{role_name} response",
            key=_response_key(stakeholder),
            height=300,
            placeholder="Describe the actions you would take, what you would verify, who you would coordinate with, and what must be confirmed before recovery.",
            label_visibility="collapsed",
        )

        previous_col, next_col = st.columns([1, 1.45])
        with previous_col:
            if current_index > 0:
                if st.button("← Previous Role", use_container_width=True):
                    st.session_state["stakeholder_index"] = current_index - 1
                    st.rerun()
            else:
                st.button("← Previous Role", disabled=True, use_container_width=True)

        with next_col:
            is_last = current_index == 3
            label = "Save & Continue to Evaluation" if is_last else "Save Response & Continue"

            if st.button(label, type="primary", use_container_width=True):
                cleaned_response = response_text.strip()
                if not cleaned_response:
                    st.warning(f"Please enter the {role_name} response before continuing.")
                else:
                    try:
                        save_response(scenario_id, stakeholder, cleaned_response)
                        if is_last:
                            st.session_state["responses_complete"] = True
                            _go_to("evaluation")
                        else:
                            st.session_state["stakeholder_index"] = current_index + 1
                            st.rerun()
                    except Exception as error:
                        st.error(f"Could not save the response: {error}")

    with right:
        st.markdown(f'''<div class="panel-card">
        <div class="section-title">Scenario</div>
        <div class="section-note">{escape(str(scenario_id))}</div>
        <div style="font-weight:700;color:#172033;margin-bottom:.65rem;">{escape(str(scenario_title or "Untitled Scenario"))}</div>
        <div style="color:#6B778C;font-size:.83rem;line-height:1.55;">{escape(str(scenario_text))}</div></div>''',
        unsafe_allow_html=True)

        st.markdown(f'''<div class="panel-card"><div class="section-title">Operational Summary</div>
        <div class="summary-line"><span>Asset / Area</span><strong>{escape(_display_value(analysis.get("asset_area")))}</strong></div>
        <div class="summary-line"><span>Severity</span><strong>{escape(_display_value(analysis.get("severity")))}</strong></div>
        <div class="summary-line"><span>PLC</span><strong>{escape(_display_value(analysis.get("plc_status")))}</strong></div>
        <div class="summary-line"><span>HMI</span><strong>{escape(_display_value(analysis.get("hmi_status")))}</strong></div>
        <div class="summary-line"><span>Network</span><strong>{escape(_display_value(analysis.get("network_status")))}</strong></div>
        <div class="summary-line"><span>Process</span><strong>{escape(_display_value(analysis.get("last_known_state")))}</strong></div>
        </div>''', unsafe_allow_html=True)
