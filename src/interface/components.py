from html import escape

import streamlit as st


def metric_card(label: str, value: str, note: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{escape(label)}</div>
            <div class="metric-value">{escape(value)}</div>
            <div class="metric-note">{escape(note)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_badge(status: str) -> str:
    normalized = (status or "draft").strip().lower()
    css_class = "badge-evaluated" if normalized == "evaluated" else "badge-draft"
    label = normalized.replace("_", " ").title()

    return f'<span class="badge {css_class}">{escape(label)}</span>'


def severity_text(severity: str) -> str:
    normalized = (severity or "unknown").strip().lower()
    allowed = {"critical", "high", "medium", "low", "unknown"}

    if normalized not in allowed:
        normalized = "unknown"

    return (
        f'<span class="severity-{normalized}">'
        f'{escape(normalized.title())}'
        f'</span>'
    )
