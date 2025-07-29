import pytest
from datetime import datetime, timedelta
import os
from typing import Iterator


from langchain_stack_overflow_for_teams.loader import (
    StackOverflowTeamsApiV3Loader,
)


@pytest.fixture(name="access_token")
def fixture_access_token() -> Iterator[str]:
    yield get_env_var("SO_API_TOKEN", "API token for Stack Overflow for Teams API v3")


@pytest.fixture(name="team")
def fixture_team() -> Iterator[str]:
    yield get_env_var("TEAM", "Team Stack Overflow for Teams API v3")


def test_stack_overflow_for_teams_articles(
    access_token: str, team: str, content_type: str = "articles"
) -> None:
    loader = StackOverflowTeamsApiV3Loader(
        access_token=access_token,
        team=team,
        content_type=content_type,
        date_from=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%dT00:00:00Z"),
    )

    returned_docs = loader.load()

    assert len(returned_docs) >= 1
    assert returned_docs[0].metadata != {}


def test_stack_overflow_for_teams_questions(
    access_token: str, team: str, content_type: str = "questions"
) -> None:
    loader = StackOverflowTeamsApiV3Loader(
        access_token=access_token,
        team=team,
        content_type=content_type,
        date_from=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%dT00:00:00Z"),
    )

    returned_docs = loader.load()

    assert len(returned_docs) >= 1
    assert returned_docs[0].metadata != {}


def get_env_var(key: str, desc: str) -> str:
    v = os.environ.get(key)
    if v is None:
        raise ValueError(f"Must set env var {key} to: {desc}")
    return v
