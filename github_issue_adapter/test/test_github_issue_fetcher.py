from datetime import timedelta

import pytest
from github import Github

import testing_config
from adapter.github import IssuesFetcher

TEST_REPO_ORG = "exasol"
TEST_REPO_NAME = "testing-release-robot"


@pytest.fixture
def test_config() -> testing_config.TestConfig:
    return testing_config.read_test_config()


@pytest.fixture
def github_client(test_config: testing_config.TestConfig):
    return Github(test_config.github_token())


def test_list_repositories(test_config: testing_config.TestConfig):
    issue_fetcher = IssuesFetcher(TEST_REPO_ORG, test_config.github_token())
    repositories = issue_fetcher.list_repositories()
    assert TEST_REPO_NAME in repositories


def test_list_issues(test_config: testing_config.TestConfig, github_client: Github):
    issue_fetcher = IssuesFetcher(TEST_REPO_ORG, test_config.github_token())
    test_repo = github_client.get_repo(TEST_REPO_ORG + "/" + TEST_REPO_NAME)
    test_issue_name = "Issue For Testing github-issue-adapter"
    test_issue = test_repo.create_issue(test_issue_name)
    before_creating_issue = test_issue.created_at - timedelta(seconds=1)
    try:
        issues = issue_fetcher.get_issues_of_repo(TEST_REPO_NAME, before_creating_issue)
        issues_of_test_repo = list(
            filter(lambda issue: issue.repo == TEST_REPO_NAME, issues)
        )
        assert len(issues_of_test_repo) == 1
        assert issues_of_test_repo[0].title == test_issue_name
    finally:
        test_issue.edit(state="CLOSED")
