from src.llm.client import client


def main() -> None:
    """
    Test the connection between the project and OpenAI.
    """

    prompt = (
        "Reply with exactly this sentence: "
        "OT AI platform connection successful."
    )

    try:
        response = client.ask(prompt)

        print("\nLLM connection test completed successfully.")
        print(f"Response: {response}")

    except Exception as error:
        print("\nLLM connection test failed.")
        print(f"Error type: {type(error).__name__}")
        print(f"Error: {error}")


if __name__ == "__main__":
    main()