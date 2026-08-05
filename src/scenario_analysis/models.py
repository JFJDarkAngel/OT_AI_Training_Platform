from typing import Literal

from pydantic import BaseModel, Field


SeverityValue = Literal[
    "low",
    "medium",
    "high",
    "critical",
    "unknown",
]

EquipmentStatus = Literal[
    "online",
    "offline",
    "degraded",
    "unknown",
]

NetworkStatus = Literal[
    "up",
    "down",
    "degraded",
    "unknown",
]

ProcessState = Literal[
    "running",
    "stopped",
    "idle",
    "manual",
    "unknown",
]


class ScenarioOverview(BaseModel):
    """
    Structured operational summary extracted from a scenario.
    """

    asset_area: str = Field(
        description=(
            "The main industrial asset or area affected by the incident."
        )
    )

    severity: SeverityValue

    plc_status: EquipmentStatus
    hmi_status: EquipmentStatus
    network_status: NetworkStatus

    last_known_state: ProcessState

    active_alarms: int | None = Field(
        default=None,
        ge=0,
        description=(
            "Number of active alarms explicitly stated in the scenario. "
            "Use null when the number is not known."
        ),
    )