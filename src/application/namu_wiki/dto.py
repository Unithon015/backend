from pydantic import AnyHttpUrl, BaseModel, ConfigDict

from src.domain.namu_wiki.entity import NamuWikiArticle, NamuWikiSection


class CrawlNamuWikiArticleRequest(BaseModel):
    url: AnyHttpUrl


class NamuWikiSectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    level: int
    content: str

    @classmethod
    def from_domain(cls, section: NamuWikiSection) -> "NamuWikiSectionResponse":
        return cls(title=section.title, level=section.level, content=section.content)


class NamuWikiArticleResponse(BaseModel):
    source_url: str
    title: str
    content: str
    sections: list[NamuWikiSectionResponse]

    @classmethod
    def from_domain(cls, article: NamuWikiArticle) -> "NamuWikiArticleResponse":
        return cls(
            source_url=article.source_url,
            title=article.title,
            content=article.content,
            sections=[NamuWikiSectionResponse.from_domain(section) for section in article.sections],
        )
