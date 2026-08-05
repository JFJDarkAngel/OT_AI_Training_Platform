from src.llm.client import get_openai_client, TEXT_MODEL
from src.scenario_analysis.models import ScenarioOverview


SYSTEM_INSTRUCTIONS = """
You analyze industrial OT incident scenarios.

Extract only information explicitly stated or strongly implied
by the scenario.

Do not invent asset names, alarm counts, or equipment states.

Use these rules:

- asset_area:
  Main affected asset or industrial area.
  Use "Unknown" if it cannot be identified.

- severity:
  low, medium, high, critical, or unknown.

- plc_status:
  online, offline, degraded, or unknown.

- hmi_status:
  online, offline, degraded, or unknown.

- network_status:
  up, down, degraded, or unknown.

- last_known_state:
  running, stopped, idle, manual, or unknown.

- active_alarms:
  Return an integer only when the scenario explicitly gives
  the alarm count.
  Otherwise return null.
"""


def analyze_scenario(
    scenario_text: str,
) -> ScenarioOverview:
    """
    Analyze one OT scenario and return structured summary data.
    """

    cleaned_scenario = scenario_text.strip()

    if not cleaned_scenario:
        raise ValueError("Scenario text cannot be empty.")

    client = get_openai_client()

    response = client.responses.parse(
        model=TEXT_MODEL,
        instructions=SYSTEM_INSTRUCTIONS,
        input=cleaned_scenario,
        text_format=ScenarioOverview,
        store=False,
    )

    overview = response.output_parsed

    if overview is None:
        raise ValueError(
            "The model did not return a valid scenario overview."
        )

    return overview