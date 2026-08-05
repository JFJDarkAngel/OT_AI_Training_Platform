from src.scenario_analysis.analyzer import analyze_scenario


def main() -> None:
    scenario = (
        "Conveyor 2 stopped sending data to the HMI. "
        "PLC-02 is offline, the HMI remains online, "
        "and three communication alarms are active. "
        "The conveyor was running before communication was lost."
    )

    try:
        overview = analyze_scenario(scenario)

        print("\nScenario analysis completed successfully.")
        print(f"Asset / Area: {overview.asset_area}")
        print(f"Severity: {overview.severity}")
        print(f"PLC Status: {overview.plc_status}")
        print(f"HMI Status: {overview.hmi_status}")
        print(f"Network Status: {overview.network_status}")
        print(f"Last Known State: {overview.last_known_state}")
        print(f"Active Alarms: {overview.active_alarms}")

    except Exception as error:
        print("\nScenario analysis failed.")
        print(f"Error type: {type(error).__name__}")
        print(f"Error: {error}")


if __name__ == "__main__":
    main()