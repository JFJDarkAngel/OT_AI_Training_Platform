from datetime import datetime
from uuid import uuid4


def generate_scenario_id() -> str:
    """
    Generate a unique scenario ID.

    Example:
    SCN-20260804-A1B2C3
    """

    date_part = datetime.now().strftime("%Y%m%d")
    random_part = uuid4().hex[:6].upper()

    return f"SCN-{date_part}-{random_part}"


if __name__ == "__main__":
    scenario_id = generate_scenario_id()
    print(f"Generated Scenario ID: {scenario_id}")