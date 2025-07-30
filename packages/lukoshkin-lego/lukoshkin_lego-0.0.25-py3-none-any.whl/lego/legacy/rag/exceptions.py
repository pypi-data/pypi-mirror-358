"""Exceptions for the RAG pipeline."""


class UserAccessError(Exception):
    """Raise when an user tries to modify state they do not have access to."""


class EntryDoesNotExist(Exception):  # noqa: N818
    """Raise when trying to delete entry that is not in the DB."""


class CollectionNotRegistered(Exception):  # noqa: N818
    """Raise when trying to update/delete a collection absent in the DB."""


class IndexAlreadyExists(Exception):  # noqa: N818
    """Raise when trying to create an index that already exists."""


class QueryTooShort(Exception):  # noqa: N818
    """Raise when the query is too short."""


class LLMSetupError(Exception):
    """Raise when LLM was set up incorrectly."""


class LLMGenerationError(Exception):
    """Raise when an error occurred during the response generation."""


class RetrievalError(Exception):
    """Raise when an error occurred during retrieval."""


class InconsistentSetupConfig(Exception):  # noqa: N818
    """
    Collection creation or update failed due to inconsistent setup config.

    Raised when embedding model or/and index param config is/are incompatible
    with the one/ones already in use.
    """


class NotSupportedNodeParser(Exception):  # noqa: N818
    """Raise when the node parser is not supported."""
