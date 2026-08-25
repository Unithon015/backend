from dataclasses import dataclass, field

from src.domain.audience_profile.entity import AudienceProfile


@dataclass(frozen=True)
class PolicyCandidate:
    policy_code: str
    title: str
    review_category: str
    source_url: str
    policy_summary: str = ""
    detection_hints: tuple[str, ...] = ()
    applicable_media_types: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReviewContext:
    focus_topics: list[str] = field(default_factory=list)
    policy_candidates: list[PolicyCandidate] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return not (self.focus_topics or self.policy_candidates)


def snapshot_for_audit(
    audience_profile: AudienceProfile | None,
    review_context: ReviewContext,
) -> dict[str, object]:
    return {
        "audience_profile": (
            {
                "content_categories": audience_profile.content_categories,
                "audience_contexts": audience_profile.audience_contexts,
                "account_purposes": audience_profile.account_purposes,
            }
            if audience_profile
            else None
        ),
        "focus_topics": review_context.focus_topics,
        "selected_policy_codes": [
            candidate.policy_code for candidate in review_context.policy_candidates
        ],
    }
