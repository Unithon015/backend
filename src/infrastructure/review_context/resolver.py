from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.content.review_context import PolicyCandidate, ReviewContext
from src.domain.audience_profile.entity import AudienceProfile
from src.infrastructure.persistence.models import PolicyCatalogEntryModel


@dataclass(frozen=True)
class _Rule:
    policy_codes: tuple[str, ...] = ()
    focus_topics: tuple[str, ...] = ()


_CONTENT_RULES: dict[str, _Rule] = {
    "beauty_fashion": _Rule(
        policy_codes=("META_BULLYING_HARASSMENT",),
        focus_topics=("외모 평가와 체형 조롱",),
    ),
    "health_fitness": _Rule(
        policy_codes=("META_MISINFORMATION", "META_SUICIDE_SELF_INJURY"),
        focus_topics=("근거 없는 건강 주장", "극단적인 체중 감량"),
    ),
    "diet": _Rule(
        policy_codes=("META_SUICIDE_SELF_INJURY", "META_MISINFORMATION"),
        focus_topics=("섭식 관련 표현", "극단적인 체중 감량", "체형 조롱"),
    ),
    "food": _Rule(
        policy_codes=("META_MISINFORMATION",),
        focus_topics=("식습관을 겨냥한 비하", "건강 효능 단정"),
    ),
    "parenting": _Rule(
        policy_codes=("META_CHILD_SAFETY", "META_MINORS"),
        focus_topics=("아동의 안전과 사생활",),
    ),
    "gaming": _Rule(
        policy_codes=("META_BULLYING_HARASSMENT", "META_HATE_SPEECH"),
        focus_topics=("이용자 집단 비하와 괴롭힘",),
    ),
    "finance_investing": _Rule(
        policy_codes=("META_FRAUD_SCAMS", "META_MISINFORMATION"),
        focus_topics=("수익 보장 표현", "검증되지 않은 금융 정보"),
    ),
    "entertainment_fandom": _Rule(
        policy_codes=("META_BULLYING_HARASSMENT", "META_HATE_SPEECH"),
        focus_topics=("인물·팬덤 대상 괴롭힘",),
    ),
    "education_information": _Rule(
        policy_codes=("META_MISINFORMATION",),
        focus_topics=("사실 확인이 필요한 정보성 주장",),
    ),
}

_AUDIENCE_RULES: dict[str, _Rule] = {
    "teens": _Rule(
        policy_codes=("META_MINORS", "META_CHILD_SAFETY"),
        focus_topics=("미성년자 추가 보호",),
    ),
    "fitness_diet_interest": _Rule(
        policy_codes=("META_SUICIDE_SELF_INJURY",),
        focus_topics=("섭식과 체중 관리 관련 표현",),
    ),
    "parenting": _Rule(
        policy_codes=("META_CHILD_SAFETY",),
        focus_topics=("아동 관련 안전·사생활",),
    ),
    "gaming_fandom": _Rule(
        policy_codes=("META_BULLYING_HARASSMENT",),
        focus_topics=("커뮤니티 내 괴롭힘",),
    ),
    "idol_interest": _Rule(
        policy_codes=("META_BULLYING_HARASSMENT",),
        focus_topics=("인물과 팬덤을 향한 공격 표현",),
    ),
    "finance_investing_interest": _Rule(
        policy_codes=("META_FRAUD_SCAMS", "META_MISINFORMATION"),
        focus_topics=("금융 사기와 수익 보장 표현",),
    ),
}

_PURPOSE_RULES: dict[str, _Rule] = {
    "promotion": _Rule(
        policy_codes=("META_FRAUD_SCAMS", "META_SPAM", "META_THIRD_PARTY_IP"),
        focus_topics=("광고성 주장과 제3자 권리",),
    ),
    "review": _Rule(
        policy_codes=("META_MISINFORMATION",),
        focus_topics=("검증이 필요한 후기·비교 주장",),
    ),
    "fan_community": _Rule(
        policy_codes=("META_BULLYING_HARASSMENT",),
        focus_topics=("팬덤 간 갈등과 괴롭힘",),
    ),
    "humor_satire": _Rule(
        policy_codes=("META_BULLYING_HARASSMENT", "META_HATE_SPEECH"),
        focus_topics=("풍자 맥락의 비하·공격 표현",),
    ),
}


class DatabaseReviewContextResolver:
    """Select compact Meta policy references before the reference review call."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def resolve(self, audience_profile: AudienceProfile | None) -> ReviewContext:
        if not audience_profile:
            return ReviewContext()

        rules = self._rules_for(audience_profile)
        policy_codes = _unique(code for rule in rules for code in rule.policy_codes)
        focus_topics = _unique(topic for rule in rules for topic in rule.focus_topics)
        return ReviewContext(
            focus_topics=focus_topics,
            policy_candidates=await self._find_policies(policy_codes),
        )

    @staticmethod
    def _rules_for(profile: AudienceProfile) -> list[_Rule]:
        return [
            *(_CONTENT_RULES[value] for value in profile.content_categories if value in _CONTENT_RULES),
            *(_AUDIENCE_RULES[value] for value in profile.audience_contexts if value in _AUDIENCE_RULES),
            *(_PURPOSE_RULES[value] for value in profile.account_purposes if value in _PURPOSE_RULES),
        ]

    async def _find_policies(self, policy_codes: list[str]) -> list[PolicyCandidate]:
        if not policy_codes:
            return []
        result = await self._session.execute(
            select(PolicyCatalogEntryModel).where(PolicyCatalogEntryModel.policy_code.in_(policy_codes))
        )
        entries = {entry.policy_code: entry for entry in result.scalars()}
        return [
            PolicyCandidate(
                policy_code=code,
                title=entries[code].title,
                review_category=entries[code].review_category,
                source_url=entries[code].source_url,
                policy_summary=entries[code].policy_summary,
                detection_hints=tuple(entries[code].detection_hints or []),
                applicable_media_types=tuple(entries[code].applicable_media_types or []),
            )
            for code in policy_codes
            if code in entries
        ][:3]


def _unique(values) -> list[str]:
    return list(dict.fromkeys(values))
