import os

from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI
from pydantic import BaseModel

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None


class ProjectExtraction(BaseModel):
    title: str
    summary: str
    technologies: list[str]


class AIRefusalError(Exception):
    pass


class AIServiceUnavailableError(Exception):
    pass


def extract_project(notes):
    if client is None:
        raise AIServiceUnavailableError("OPENAI_API_KEY is not configured")

    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            temperature=0.1,
            response_format=ProjectExtraction,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract a software project from the user's notes. Return a "
                        "concise project title, a one- or two-sentence summary, and "
                        "a list of technologies explicitly mentioned or clearly "
                        "required by the project."
                    ),
                },
                {"role": "user", "content": notes},
            ],
        )
    except (APIConnectionError, APITimeoutError, APIStatusError) as error:
        raise AIServiceUnavailableError("The AI provider request failed") from error

    message = completion.choices[0].message
    if message.refusal:
        raise AIRefusalError("The AI provider refused the request")
    if message.parsed is None:
        raise AIServiceUnavailableError("The AI provider returned no project details")

    return message.parsed
