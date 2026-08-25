from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IncidentIndexEntry:
    title: str
    year: int
    source_url: str
    risk_categories: tuple[str, ...] = ()
    match_keywords: tuple[str, ...] = ()
    source_type: str = "NAMU_WIKI"


@dataclass(frozen=True)
class IncidentSyncSummary:
    incident_year: int
    discovered_count: int
    inserted_count: int
    updated_count: int
