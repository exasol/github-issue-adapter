import datetime
from typing import List
from dataclasses import dataclass


@dataclass
class Issue:
    repo: str
    number: int
    title: str
    created_at: datetime
    updated_at: datetime
    closed_at: datetime
    labels: List[str]
