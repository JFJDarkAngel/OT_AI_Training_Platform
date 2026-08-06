from datetime import datetime
from html import escape
from textwrap import dedent

import streamlit as st

from src.database.connection import get_connection


def get_dashboard_statistics() -> dict:
    """
    Read dashboard statistics from SQLite.
    """

    connection = get_connection()
    cursor = connection.cursor()

    try:
        total_scenarios = cursor.execute(
            """
            SELECT COUNT(*)
            FROM scenarios
            """
        ).fetchone()[0]

        completed_scenarios = cursor.execute(
            """
            SELECT COUNT(*)
            FROM scenarios
            WHERE status = 'evaluated'
            """
        ).fetchone()[0]

        average_score = cursor.execute(
            """
            SELECT AVG(overall_score)
            FROM scenarios
            WHERE overall_score IS NOT NULL
            """
        ).fetchone()[0]

        latest_scenario = cursor.execute(
            """
            SELECT
                scenario_id,
                updated_at
            FROM scenarios
            WHERE status = 'evaluated'
            ORDER BY updated_at DESC
            LIMIT 1
            """
        ).fetchone()

        reports_generated = cursor.execute(
            """
            SELECT COUNT(*)
            FROM reports
            """
        ).fetchone()[0]

    finally:
        connection.close()

    average_score_text = (
        f"{average_score:.1f}%"
        if average_score is not None
        else "0%"
    )

    if latest_scenario is None:
        last_evaluated_date = "Not available"
        last_evaluated_id = "No evaluated scenarios"
    else:
        last_evaluated_id = latest_scenario["scenario_id"]
        raw_date = latest_scenario["updated_at"]

        try:
            parsed_date = datetime.fromisoformat(
                str(raw_date)
            )

            last_evaluated_date = parsed_date.strftime(
                "%d %b %Y"
            )

        except (TypeError, ValueError):
            last_evaluated_date = str(raw_date)

    return {
        "total_scenarios": total_scenarios,
        "completed_scenarios": completed_scenarios,
        "average_score": average_score_text,
        "last_evaluated_date": last_evaluated_date,
        "last_evaluated_id": last_evaluated_id,
        "reports_generated": reports_generated,
    }


def inject_home_styles() -> None:
    """
    Add CSS styling for the Home Dashboard.
    """

    st.markdown(
        dedent(
            """
            <style>
            .block-container {
                padding-top: 1.5rem;
                padding-bottom: 2rem;
                max-width: 1450px;
            }

            [data-testid="stAppViewContainer"] {
                background:
                    linear-gradient(
                        135deg,
                        #f8fbff 0%,
                        #ffffff 55%,
                        #f1f6fc 100%
                    );
            }

            header[data-testid="stHeader"] {
                background: #0b111c;
            }

            .hero-container {
                padding: 2rem 2.2rem;
                border-radius: 22px;
                background:
                    linear-gradient(
                        110deg,
                        #ffffff 0%,
                        #ffffff 62%,
                        #eaf3ff 100%
                    );
                border: 1px solid #dce6f2;
                box-shadow:
                    0 12px 32px rgba(15, 40, 75, 0.08);
                margin-bottom: 1.1rem;
            }

            .hero-title {
                font-size: 2.8rem;
                line-height: 1.15;
                font-weight: 800;
                color: #0d1f3c;
                margin: 0 0 0.55rem 0;
            }

            .hero-subtitle {
                font-size: 1.3rem;
                color: #135ac5;
                font-weight: 700;
                margin: 0 0 1rem 0;
            }

            .hero-description {
                font-size: 1.05rem;
                line-height: 1.7;
                color: #314562;
                max-width: 760px;
            }

            .metric-card {
                min-height: 175px;
                padding: 1.3rem 1.2rem;
                border-radius: 18px;
                background: #ffffff;
                border: 1px solid #dfe8f2;
                box-shadow:
                    0 8px 22px rgba(22, 50, 85, 0.06);
            }

            .metric-icon {
                font-size: 1.8rem;
                margin-bottom: 0.65rem;
            }

            .metric-label {
                font-size: 0.94rem;
                color: #33435f;
                margin-bottom: 0.45rem;
            }

            .metric-value {
                font-size: 2rem;
                font-weight: 800;
                color: #135ac5;
                line-height: 1.1;
            }

            .metric-value.green {
                color: #24a148;
            }

            .metric-value.purple {
                color: #5537c8;
            }

            .metric-value.orange {
                color: #d97706;
                font-size: 1.3rem;
            }

            .metric-value.teal {
                color: #1597a8;
            }

            .metric-note {
                margin-top: 0.7rem;
                font-size: 0.8rem;
                color: #64748b;
                overflow-wrap: anywhere;
            }

            .info-banner {
                padding: 1.15rem 1.4rem;
                border-radius: 15px;
                background:
                    linear-gradient(
                        90deg,
                        #edf6ff 0%,
                        #f8fbff 100%
                    );
                border: 1px solid #cfe2fa;
                color: #23456f;
                margin-top: 1.1rem;
            }

            .footer-text {
                text-align: center;
                color: #60708a;
                font-size: 0.8rem;
                margin-top: 1.2rem;
            }

            div.stButton > button {
                min-height: 95px;
                border-radius: 16px;
                font-size: 1rem;
                font-weight: 700;
                border: 1px solid #d3dfed;
                box-shadow:
                    0 8px 20px rgba(24, 54, 91, 0.07);
            }

            div.stButton > button[kind="primary"] {
                background:
                    linear-gradient(
                        135deg,
                        #2364d9,
                        #1348ad
                    );
                color: white;
                border: none;
            }
            </style>
            """
        ),
        unsafe_allow_html=True,
    )


def render_metric_card(
    icon: str,
    label: str,
    value: str | int,
    note: str,
    value_class: str = "",
) -> None:
    """
    Render one dashboard metric card.
    """

    safe_label = escape(str(label))
    safe_value = escape(str(value))
    safe_note = escape(str(note))
    safe_class = escape(value_class)

    html = f"""
<div class="metric-card">
    <div class="metric-icon">{icon}</div>
    <div class="metric-label">{safe_label}</div>
    <div class="metric-value {safe_class}">
        {safe_value}
    </div>
    <div class="metric-note">{safe_note}</div>
</div>
"""

    st.markdown(
        dedent(html),
        unsafe_allow_html=True,
    )


def show_home_page() -> None:
    """
    Render the Home Dashboard.
    """

    inject_home_styles()

    stats = get_dashboard_statistics()

    st.markdown(
        dedent(
            """
            <div class="hero-container">
                <div class="hero-title">
                    OT AI Training &amp; Evaluation Platform
                </div>

                <div class="hero-subtitle">
                    AI-supported industrial incident response
                </div>

                <div class="hero-description">
                    Simulate realistic OT incidents, collect
                    stakeholder responses, and evaluate performance
                    with AI-powered analysis aligned with best
                    practices and standards.
                </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    metric_columns = st.columns(5)

    with metric_columns[0]:
        render_metric_card(
            icon="🗂️",
            label="Total Scenarios",
            value=stats["total_scenarios"],
            note="All-time scenarios",
        )

    with metric_columns[1]:
        render_metric_card(
            icon="✅",
            label="Completed Scenarios",
            value=stats["completed_scenarios"],
            note="Completed evaluations",
            value_class="green",
        )

    with metric_columns[2]:
        render_metric_card(
            icon="📈",
            label="Average Score",
            value=stats["average_score"],
            note="Across all evaluated scenarios",
            value_class="purple",
        )

    with metric_columns[3]:
        render_metric_card(
            icon="🕒",
            label="Last Evaluated",
            value=stats["last_evaluated_date"],
            note=stats["last_evaluated_id"],
            value_class="orange",
        )

    with metric_columns[4]:
        render_metric_card(
            icon="📄",
            label="Reports Generated",
            value=stats["reports_generated"],
            note="PDF reports",
            value_class="teal",
        )

    st.write("")

    action_columns = st.columns(2)

    with action_columns[0]:
        if st.button(
            "➕  Start New Scenario\n\n"
            "Create a new incident scenario and begin evaluation",
            type="primary",
            use_container_width=True,
        ):
            st.session_state["current_page"] = "New Scenario"
            st.rerun()

    with action_columns[1]:
        if st.button(
            "📁  View Scenario History\n\n"
            "Browse, search, and manage existing scenarios",
            use_container_width=True,
        ):
            st.session_state["current_page"] = (
                "Scenario History"
            )
            st.rerun()

    st.markdown(
        dedent(
            """
            <div class="info-banner">
                🛡️ This platform helps OT teams improve
                incident-response readiness through AI-driven
                evaluation, best-practice guidance, and
                comprehensive reporting.
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    st.markdown(
        dedent(
            """
            <div class="footer-text">
                © 2026 OT AI Platform.
                Secure. Intelligent. Resilient.
                &nbsp;&nbsp;|&nbsp;&nbsp; Version 1.0.0
            </div>
            """
        ),
        unsafe_allow_html=True,
    )