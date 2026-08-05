from src.utils.scenario_id import generate_scenario_id
from src.database.scenario_repository import (
    save_scenario,
    get_scenario_by_id,
)


scenario_id = generate_scenario_id()

save_scenario(
    scenario_id=scenario_id,
    scenario_title="PLC Communication Failure",
    scenario_text="PLC stopped responding while tank level continued rising.",
)

saved_scenario = get_scenario_by_id(scenario_id)

print("\nRetrieved Scenario:")
print(f"Scenario ID: {saved_scenario['scenario_id']}")
print(f"Title: {saved_scenario['scenario_title']}")
print(f"Scenario: {saved_scenario['scenario_text']}")
print(f"Status: {saved_scenario['status']}")
print(f"Created At: {saved_scenario['created_at']}")