import os
import uuid
from typing import Annotated, Literal

from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI
from pydantic import BaseModel, StringConstraints

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None


class ProjectExtraction(BaseModel):
    title: str
    summary: str
    technologies: list[str]


class GitHubProjectDraft(BaseModel):
    title: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=120),
    ]
    summary: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    technologies: list[str]
    difficulty: Literal["Beginner", "Intermediate", "Advanced"]


class AIRefusalError(Exception):
    pass


class AIServiceUnavailableError(Exception):
    pass


github_import_sessions = {}


def _request_extraction(messages, response_format):
    if client is None:
        raise AIServiceUnavailableError("OPENAI_API_KEY is not configured")

    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            temperature=0.1,
            response_format=response_format,
            messages=messages,
        )
    except (APIConnectionError, APITimeoutError, APIStatusError) as error:
        raise AIServiceUnavailableError("The AI provider request failed") from error

    message = completion.choices[0].message
    if message.refusal:
        raise AIRefusalError("The AI provider refused the request")
    if message.parsed is None:
        raise AIServiceUnavailableError("The AI provider returned no project details")

    return message.parsed, message.content


def extract_project(notes):
    parsed, _ = _request_extraction(
        [
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
        ProjectExtraction,
    )
    return parsed


def start_github_import(text):
    messages = [
        {
            "role": "system",
            "content": (
                "Extract a software project from the provided text. Return a short "
                "title, a one- or two-sentence summary, a list of technologies, "
                "and difficulty exactly as Beginner, Intermediate, or Advanced."
            ),
        },
        {"role": "user", "content": text},
    ]
    draft, assistant_message = _request_extraction(messages, GitHubProjectDraft)
    session_id = str(uuid.uuid4())
    github_import_sessions[session_id] = {
        "draft": draft,
        "messages": messages
        + [{"role": "assistant", "content": assistant_message or ""}],
    }
    return session_id, draft.model_dump()


def get_github_import_session(session_id):
    return github_import_sessions.get(session_id)


def refine_github_import(session_id, feedback):
    session = get_github_import_session(session_id)
    if session is None:
        return None

    updated_messages = session["messages"] + [
        {"role": "user", "content": feedback}
    ]
    draft, assistant_message = _request_extraction(
        updated_messages,
        GitHubProjectDraft,
    )
    session["draft"] = draft
    session["messages"] = updated_messages + [
        {"role": "assistant", "content": assistant_message or ""}
    ]
    return draft.model_dump()


def refine_github_import_blind(session_id, feedback):
    if get_github_import_session(session_id) is None:
        return None

    draft, _ = _request_extraction(
        [{"role": "user", "content": feedback}],
        GitHubProjectDraft,
    )
    return draft.model_dump()


def clear_github_import_session(session_id):
    return github_import_sessions.pop(session_id, None) is not None
