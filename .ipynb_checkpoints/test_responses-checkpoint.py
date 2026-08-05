from src.utils.scenario_id import generate_scenario_id
from src.database.scenario_repository import save_scenario
from src.database.response_repository import (
    save_response,
    get_response,
    get_all_responses,
)


scenario_id = generate_scenario_id()

save_scenario(
    scenario_id=scenario_id,
    scenario_title="PLC Communication Failure",
    scenario_text=(
        "PLC stopped responding while tank level continued rising."
    ),
)


save_response(
    scenario_id=scenario_id,
    stakeholder="ot_cybersecurity",
    answer_text=(
        "Isolate the affected PLC network, preserve logs, "
        "and investigate suspicious communications."
    ),
)

save_response(
    scenario_id=scenario_id,
    stakeholder="maintenance",
    answer_text=(
        "Inspect the PLC-connected equipment, diagnose the failure, "
        "and verify readiness before restart."
    ),
)

save_response(
    scenario_id=scenario_id,
    stakeholder="operations",
    answer_text=(
        "Monitor process variables, place the process in a safe state, "
        "and report the abnormal condition."
    ),
)

save_response(
    scenario_id=scenario_id,
    stakeholder="production",
    answer_text=(
        "Assess production impact, prioritize critical processes, "
        "and delay full production until safe recovery."
    ),
)


maintenance_response = get_response(
    scenario_id=scenario_id,
    stakeholder="maintenance",
)

print("\nRetrieved Maintenance Response:")
print(f"Scenario ID: {maintenance_response['scenario_id']}")
print(f"Stakeholder: {maintenance_response['stakeholder']}")
print(f"Answer: {maintenance_response['answer_text']}")


all_responses = get_all_responses(scenario_id)

print("\nAll Stakeholder Responses:")

for response in all_responses:
    print("\n----------------------------")
    print(f"Stakeholder: {response['stakeholder']}")
    print(f"Answer: {response['answer_text']}")
    print(f"Created At: {response['created_at']}")