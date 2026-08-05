import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"

load_dotenv(ENV_PATH)

TEXT_MODEL = os.getenv(
    "OPENAI_TEXT_MODEL",
    "gpt-5-mini",
)


@lru_cache(maxsize=1)
def get_openai_client() -> OpenAI:
    """
    Create and reuse one OpenAI client.
    """

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise EnvironmentError(
            f"OPENAI_API_KEY was not found in: {ENV_PATH}"
        )

    return OpenAI(api_key=api_key)


def ask_llm(prompt: str) -> str:
    """
    Send a normal text prompt to OpenAI.
    """

    cleaned_prompt = prompt.strip()

    if not cleaned_prompt:
        raise ValueError("Prompt cannot be empty.")

    response = get_openai_client().responses.create(
        model=TEXT_MODEL,
        input=cleaned_prompt,
        store=False,
    )

    return response.output_text.strip()


class LLMClient:
    """
    Shared compatibility interface for the project.
    """

    def ask(self, prompt: str) -> str:
        return ask_llm(prompt)


client = LLMClient()