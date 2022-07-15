import os
from datetime import datetime, timedelta

import pyexasol

from adapter.github_issue_fetcher import GithubIssuesFetcher


def lambda_handler(event, context):
    """AWS Lambda Entry Point"""
    _, _ = event, context
    schema = _config("EXASOL_SCHEMA")
    table = _config("EXASOL_TABLE")

    connection = pyexasol.connect(
        dsn=_config("EXASOL_HOST"),
        user=_config("EXASOL_USER"),
        password=_config("EXASOL_PASS"),
    )

    connection.execute("ALTER SESSION SET  TIME_ZONE = 'UTC';")
    last_update = _last_update(connection, schema, table)
    issue_fetcher = GithubIssuesFetcher("exasol", _config("GITHUB_TOKEN"))

    repositories = issue_fetcher.list_repositories()
    for repository in repositories:
        issues = issue_fetcher.get_issues_of_repo(repository, last_update)
        connection.import_from_iterable(
            (
                [
                    issue.repo,
                    issue.number,
                    issue.title,
                    issue.closed_at,
                    _type_label(issue),
                    issue.updated_at,
                    issue.created_at,
                ]
                for issue in issues
            ),
            (schema, table),
        )


def _last_update(connection, schema, table):
    result: list = connection.export_to_list(
        f"SELECT MAX(UPDATED) as last_update FROM {schema}.{table}"
    )
    if len(result[0]) == 0:
        return datetime.now() - timedelta(days=365 * 3)
    else:
        last_update_str = result[0][0]
        return datetime.strptime(last_update_str, "%Y-%m-%d %H:%M:%S.%f")


def _type_label(issue):
    """Get the label type for a specific issue"""
    type_labels = list(filter(lambda label: ":" not in label, issue.labels))
    type_labels.append("")
    return type_labels[0]


def _config(name: str) -> str:
    """Get the value of a configuration setting"""
    try:
        return os.environ[name]
    except KeyError as ex:
        raise RuntimeError(
            "Missing required environment variable {}.".format(name)
        ) from ex
