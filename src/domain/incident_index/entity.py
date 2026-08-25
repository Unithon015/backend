from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IncidentIndexEntry:
    title: str
    normalized_title: str
    article_url: str
    incident_year: int


@dataclass(frozen=True)
class IncidentSyncSummary:
    incident_year: int
    discovered_count: int
    inserted_count: int
    updated_count: int
