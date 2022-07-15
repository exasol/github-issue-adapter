import datetime
from typing import List


class Issue:
    def __init__(
        self,
        repo: str,
        number: int,
        title: str,
        created_at: datetime,
        updated_at: datetime,
        closed_at: datetime,
        labels: List[str],
    ):
        self.repo = repo
        self.number = number
        self.title = title
        self.created_at = created_at
        self.updated_at = updated_at
        self.closed_at = closed_at
        self.labels = labels

    def __repr__(self):
        return "Issue(repo: {}, number: {}, title: '{}', created_at: {}, updated_at: {}, closed_at: '{}', labels: {})".format(
            self.repo,
            self.number,
            self.title,
            self.created_at,
            self.updated_at,
            self.closed_at,
            self.labels,
        )
