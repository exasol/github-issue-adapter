from typing import List

import requests
from string import Template
import datetime
from adapter.issue import Issue


class IssuesFetcher:

    def __init__(self, org: str, github_token: str):
        self.org = org
        self.github_token = github_token

    def run_query(self, graphql_query: str):
        headers = {"Authorization": "token " + self.github_token}
        request = requests.post('https://api.github.com/graphql', json={'query': graphql_query}, headers=headers)
        if request.status_code == 200:
            return request.json()
        else:
            raise RuntimeError(
                "Filed to run GitHub graphql query. Status code: {}  Reason: '{}' Query: {}".format(request.status_code,
                                                                                                    request.reason,
                                                                                                    graphql_query))

    def list_repositories(self) -> List[str]:
        repos = list()
        query = Template("""
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
        """)

        cursor = None
        while True:
            cursor_string = "null" if cursor is None else ('"' + cursor + '"')
            filled_query = query.substitute(cursor=cursor_string, org=self.org)
            response = self.run_query(filled_query)
            repos.extend(map(lambda edge: edge["node"]["name"], response["data"]["search"]["edges"]))
            if not response["data"]["search"]["pageInfo"]["hasNextPage"]:
                break
            cursor = response["data"]["search"]["pageInfo"]["endCursor"]
        return repos

    def get_issues_of_repo(self, repo_name: str, since: datetime) -> List[Issue]:
        issues: List[Issue] = list()
        query_template = Template("""
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
        """)
        cursor = None
        while True:
            cursor_string = "null" if cursor is None else ('"' + cursor + '"')
            date = render_date(since)
            query = query_template.substitute(org=self.org, repo=repo_name, cursor=cursor_string, since=date)
            response = self.run_query(query)
            page_info = read_issues(issues, repo_name, response, since)
            if not page_info["hasNextPage"]:
                break
            cursor = page_info["endCursor"]
        return issues


def read_issues(issues, repo_name, response, since):
    for each in response["data"]["repository"]["issues"]["edges"]:
        issue = read_issue(repo_name, each["node"])
        if issue.updated_at <= since:
            continue
        issues.append(issue)
    page_info = response["data"]["repository"]["issues"]["pageInfo"]
    return page_info


def read_issue(repo: str, node) -> Issue:
    created_at = parse_date(node["createdAt"])
    updated_at = parse_date(node["updatedAt"])
    closed_at = parse_date(node["closedAt"])
    labels = read_labels(node)
    issue = Issue(repo, node["number"], node["title"], created_at, updated_at, closed_at, labels)
    return issue


def read_labels(node):
    labels: List[str] = list()
    for label_edge in node["labels"]["edges"]:
        labels.append(label_edge["node"]["name"])
    return labels


def parse_date(iso_timestamp: str) -> datetime:
    return None if iso_timestamp is None else datetime.datetime.strptime(iso_timestamp,
                                                                         "%Y-%m-%dT%H:%M:%S%z").replace(
        tzinfo=None)


def render_date(date: datetime) -> str:
    return date.replace(microsecond=0).isoformat() + 'Z'
