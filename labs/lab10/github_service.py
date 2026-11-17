import os
from urllib.parse import quote

import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
README_MAX_LENGTH = 4000


class GitHubRepositoryNotFoundError(Exception):
    pass


class GitHubServiceUnavailableError(Exception):
    pass


def fetch_readme(owner, repo):
    url = (
        "https://api.github.com/repos/"
        f"{quote(owner, safe='')}/{quote(repo, safe='')}/readme"
    )
    headers = {"Accept": "application/vnd.github.raw+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 404:
            raise GitHubRepositoryNotFoundError(
                f"GitHub repository {owner}/{repo} was not found"
            )
        response.raise_for_status()
    except GitHubRepositoryNotFoundError:
        raise
    except requests.RequestException as error:
        raise GitHubServiceUnavailableError(
            "Unable to fetch the GitHub README"
        ) from error

    return response.text[:README_MAX_LENGTH]
