from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit

from .exceptions import InvalidNamuWikiUrl

_ALLOWED_HOSTS = {"namu.wiki", "www.namu.wiki"}


@dataclass(frozen=True, slots=True)
class NamuWikiArticleUrl:
    value: str

    @classmethod
    def from_value(cls, value: str) -> "NamuWikiArticleUrl":
        parsed = urlsplit(value)
        if parsed.scheme != "https" or parsed.hostname not in _ALLOWED_HOSTS:
            raise InvalidNamuWikiUrl("Only HTTPS Namu Wiki article URLs are allowed.")
        if not parsed.path.startswith("/w/"):
            raise InvalidNamuWikiUrl("A Namu Wiki article URL must start with /w/.")

        return cls(
            urlunsplit((parsed.scheme, parsed.netloc, parsed.path, parsed.query, ""))
        )
