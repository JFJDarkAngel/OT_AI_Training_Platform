import json
from html import escape
from pathlib import Path

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from src.database.connection import get_connection


PROJECT_ROOT = Path(__file__).resolve().parents[2]

REPORTS_FOLDER = PROJECT_ROOT / "reports"

REPORTS_FOLDER.mkdir(
    parents=True,
    exist_ok=True,
)


STAKEHOLDER_DISPLAY_NAMES = {
    "maintenance": "Maintenance",
    "operations": "Operations",
    "production": "Production",
    "ot_cybersecurity": "OT Cybersecurity",
}


def parse_json_list(value: str | None) -> list:
    """
    Convert a JSON text field from SQLite into a Python list.
    """

    if not value:
        return []

    try:
        parsed_value = json.loads(value)

        if isinstance(parsed_value, list):
            return parsed_value

    except json.JSONDecodeError:
        pass

    return [value]


def add_bullet_list(
    story: list,
    items: list,
    styles: dict,
    empty_message: str = "None recorded.",
) -> None:
    """
    Add a readable bullet list to the PDF story.
    """

    if not items:
        story.append(
            Paragraph(
                escape(empty_message),
                styles["BodyText"],
            )
        )
        return

    for item in items:
        if isinstance(item, dict):
            item_text = format_reference(item)
        else:
            item_text = str(item)

        story.append(
            Paragraph(
                f"• {escape(item_text)}",
                styles["BodyText"],
            )
        )


def format_reference(reference: dict) -> str:
    """
    Convert one saved reference dictionary into readable text.
    """

    document_title = reference.get(
        "document_title",
        "Unknown document",
    )

    file_name = reference.get(
        "file_name",
        "Unknown file",
    )

    page_number = reference.get(
        "page_number",
        "Unknown",
    )

    chunk_id = reference.get(
        "chunk_id",
        "Unknown",
    )

    relevance = reference.get(
        "relevance",
        "",
    )

    text = (
        f"{document_title}, page {page_number}, "
        f"file {file_name}, chunk {chunk_id}"
    )

    if relevance:
        text += f". Relevance: {relevance}"

    return text


def get_report_styles() -> dict:
    """
    Create the styles used throughout the PDF report.
    """

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontSize=20,
            leading=24,
            alignment=TA_CENTER,
            spaceAfter=18,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading1"],
            fontSize=15,
            leading=19,
            spaceBefore=12,
            spaceAfter=8,
        )
    )

    styles.add(
        ParagraphStyle(
            name="SubsectionTitle",
            parent=styles["Heading2"],
            fontSize=12,
            leading=15,
            spaceBefore=8,
            spaceAfter=5,
        )
    )

    styles.add(
        ParagraphStyle(
            name="ReportBody",
            parent=styles["BodyText"],
            fontSize=10,
            leading=15,
            spaceAfter=6,
        )
    )

    return styles


def save_report_record(
    scenario_id: str,
    report_path: Path,
) -> None:
    """
    Save or update the generated report path in SQLite.
    """

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO reports (
                scenario_id,
                report_path
            )
            VALUES (?, ?)

            ON CONFLICT(scenario_id)
            DO UPDATE SET
                report_path = excluded.report_path,
                generated_at = CURRENT_TIMESTAMP
            """,
            (
                scenario_id,
                str(report_path),
            ),
        )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def generate_report(
    scenario_id: str,
) -> Path:
    """
    Generate a complete PDF report for one evaluated scenario.
    """

    cleaned_scenario_id = scenario_id.strip()

    if not cleaned_scenario_id:
        raise ValueError(
            "Scenario ID cannot be empty."
        )

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT
                scenario_title,
                scenario_text,
                overall_score,
                executive_summary,
                overall_feedback,
                overall_recommendations,
                status,
                created_at,
                updated_at
            FROM scenarios
            WHERE scenario_id = ?
            """,
            (cleaned_scenario_id,),
        )

        scenario = cursor.fetchone()

        if scenario is None:
            raise ValueError(
                f"Scenario was not found: "
                f"{cleaned_scenario_id}"
            )

        cursor.execute(
            """
            SELECT
                asset_area,
                severity,
                plc_status,
                hmi_status,
                network_status,
                last_known_state,
                active_alarms
            FROM scenario_analysis
            WHERE scenario_id = ?
            """,
            (cleaned_scenario_id,),
        )

        scenario_analysis = cursor.fetchone()

        cursor.execute(
            """
            SELECT
                stakeholder,
                answer_text
            FROM responses
            WHERE scenario_id = ?
            ORDER BY
                CASE stakeholder
                    WHEN 'maintenance' THEN 1
                    WHEN 'operations' THEN 2
                    WHEN 'production' THEN 3
                    WHEN 'ot_cybersecurity' THEN 4
                    ELSE 5
                END
            """,
            (cleaned_scenario_id,),
        )

        responses = cursor.fetchall()

        cursor.execute(
            """
            SELECT
                stakeholder,
                score,
                correct_actions,
                missing_actions,
                incorrect_actions,
                feedback,
                recommendations,
                references_json
            FROM evaluations
            WHERE scenario_id = ?
            ORDER BY
                CASE stakeholder
                    WHEN 'maintenance' THEN 1
                    WHEN 'operations' THEN 2
                    WHEN 'production' THEN 3
                    WHEN 'ot_cybersecurity' THEN 4
                    ELSE 5
                END
            """,
            (cleaned_scenario_id,),
        )

        evaluations = cursor.fetchall()

    finally:
        connection.close()

    report_path = (
        REPORTS_FOLDER
        / f"{cleaned_scenario_id}_report.pdf"
    )

    styles = get_report_styles()

    document = SimpleDocTemplate(
        str(report_path),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=(
            "OT Incident Response "
            "Evaluation Report"
        ),
        author="OT AI Training Platform",
    )

    story: list = []

    scenario_title = scenario[0]
    scenario_text = scenario[1]
    overall_score = scenario[2]
    executive_summary = scenario[3]
    overall_feedback = scenario[4]
    overall_recommendations = parse_json_list(
        scenario[5]
    )
    status = scenario[6]
    created_at = scenario[7]
    updated_at = scenario[8]

    story.append(
        Paragraph(
            "OT Incident Response Evaluation Report",
            styles["ReportTitle"],
        )
    )

    story.append(
        Paragraph(
            (
                f"<b>Scenario ID:</b> "
                f"{escape(cleaned_scenario_id)}"
            ),
            styles["ReportBody"],
        )
    )

    story.append(
        Paragraph(
            (
                f"<b>Scenario Title:</b> "
                f"{escape(str(scenario_title))}"
            ),
            styles["ReportBody"],
        )
    )

    story.append(
        Paragraph(
            f"<b>Status:</b> {escape(str(status))}",
            styles["ReportBody"],
        )
    )

    story.append(
        Paragraph(
            (
                f"<b>Created At:</b> "
                f"{escape(str(created_at))}"
            ),
            styles["ReportBody"],
        )
    )

    story.append(
        Paragraph(
            (
                f"<b>Last Updated:</b> "
                f"{escape(str(updated_at))}"
            ),
            styles["ReportBody"],
        )
    )

    story.append(
        Spacer(
            1,
            12,
        )
    )

    story.append(
        Paragraph(
            "Incident Scenario",
            styles["SectionTitle"],
        )
    )

    story.append(
        Paragraph(
            escape(str(scenario_text)),
            styles["ReportBody"],
        )
    )

    story.append(
        Spacer(
            1,
            10,
        )
    )

    story.append(
        Paragraph(
            "Operational Summary",
            styles["SectionTitle"],
        )
    )

    if scenario_analysis is None:
        story.append(
            Paragraph(
                "No operational summary was saved.",
                styles["ReportBody"],
            )
        )

    else:
        operational_fields = [
            ("Asset / Area", scenario_analysis[0]),
            ("Severity", scenario_analysis[1]),
            ("PLC Status", scenario_analysis[2]),
            ("HMI Status", scenario_analysis[3]),
            ("Network Status", scenario_analysis[4]),
            ("Last Known State", scenario_analysis[5]),
            (
                "Active Alarms",
                (
                    scenario_analysis[6]
                    if scenario_analysis[6] is not None
                    else "Unknown"
                ),
            ),
        ]

        for field_name, field_value in operational_fields:
            story.append(
                Paragraph(
                    (
                        f"<b>{escape(field_name)}:</b> "
                        f"{escape(str(field_value))}"
                    ),
                    styles["ReportBody"],
                )
            )

    story.append(
        PageBreak()
    )

    responses_map = {
        stakeholder: answer_text
        for stakeholder, answer_text in responses
    }

    for evaluation in evaluations:
        stakeholder = evaluation[0]
        score = evaluation[1]

        correct_actions = parse_json_list(
            evaluation[2]
        )

        missing_actions = parse_json_list(
            evaluation[3]
        )

        incorrect_actions = parse_json_list(
            evaluation[4]
        )

        feedback = evaluation[5] or ""

        recommendations = parse_json_list(
            evaluation[6]
        )

        references = parse_json_list(
            evaluation[7]
        )

        display_name = STAKEHOLDER_DISPLAY_NAMES.get(
            stakeholder,
            stakeholder.replace("_", " ").title(),
        )

        story.append(
            Paragraph(
                f"{escape(display_name)} Evaluation",
                styles["SectionTitle"],
            )
        )

        stakeholder_response = responses_map.get(
            stakeholder
        )

        if stakeholder_response:
            story.append(
                Paragraph(
                    "Stakeholder Response",
                    styles["SubsectionTitle"],
                )
            )

            story.append(
                Paragraph(
                    escape(str(stakeholder_response)),
                    styles["ReportBody"],
                )
            )

        story.append(
            Paragraph(
                f"<b>Score:</b> {score}/100",
                styles["ReportBody"],
            )
        )

        story.append(
            Paragraph(
                "Correct Actions",
                styles["SubsectionTitle"],
            )
        )

        add_bullet_list(
            story=story,
            items=correct_actions,
            styles=styles,
        )

        story.append(
            Paragraph(
                "Missing Actions",
                styles["SubsectionTitle"],
            )
        )

        add_bullet_list(
            story=story,
            items=missing_actions,
            styles=styles,
        )

        story.append(
            Paragraph(
                "Incorrect Actions",
                styles["SubsectionTitle"],
            )
        )

        add_bullet_list(
            story=story,
            items=incorrect_actions,
            styles=styles,
        )

        story.append(
            Paragraph(
                "Feedback",
                styles["SubsectionTitle"],
            )
        )

        story.append(
            Paragraph(
                escape(str(feedback)),
                styles["ReportBody"],
            )
        )

        story.append(
            Paragraph(
                "Recommendations",
                styles["SubsectionTitle"],
            )
        )

        add_bullet_list(
            story=story,
            items=recommendations,
            styles=styles,
        )

        story.append(
            Paragraph(
                "References",
                styles["SubsectionTitle"],
            )
        )

        add_bullet_list(
            story=story,
            items=references,
            styles=styles,
            empty_message="No references were recorded.",
        )

        story.append(
            PageBreak()
        )

    story.append(
        Paragraph(
            "Overall Evaluation",
            styles["SectionTitle"],
        )
    )

    overall_score_text = (
        f"{overall_score}/100"
        if overall_score is not None
        else "Not available"
    )

    story.append(
        Paragraph(
            (
                f"<b>Overall Score:</b> "
                f"{escape(overall_score_text)}"
            ),
            styles["ReportBody"],
        )
    )

    story.append(
        Paragraph(
            "Executive Summary",
            styles["SubsectionTitle"],
        )
    )

    story.append(
        Paragraph(
            escape(
                str(
                    executive_summary
                    or "Not available."
                )
            ),
            styles["ReportBody"],
        )
    )

    story.append(
        Paragraph(
            "Overall Feedback",
            styles["SubsectionTitle"],
        )
    )

    story.append(
        Paragraph(
            escape(
                str(
                    overall_feedback
                    or "Not available."
                )
            ),
            styles["ReportBody"],
        )
    )

    story.append(
        Paragraph(
            "Final Recommendations",
            styles["SubsectionTitle"],
        )
    )

    add_bullet_list(
        story=story,
        items=overall_recommendations,
        styles=styles,
        empty_message=(
            "No final recommendations were recorded."
        ),
    )

    document.build(
        story
    )

    save_report_record(
        scenario_id=cleaned_scenario_id,
        report_path=report_path,
    )

    return report_path


if __name__ == "__main__":
    print(
        "Import generate_report() and pass "
        "a valid evaluated Scenario ID."
    )