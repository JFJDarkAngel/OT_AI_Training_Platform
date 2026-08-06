from copy import deepcopy
from typing import Final, TypedDict


class StakeholderResponsibilityConfig(TypedDict):
    """
    Responsibility configuration for one stakeholder.
    """

    display_name: str
    purpose: str
    expected_responsibilities: list[str]


ALLOWED_STAKEHOLDERS: Final[frozenset[str]] = frozenset(
    {
        "ot_cybersecurity",
        "maintenance",
        "operations",
        "production",
    }
)


STAKEHOLDER_RESPONSIBILITIES: Final[
    dict[str, StakeholderResponsibilityConfig]
] = {
    "maintenance": {
        "display_name": "Maintenance",
        "purpose": (
            "Restore field devices, machinery, "
            "PLC-connected equipment, and supporting utilities."
        ),
        "expected_responsibilities": [
            (
                "Inspect affected field devices, machinery, "
                "and PLC-connected equipment."
            ),
            (
                "Diagnose equipment, instrumentation, electrical, "
                "mechanical, or control-related failures."
            ),
            "Perform or coordinate required repairs.",
            (
                "Verify equipment condition and operational "
                "readiness."
            ),
            "Confirm that equipment is safe before restart.",
            "Support a controlled and safe restart.",
            (
                "Document inspection, repair, testing, "
                "and readiness results."
            ),
            (
                "Coordinate technical readiness with Operations "
                "before restart."
            ),
        ],
    },
    "operations": {
        "display_name": "Operations",
        "purpose": (
            "Maintain safe control of the mine and processing "
            "plant during disruption."
        ),
        "expected_responsibilities": [
            (
                "Monitor process variables and abnormal "
                "operating conditions."
            ),
            (
                "Place affected processes or equipment in a safe "
                "state when necessary."
            ),
            "Execute approved shutdown and startup procedures.",
            (
                "Apply manual controls when automated control "
                "is unavailable or unreliable."
            ),
            (
                "Maintain awareness of alarms, interlocks, "
                "and process conditions."
            ),
            "Report abnormal conditions and operational impacts.",
            (
                "Coordinate with Maintenance and OT Cybersecurity "
                "before restart."
            ),
            (
                "Confirm operational conditions are stable "
                "during recovery."
            ),
        ],
    },
    "production": {
        "display_name": "Production",
        "purpose": (
            "Establish production priorities and acceptable "
            "operating capacity."
        ),
        "expected_responsibilities": [
            "Assess the incident's impact on production.",
            (
                "Identify and prioritize critical production "
                "processes."
            ),
            "Determine acceptable reduced operating capacity.",
            (
                "Coordinate production priorities with Operations "
                "and Maintenance."
            ),
            (
                "Avoid requesting full production before technical "
                "and safety readiness is confirmed."
            ),
            (
                "Authorize a gradual and controlled return "
                "to production."
            ),
            (
                "Monitor production recovery against agreed "
                "priorities."
            ),
            (
                "Document production impacts, constraints, "
                "and recovery decisions."
            ),
        ],
    },
    "ot_cybersecurity": {
        "display_name": "OT Cybersecurity",
        "purpose": (
            "Protect and recover industrial control systems "
            "and networks."
        ),
        "expected_responsibilities": [
            "Detect and investigate possible cyber incidents.",
            (
                "Identify affected industrial control assets "
                "and network segments."
            ),
            (
                "Isolate or contain affected assets when "
                "appropriate."
            ),
            (
                "Preserve logs, forensic evidence, and relevant "
                "system information."
            ),
            (
                "Avoid actions that could destroy evidence "
                "or increase operational risk."
            ),
            (
                "Support restoration of trusted and secure "
                "configurations."
            ),
            (
                "Verify communications and system integrity "
                "before reconnection."
            ),
            "Monitor systems and networks during recovery.",
            (
                "Coordinate containment and recovery with "
                "Operations and Maintenance."
            ),
            (
                "Document incident findings, containment actions, "
                "and recovery status."
            ),
        ],
    },
}


def normalize_stakeholder(
    stakeholder: str,
) -> str:
    """
    Normalize and validate a stakeholder name.
    """

    cleaned_stakeholder = stakeholder.strip().lower()

    if not cleaned_stakeholder:
        raise ValueError(
            "Stakeholder cannot be empty."
        )

    if cleaned_stakeholder not in ALLOWED_STAKEHOLDERS:
        raise ValueError(
            f"Invalid stakeholder: {cleaned_stakeholder}. "
            f"Allowed values: "
            f"{sorted(ALLOWED_STAKEHOLDERS)}"
        )

    return cleaned_stakeholder


def get_stakeholder_responsibilities(
    stakeholder: str,
) -> StakeholderResponsibilityConfig:
    """
    Return a safe copy of one stakeholder configuration.
    """

    cleaned_stakeholder = normalize_stakeholder(
        stakeholder
    )

    return deepcopy(
        STAKEHOLDER_RESPONSIBILITIES[
            cleaned_stakeholder
        ]
    )


def format_stakeholder_responsibilities(
    stakeholder: str,
) -> str:
    """
    Convert stakeholder responsibilities into prompt-ready text.
    """

    responsibility_data = (
        get_stakeholder_responsibilities(
            stakeholder
        )
    )

    responsibility_lines = "\n".join(
        f"- {responsibility}"
        for responsibility in responsibility_data[
            "expected_responsibilities"
        ]
    )

    return (
        f"Stakeholder: "
        f"{responsibility_data['display_name']}\n"
        f"Primary purpose: "
        f"{responsibility_data['purpose']}\n\n"
        "Expected responsibilities:\n"
        f"{responsibility_lines}"
    )


if __name__ == "__main__":
    for stakeholder_name in sorted(
        ALLOWED_STAKEHOLDERS
    ):
        print("\n" + "=" * 70)
        print(
            format_stakeholder_responsibilities(
                stakeholder_name
            )
        )