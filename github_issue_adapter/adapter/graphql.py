import requests
import os
from string import Template
import datetime

org = "exasol"


def get_config_value(config_name: str) -> str:
    if config_name not in os.environ:
        raise Exception("Missing required environment variable {}.".format(config_name))
    else:
        return os.environ[config_name]


headers = {"Authorization": "token " + get_config_value("GITHUB_TOKEN")}


def run_query(graphql_query: str):
    request = requests.post('https://api.github.com/graphql', json={'query': graphql_query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, graphql_query))


def list_repositories() -> list[str]:
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
        filled_query = query.substitute(cursor=cursor_string, org=org)
        response = run_query(filled_query)
        repos.extend(map(lambda edge: edge["node"]["name"], response["data"]["search"]["edges"]))
        if not response["data"]["search"]["pageInfo"]["hasNextPage"]:
            break
        cursor = response["data"]["search"]["pageInfo"]["endCursor"]
    return repos


class Issue:
    def __init__(self, repo: str, number: int, title: str, created_at: datetime, updated_at: datetime,
                 closed_at: datetime, labels: list[str]):
        self.repo = repo
        self.number = number
        self.title = title
        self.created_at = created_at
        self.updated_at = updated_at
        self.closed_at = closed_at
        self.labels = labels

    def __repr__(self):
        return "Issue(repo: {}, number: {}, title: '{}', created_at: {}, updated_at: {}, closed_at: '{}', labels: {})" \
            .format(self.repo, self.number, self.title, self.created_at, self.updated_at, self.closed_at, self.labels)


def get_issues_of_repo(repo_name: str, since: datetime) -> list[Issue]:
    issues: list[Issue] = list()
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
        query = query_template.substitute(org=org, repo=repo_name, cursor=cursor_string, since=render_date(since))
        response = run_query(query)
        for each in response["data"]["repository"]["issues"]["edges"]:
            issue = read_issue(repo_name, each["node"])
            if issue.updated_at <= since:
                raise Exception("Strange, the github filter does not work as expected")
            issues.append(issue)
        page_info = response["data"]["repository"]["issues"]["pageInfo"]
        if not page_info["hasNextPage"]:
            break
        cursor = page_info["endCursor"]
    return issues


def read_issue(repo: str, node) -> Issue:
    created_at = parse_date(node["createdAt"])
    updated_at = parse_date(node["updatedAt"])
    closed_at = parse_date(node["closedAt"])
    labels = read_labels(node)
    issue = Issue(repo, node["number"], node["title"], created_at, updated_at, closed_at, labels)
    return issue


def read_labels(node):
    labels: list[str] = list()
    for label_edge in node["labels"]["edges"]:
        labels.append(label_edge["node"]["name"])
    return labels


def parse_date(iso_timestamp: str) -> datetime:
    return None if iso_timestamp is None else datetime.datetime.strptime(iso_timestamp, "%Y-%m-%dT%H:%M:%S%z").replace(
        tzinfo=None)


def render_date(date: datetime) -> str:
    return date.isoformat()[:-3] + 'Z'
