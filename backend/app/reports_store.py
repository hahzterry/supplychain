"""In-memory report metadata store."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ReportRecord:
    id: str
    name: str
    template: str
    format: str
    audience: str = "Internal"
    date: str = ""
    pages: int = 0
    blob_name: str = ""
    file_size: int = 0
    generated_by: str = "rashid"


class ReportsStore:
    def __init__(self):
        self._records: list[ReportRecord] = []

    def add(self, record: ReportRecord) -> None:
        self._records.insert(0, record)

    def get(self, report_id: str) -> ReportRecord | None:
        for r in self._records:
            if r.id == report_id:
                return r
        return None

    def list_recent(self, limit: int = 20) -> list[ReportRecord]:
        return self._records[:limit]

    def delete(self, report_id: str) -> None:
        self._records = [r for r in self._records if r.id != report_id]
