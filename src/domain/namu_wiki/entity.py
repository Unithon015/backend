from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class NamuWikiSection:
    title: str
    level: int
    content: str


@dataclass(frozen=True, slots=True)
class NamuWikiArticle:
    source_url: str
    title: str
    content: str
    sections: tuple[NamuWikiSection, ...] = field(default_factory=tuple)
