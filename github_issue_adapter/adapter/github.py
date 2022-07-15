from typing import List

import requests
from string import Template
import datetime
from adapter.issue import Issue


class IssuesFetcher:
    _LIST_REPOSITORIES = Template(
        """
    query { 
      search(query:"org:$org, topic:exasol-integration", type:REPOSITORY, first:100, after: $cursor){
        edges{
            node{
                ... on Repository{
              name
            }
          }
        },
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
    """
    )

    _LIST_ISSUES = Template(
        """
    query { 
      repository(owner:"$org" name:"$repo"){
        issues(first:100, after: $cursor, filterBy: {since: "$since"}){
          edges{
            node{
              title,
              number,
              closedAt,
              updatedAt,
              createdAt,
              labels(first:100) {
                edges {
                  node {
                    name
                  }
                }
              }
            }
          },
          pageInfo {
            hasNextPage
            endCursor
          }
        }
      }
    } 
    """
    )

    def __init__(self, org: str, github_token: str):
        self.org = org
        self.github_token = github_token

    def _execute(self, graphql_query: str):
        headers = {"Authorization": "token " + self.github_token}
        request = requests.post(
            "https://api.github.com/graphql",
            json={"query": graphql_query},
            headers=headers,
        )
        if not request.status_code == 200:
            raise RuntimeError(
                "Filed to run GitHub graphql query. Status code: {}  Reason: '{}' Query: {}".format(
                    request.status_code, request.reason, graphql_query
                )
            )
        return request.json()

    def repositories(self) -> List[str]:
        repos = list()

        cursor = None
        while True:
            cursor_string = "null" if cursor is None else ('"' + cursor + '"')
            filled_query = self._LIST_REPOSITORIES.substitute(
                cursor=cursor_string, org=self.org
            )
            response = self._execute(filled_query)
            repos.extend(
                map(
                    lambda edge: edge["node"]["name"],
                    response["data"]["search"]["edges"],
                )
            )
            if not response["data"]["search"]["pageInfo"]["hasNextPage"]:
                break
            cursor = response["data"]["search"]["pageInfo"]["endCursor"]
        return repos

    def issues(self, repo_name: str, since: datetime) -> List[Issue]:
        _issues: List[Issue] = list()
        cursor = None
        while True:
            cursor_string = "null" if cursor is None else ('"' + cursor + '"')
            date = self.render_date(since)
            query = self._LIST_ISSUES.substitute(
                org=self.org, repo=repo_name, cursor=cursor_string, since=date
            )
            response = self._execute(query)
            page_info = self.read_issues(_issues, repo_name, response, since)
            if not page_info["hasNextPage"]:
                break
            cursor = page_info["endCursor"]
        return _issues

    @classmethod
    def read_issues(cls, issues, repo_name, response, since):
        for each in response["data"]["repository"]["issues"]["edges"]:
            issue = cls.read_issue(repo_name, each["node"])
            if issue.updated_at <= since:
                continue
            issues.append(issue)
        page_info = response["data"]["repository"]["issues"]["pageInfo"]
        return page_info

    @staticmethod
    def read_issue(repo: str, node) -> Issue:
        def _parse(iso_timestamp: str) -> datetime:
            return (
                None
                if iso_timestamp is None
                else datetime.datetime.strptime(
                    iso_timestamp, "%Y-%m-%dT%H:%M:%S%z"
                ).replace(tzinfo=None)
            )

        def _labels(n):
            return [label_edge["node"]["name"] for label_edge in n["labels"]["edges"]]

        created_at = _parse(node["createdAt"])
        updated_at = _parse(node["updatedAt"])
        closed_at = _parse(node["closedAt"])
        labels = _labels(node)

        return Issue(
            repo,
            node["number"],
            node["title"],
            created_at,
            updated_at,
            closed_at,
            labels,
        )

    @staticmethod
    def render_date(date: datetime) -> str:
        return date.replace(microsecond=0).isoformat() + "Z"
