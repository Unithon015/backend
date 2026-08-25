from pydantic import BaseModel

from src.domain.incident_index.entity import IncidentIndexEntry, IncidentSyncSummary
from src.infrastructure.namu_wiki.incident_index import YEARLY_INCIDENT_CATEGORY_URLS


class NamuWikiIncidentEntryResponse(BaseModel):
    title: str
    year: int
    risk_categories: list[str]
    match_keywords: list[str]
    source_url: str
    source_type: str

    @classmethod
    def from_domain(cls, entry: IncidentIndexEntry) -> "NamuWikiIncidentEntryResponse":
        return cls(
            title=entry.title,
            year=entry.year,
            risk_categories=list(entry.risk_categories),
            match_keywords=list(entry.match_keywords),
            source_url=entry.source_url,
            source_type=entry.source_type,
        )


class NamuWikiIncidentIndexResponse(BaseModel):
    incident_year: int
    category_url: str
    entries: list[NamuWikiIncidentEntryResponse]

    @classmethod
    def from_entries(
        cls,
        incident_year: int,
        entries: list[IncidentIndexEntry],
    ) -> "NamuWikiIncidentIndexResponse":
        return cls(
            incident_year=incident_year,
            category_url=YEARLY_INCIDENT_CATEGORY_URLS[incident_year],
            entries=[NamuWikiIncidentEntryResponse.from_domain(entry) for entry in entries],
        )


class NamuWikiIncidentSyncResponse(NamuWikiIncidentIndexResponse):
    discovered_count: int
    inserted_count: int
    updated_count: int

    @classmethod
    def from_sync(
        cls,
        summary: IncidentSyncSummary,
        entries: list[IncidentIndexEntry],
    ) -> "NamuWikiIncidentSyncResponse":
        return cls(
            incident_year=summary.incident_year,
            category_url=YEARLY_INCIDENT_CATEGORY_URLS[summary.incident_year],
            entries=[NamuWikiIncidentEntryResponse.from_domain(entry) for entry in entries],
            discovered_count=summary.discovered_count,
            inserted_count=summary.inserted_count,
            updated_count=summary.updated_count,
        )
