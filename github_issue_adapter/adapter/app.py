import os
from datetime import datetime, timedelta, timezone

import pyexasol

from adapter.github_issue_fetcher import GithubIssuesFetcher


def lambda_handler(event, context):
    schema_name = get_config_value('EXASOL_SCHEMA')
    table_name = get_config_value('EXASOL_TABLE')
    exasol = pyexasol.connect(dsn=get_config_value('EXASOL_HOST'), user=get_config_value('EXASOL_USER'),
                              password=get_config_value('EXASOL_PASS'))
    exasol.execute("ALTER SESSION SET  TIME_ZONE = 'UTC';")

    def get_last_update():
        result: list = exasol.export_to_list("SELECT MAX(UPDATED) as last_update FROM " + schema_name + "." + table_name)
        if len(result[0]) == 0:
            return datetime.now() - timedelta(days=365 * 3)
        else:
            last_update_str = result[0][0]
            return datetime.strptime(last_update_str, '%Y-%m-%d %H:%M:%S.%f')

    last_update = get_last_update()
    issue_fetcher = GithubIssuesFetcher("exasol", get_config_value("GITHUB_TOKEN"))
    repos = issue_fetcher.list_repositories()
    for repo in repos:
        issues = issue_fetcher.get_issues_of_repo(repo, last_update)
        rows = []
        for issue in issues:
            type_label = get_type_label(issue)
            rows.append([issue.repo, issue.number, issue.title, issue.closed_at, type_label, issue.updated_at,
                         issue.created_at])
        exasol.import_from_iterable(rows, (schema_name, table_name))


def is_type_label(label: str) -> bool:
    return ":" not in label


def get_type_label(issue):
    type_labels = list(filter(is_type_label, issue.labels))
    if not len(type_labels) == 0:
        return type_labels[0]
    else:
        return ""


def get_config_value(config_name: str) -> str:
    if config_name not in os.environ:
        raise RuntimeError("Missing required environment variable {}.".format(config_name))
    else:
        return os.environ[config_name]
