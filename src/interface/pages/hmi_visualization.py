from html import escape

import streamlit as st


def _go_to(page_name: str) -> None:
    st.session_state["page"] = page_name
    st.rerun()


def _normalize(value, fallback="unknown") -> str:
    if value is None:
        return fallback
    text = str(value).strip().lower()
    return text or fallback


def _display(value) -> str:
    return _normalize(value).replace("_", " ").title()


def _status_class(value: str) -> str:
    normalized = _normalize(value)

    if normalized in {"online", "up", "running", "idle", "low"}:
        return "hmi-good"
    if normalized in {"offline", "down", "stopped", "high", "critical"}:
        return "hmi-bad"
    if normalized in {"degraded", "manual", "medium", "unknown"}:
        return "hmi-warning"
    return "hmi-neutral"


def _status_tile(label: str, value: str, detail: str) -> str:
    return f"""
    <div class="hmi-status-tile">
        <div class="hmi-tile-top">
            <span class="hmi-status-dot {_status_class(value)}"></span>
            <span class="hmi-tile-label">{escape(label)}</span>
        </div>
        <div class="hmi-tile-value">{escape(_display(value))}</div>
        <div class="hmi-tile-detail">{escape(detail)}</div>
    </div>
    """


def render_hmi_visualization() -> None:
    scenario_id = st.session_state.get("active_scenario_id")
    scenario_title = st.session_state.get("active_scenario_title")
    scenario_text = st.session_state.get("active_scenario_text")
    analysis = st.session_state.get("active_scenario_analysis") or {}

    if not scenario_id:
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

    back_col, _ = st.columns([1.15, 5])
    with back_col:
        if st.button("← Dashboard", use_container_width=True):
            _go_to("dashboard")

    st.markdown('<div class="page-title">HMI Scenario Visualization</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">'
        'A simplified training visualization of the current OT scenario state. '
        'This page is not connected to a live control system.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="training-banner">
            <strong>Training visualization only</strong>
            <span>Values are derived from the scenario analysis and do not represent live plant telemetry.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    asset_area = analysis.get("asset_area", "Unknown")
    severity = analysis.get("severity", "unknown")
    plc = analysis.get("plc_status", "unknown")
    hmi = analysis.get("hmi_status", "unknown")
    network = analysis.get("network_status", "unknown")
    process = analysis.get("last_known_state", "unknown")
    alarms = analysis.get("active_alarms")
    alarms_text = "Unknown" if alarms is None else str(alarms)

    top1, top2, top3 = st.columns([1.25, 1, 1])

    with top1:
        st.markdown(
            f"""
            <div class="hmi-main-card">
                <div class="hmi-card-label">Affected Area</div>
                <div class="hmi-card-value">{escape(_display(asset_area))}</div>
                <div class="hmi-card-sub">{escape(str(scenario_title or scenario_id))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with top2:
        st.markdown(
            f"""
            <div class="hmi-main-card">
                <div class="hmi-card-label">Scenario Severity</div>
                <div class="hmi-card-value">
                    <span class="hmi-status-dot {_status_class(severity)}"></span>
                    {escape(_display(severity))}
                </div>
                <div class="hmi-card-sub">AI-extracted operational severity</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with top3:
        st.markdown(
            f"""
            <div class="hmi-main-card">
                <div class="hmi-card-label">Active Alarms</div>
                <div class="hmi-card-value">{escape(alarms_text)}</div>
                <div class="hmi-card-sub">Scenario-reported alarm count</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.markdown('<div class="section-title">System Status</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-note">Simplified status blocks generated from the scenario summary.</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(_status_tile("HMI", hmi, "Operator interface availability"), unsafe_allow_html=True)
    with c2:
        st.markdown(_status_tile("PLC", plc, "Controller communication state"), unsafe_allow_html=True)
    with c3:
        st.markdown(_status_tile("Network", network, "Industrial network condition"), unsafe_allow_html=True)
    with c4:
        st.markdown(_status_tile("Process", process, "Last known operating state"), unsafe_allow_html=True)

    st.write("")
    left, right = st.columns([1.6, 1], gap="large")

    with left:
        process_html = f"""<div class="hmi-process-panel">
<div class="hmi-panel-header">
<div>
<div class="hmi-panel-title">Process Overview</div>
<div class="hmi-panel-sub">Simplified HMI-style incident snapshot</div>
</div>
<div class="hmi-mode-pill">{escape(_display(process))}</div>
</div>

<div class="hmi-process-line">
<div class="hmi-node">
<div class="hmi-node-box">FIELD</div>
<div class="hmi-node-caption">Equipment / Sensors</div>
</div>

<div class="hmi-connector">›</div>

<div class="hmi-node">
<div class="hmi-node-box">PLC</div>
<div class="hmi-node-caption">{escape(_display(plc))}</div>
</div>

<div class="hmi-connector">›</div>

<div class="hmi-node">
<div class="hmi-node-box">NET</div>
<div class="hmi-node-caption">{escape(_display(network))}</div>
</div>

<div class="hmi-connector">›</div>

<div class="hmi-node">
<div class="hmi-node-box">HMI</div>
<div class="hmi-node-caption">{escape(_display(hmi))}</div>
</div>
</div>

<div class="hmi-process-note">
Unknown values remain visible rather than being guessed.
</div>
</div>"""

        st.markdown(process_html, unsafe_allow_html=True)

    with right:
        st.markdown(
            f"""
            <div class="panel-card">
                <div class="section-title">Scenario Context</div>
                <div class="section-note">{escape(str(scenario_id))}</div>
                <div style="font-weight:700; color:#172033; margin-bottom:.65rem;">
                    {escape(str(scenario_title or "Untitled Scenario"))}
                </div>
                <div style="color:#6B778C; font-size:.83rem; line-height:1.55;">
                    {escape(str(scenario_text or ""))}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    back_step, next_step, _ = st.columns([1.2, 1.5, 3.5])

    with back_step:
        if st.button("← Back to Scenario", use_container_width=True):
            _go_to("new_scenario")

    with next_step:
        if st.button("Continue to Responses →", type="primary", use_container_width=True):
            st.session_state["stakeholder_index"] = 0
            _go_to("stakeholder_response")