import unittest
from datetime import datetime, timedelta

import pytest

from adapter.github_issue_fetcher import GithubIssuesFetcher
import testing_config
from github import Github

TEST_REPO_ORG = "exasol"
TEST_REPO_NAME = "testing-release-robot"


class GithubTestingSetup:
    def __init__(self, test_config, github_client):
        self.test_config = test_config
        self.github_client = github_client


@pytest.fixture
def github_testing_setup() -> GithubTestingSetup:
    test_config = testing_config.read_test_config()
    return GithubTestingSetup(test_config, Github(test_config.github_token()))


def test_list_repositories(github_testing_setup):
    issue_fetcher = GithubIssuesFetcher(TEST_REPO_ORG, github_testing_setup.test_config.github_token())
    repositories = issue_fetcher.list_repositories()
    assert TEST_REPO_NAME in repositories


def test_list_issues(github_testing_setup):
    issue_fetcher = GithubIssuesFetcher(TEST_REPO_ORG, github_testing_setup.test_config.github_token())
    test_repo = github_testing_setup.github_client.get_repo(TEST_REPO_ORG + "/" + TEST_REPO_NAME)
    test_issue_name = "Issue For Testing github-issue-adapter"
    test_issue = test_repo.create_issue(test_issue_name)
    before_creating_issue = test_issue.created_at - timedelta(seconds=1)
    try:
        issues = issue_fetcher.get_issues_of_repo(TEST_REPO_NAME, before_creating_issue)
        issues_of_test_repo = list(filter(lambda issue: issue.repo == TEST_REPO_NAME, issues))
        assert len(issues_of_test_repo) == 1
        assert issues_of_test_repo[0].title == test_issue_name
    finally:
        test_issue.edit(state="CLOSED")
