from __future__ import annotations

from dataclasses import dataclass
import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.models import (
    NamuWikiIncidentIndexEntryModel,
    PolicyCatalogEntryModel,
)


@dataclass(frozen=True)
class PolicyPromptContext:
    policy_code: str
    title: str
    review_category: str
    source_url: str
    policy_summary: str
    detection_hints: tuple[str, ...]
    applicable_media_types: tuple[str, ...]


@dataclass(frozen=True)
class IncidentPromptContext:
    title: str
    year: int
    source_url: str
    source_type: str
    risk_categories: tuple[str, ...]


_TOKEN_PATTERN = re.compile(r"[0-9A-Za-z가-힣]{2,}")
_STOPWORDS = {
    "관련", "대한", "사건", "사고", "논란", "내용", "영상", "이미지", "텍스트",
    "그리고", "또는", "있는", "없는", "하는", "합니다", "검토", "필요",
}


async def search_relevant_reference_context(
    session: AsyncSession,
    query_text: str,
    *,
    policy_limit: int = 6,
    incident_limit: int = 5,
) -> tuple[list[PolicyPromptContext], list[IncidentPromptContext]]:
    normalized_query, query_tokens = _prepare_query(query_text)
    if not query_tokens:
        return [], []

    policy_result = await session.execute(
        select(PolicyCatalogEntryModel).where(PolicyCatalogEntryModel.is_active.is_(True))
    )
    scored_policies = []
    for entry in policy_result.scalars().all():
        score = _match_score(normalized_query, query_tokens, [entry.title, *(entry.match_keywords or [])])
        if score:
            scored_policies.append((score, entry.policy_code, entry))
    scored_policies.sort(key=lambda item: (-item[0], item[1]))

    scored_incidents = []
    if incident_limit > 0:
        incident_result = await session.execute(
            select(NamuWikiIncidentIndexEntryModel).where(
                NamuWikiIncidentIndexEntryModel.is_active.is_(True)
            )
        )
        for entry in incident_result.scalars().all():
            score = _match_score(
                normalized_query,
                query_tokens,
                [entry.title, *(entry.match_keywords or [])],
            )
            if score:
                scored_incidents.append((score, entry.year, entry.title, entry))
        scored_incidents.sort(key=lambda item: (-item[0], -item[1], item[2]))

    policies = [
        PolicyPromptContext(
            policy_code=entry.policy_code,
            title=entry.title,
            review_category=entry.review_category,
            source_url=entry.source_url,
            policy_summary=entry.policy_summary,
            detection_hints=tuple(entry.detection_hints or []),
            applicable_media_types=tuple(entry.applicable_media_types or []),
        )
        for _, _, entry in scored_policies[:policy_limit]
    ]
    incidents = [
        IncidentPromptContext(
            title=entry.title,
            year=entry.year,
            source_url=entry.source_url,
            source_type=entry.source_type,
            risk_categories=tuple(entry.risk_categories or []),
        )
        for _, _, _, entry in scored_incidents[:incident_limit]
    ]
    return policies, incidents


def _prepare_query(value: str) -> tuple[str, set[str]]:
    normalized = " ".join(value.lower().split())
    tokens = {
        token for token in _TOKEN_PATTERN.findall(normalized)
        if token not in _STOPWORDS
    }
    return normalized, tokens


def _match_score(normalized_query: str, query_tokens: set[str], candidates: list[str]) -> int:
    score = 0
    for candidate in candidates:
        normalized_candidate = " ".join(candidate.lower().split())
        if len(normalized_candidate) >= 2 and normalized_candidate in normalized_query:
            score += 8 if " " in normalized_candidate else 5
        candidate_tokens = {
            token for token in _TOKEN_PATTERN.findall(normalized_candidate)
            if token not in _STOPWORDS
        }
        score += 2 * len(query_tokens & candidate_tokens)
    return score
