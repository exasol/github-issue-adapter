from github import Github
from datetime import datetime, timedelta
import pyexasol
import os


def is_pull_request(issue):
    return issue.pull_request is not None


def lambda_handler(event, context):
    exasol = pyexasol.connect(dsn=os.environ['EXASOL_HOST'], user=os.environ['EXASOL_USER'],
                              password=os.environ['EXASOL_PASS'])
    exasol.execute("ALTER SESSION SET  TIME_ZONE = 'UTC';")

    def get_last_update():
        result: list = exasol.export_to_list("SELECT MAX(UPDATED) as last_update FROM EXASOL_JABR.ISSUES")
        if len(result[0]) == 0:
            return datetime.now() - timedelta(days=100)
        else:
            last_update_str = result[0][0]
            return datetime.strptime(last_update_str, '%Y-%m-%d %H:%M:%S.%f')

    last_update = get_last_update()

    g = Github(os.environ['GITHUB_TOKEN'])
    org = g.get_organization("exasol")
    repos = org.get_repos()
    rows = []
    for repo in repos:
        issues = repo.get_issues(state='all', since=last_update)
        for issue in issues:
            if issue.updated_at <= last_update:
                continue
            if is_pull_request(issue):
                continue
            first_label = ''
            labels = issue.get_labels()
            if labels.totalCount > 0:
                first_label = labels[0].name

            closer = ''
            if issue.closed_by is not None:
                closer = issue.closed_by.login
            rows.append([repo.name, issue.number, issue.title, issue.closed_at, closer, first_label, issue.updated_at,
                         issue.created_at])
    exasol.import_from_iterable(rows, (os.environ['EXASOL_SCHEMA'], os.environ['EXASOL_TABLE']))
