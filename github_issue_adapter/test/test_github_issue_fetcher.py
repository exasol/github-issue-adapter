import unittest
from datetime import datetime, timedelta

from adapter.github_issue_fetcher import GithubIssuesFetcher
import testing_config
from github import Github

TEST_REPO_ORG = "exasol"
TEST_REPO_NAME = "testing-release-robot"


class GitHubIssueFetcherTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        test_config = testing_config.read_test_config()
        cls.test_config = test_config
        cls.github_client = Github(test_config.github_token())

    def test_list_repositories(self):
        issue_fetcher = GithubIssuesFetcher(TEST_REPO_ORG, self.test_config.github_token())
        repositories = issue_fetcher.list_repositories()
        self.assertIn(TEST_REPO_NAME, repositories)

    def test_list_issues(self):
        issue_fetcher = GithubIssuesFetcher(TEST_REPO_ORG, self.test_config.github_token())
        test_repo = self.github_client.get_repo(TEST_REPO_ORG + "/" + TEST_REPO_NAME)
        test_issue_name = "Issue For Testing github-issue-adapter"
        test_issue = test_repo.create_issue(test_issue_name)
        before_creating_issue = test_issue.created_at - timedelta(seconds=1)
        try:
            issues = issue_fetcher.get_issues_of_repo(TEST_REPO_NAME, before_creating_issue)
            issues_of_test_repo = list(filter(lambda issue: issue.repo == TEST_REPO_NAME, issues))
            self.assertEqual(len(issues_of_test_repo), 1)
            self.assertEqual(issues_of_test_repo[0].title, test_issue_name)
        finally:
            test_issue.edit(state="CLOSED")


if __name__ == '__main__':
    unittest.main()
