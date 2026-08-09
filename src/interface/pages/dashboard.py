import streamlit as st

from src.database.scenario_repository import (
    get_scenario_count,
    get_scenario_history,
)
from src.interface.components import (
    metric_card,
    severity_text,
    status_badge,
)


def _safe_count(status: str) -> int:
    try:
        return get_scenario_count(status=status)
    except Exception:
        return 0


def _safe_history(limit: int = 5):
    try:
        return get_scenario_history()[:limit]
    except Exception:
        return []


def _go_to(page_name: str) -> None:
    st.session_state["page"] = page_name
    st.rerun()


def render_dashboard() -> None:
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

    title_col, history_col, new_col = st.columns(
        [4.6, 1.25, 1.25],
        vertical_alignment="center",
    )

    with title_col:
        st.markdown(
            '<div class="page-title">Dashboard</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="page-subtitle">'
            'Overview of OT incident-response scenarios, evaluations, and recent activity.'
            '</div>',
            unsafe_allow_html=True,
        )

    with history_col:
        if st.button(
            "Scenario History",
            use_container_width=True,
        ):
            _go_to("scenario_history")

    with new_col:
        if st.button(
            "＋ New Scenario",
            type="primary",
            use_container_width=True,
        ):
            _go_to("new_scenario")

    total = _safe_count("all")
    evaluated = _safe_count("evaluated")
    drafts = _safe_count("draft")

    all_rows = _safe_history(limit=100)
    scores = []

    for row in all_rows:
        score = row["overall_score"]

        if score is not None:
            try:
                scores.append(float(score))
            except (TypeError, ValueError):
                pass

    average_score = (
        f"{sum(scores) / len(scores):.1f}"
        if scores
        else "—"
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Total Scenarios",
            str(total),
            "All saved scenarios",
        )

    with c2:
        metric_card(
            "Evaluated",
            str(evaluated),
            "Completed team evaluations",
        )

    with c3:
        metric_card(
            "Drafts",
            str(drafts),
            "Awaiting completion",
        )

    with c4:
        metric_card(
            "Average Score",
            average_score,
            "Across evaluated scenarios",
        )

    st.write("")

    st.markdown(
        '<div class="section-title">Recent Scenarios</div>',
        unsafe_allow_html=True,
    )

    recent = _safe_history(limit=5)

    if not recent:
        st.info("No scenarios have been saved yet.")
        return

    for row in recent:
        st.markdown(
            f"""
            <div class="panel-card">
                <b>{row["scenario_title"]}</b><br>
                <span class="scenario-cell muted">{row["scenario_id"]}</span><br><br>
                {status_badge(str(row["status"]))}
                &nbsp; {severity_text(str(row["severity"]))}
                &nbsp; Score: {row["overall_score"] if row["overall_score"] is not None else "—"}
            </div>
            """,
            unsafe_allow_html=True,
        )
