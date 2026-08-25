class NamuWikiError(Exception):
    """Base error for the Namu Wiki bounded context."""


class InvalidNamuWikiUrl(NamuWikiError):
    pass


class NamuWikiArticleNotFound(NamuWikiError):
    pass


class NamuWikiUnavailable(NamuWikiError):
    pass
