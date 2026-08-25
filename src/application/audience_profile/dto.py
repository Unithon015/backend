from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


CONTENT_CATEGORY_OPTIONS = frozenset({
    "beauty_fashion", "health_fitness", "diet", "food", "parenting", "gaming",
    "finance_investing", "daily_life", "entertainment_fandom", "education_information", "travel",
})
AUDIENCE_CONTEXT_OPTIONS = frozenset({
    "teens", "twenties_thirties", "forties_plus", "men", "women",
    "fitness_diet_interest", "parenting", "gaming_fandom", "idol_interest",
    "finance_investing_interest", "general_public",
})
ACCOUNT_PURPOSE_OPTIONS = frozenset({
    "information", "promotion", "review", "fan_community", "daily_life", "humor_satire",
})


class UpsertAudienceProfileRequest(BaseModel):
    content_categories: list[str] = Field(min_length=1, max_length=3)
    audience_contexts: list[str] = Field(min_length=1, max_length=2)
    account_purposes: list[str] = Field(min_length=1, max_length=2)

    @field_validator("content_categories", "audience_contexts", "account_purposes")
    @classmethod
    def unique_items(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("Each option can only be selected once")
        return value

    @field_validator("content_categories")
    @classmethod
    def supported_content_categories(cls, value: list[str]) -> list[str]:
        return _validate_options(value, CONTENT_CATEGORY_OPTIONS, "content_categories")

    @field_validator("audience_contexts")
    @classmethod
    def supported_audience_contexts(cls, value: list[str]) -> list[str]:
        return _validate_options(value, AUDIENCE_CONTEXT_OPTIONS, "audience_contexts")

    @field_validator("account_purposes")
    @classmethod
    def supported_account_purposes(cls, value: list[str]) -> list[str]:
        return _validate_options(value, ACCOUNT_PURPOSE_OPTIONS, "account_purposes")


class AudienceProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    content_categories: list[str]
    audience_contexts: list[str]
    account_purposes: list[str]
    created_at: datetime
    updated_at: datetime


def _validate_options(value: list[str], allowed: frozenset[str], field_name: str) -> list[str]:
    invalid = sorted(set(value) - allowed)
    if invalid:
        raise ValueError(f"Unsupported {field_name}: {', '.join(invalid)}")
    return value
