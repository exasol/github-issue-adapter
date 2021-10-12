from datetime import datetime, timedelta, timezone
import pyexasol
import os
import graphql


def lambda_handler(event, context):
    exasol = pyexasol.connect(dsn=os.environ['EXASOL_HOST'], user=os.environ['EXASOL_USER'],
                              password=os.environ['EXASOL_PASS'])
    exasol.execute("ALTER SESSION SET  TIME_ZONE = 'UTC';")

    def get_last_update():
        result: list = exasol.export_to_list("SELECT MAX(UPDATED) as last_update FROM EXASOL_JABR.ISSUES")
        if len(result[0]) == 0:
            return datetime.now() - timedelta(days=365*3)
        else:
            last_update_str = result[0][0]
            return datetime.strptime(last_update_str, '%Y-%m-%d %H:%M:%S.%f')

    last_update = get_last_update()
    repos = graphql.list_repositories()
    for repo in repos:
        print(repo)
        issues = graphql.get_issues_of_repo(repo, last_update)
        rows = []
        for issue in issues:
            type_label = get_type_label(issue)
            rows.append([issue.repo, issue.number, issue.title, issue.closed_at, type_label, issue.updated_at,
                         issue.created_at])
        exasol.import_from_iterable(rows, (os.environ['EXASOL_SCHEMA'], os.environ['EXASOL_TABLE']))


def get_type_label(issue):
    def is_type_label(label: str) -> bool:
        return ":" not in label

    type_labels = list(filter(is_type_label, issue.labels))
    if not len(type_labels) == 0:
        return type_labels[0]
    else:
        return ""


lambda_handler(None, None)
