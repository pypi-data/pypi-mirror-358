"""
Exceptions raised during Redshift query execution with the RedshiftData API.


Currently relies on definitions used in psycopg2.errors and includes only:
- SyntaxError
- AmbiguousColumn
- UndefinedColumn
- GroupingError
- InternalError
"""

import re


class RedshiftQueryAbortedError(Exception):
    """Raise when a Redshift query was aborted"""


class RedshiftDataError(Exception):
    """Base class for RedshiftData errors"""

    _error_patterns = [
        (
            "UndefinedColumn",
            re.compile(r"column .*? does not exist"),
            "pattern",
        ),
        (
            "UndefinedTable",
            re.compile(r"relation .*? does not exist"),
            "pattern",
        ),
        (
            "UndefinedFunction",
            re.compile(r"function .*? does not exist"),
            "pattern",
        ),
        (
            "AmbiguousColumn",
            re.compile(r"column reference .*? is ambiguous"),
            "pattern",
        ),
        (
            "InternalError",
            re.compile("internal_? ?error", re.IGNORECASE),
            "pattern",
        ),
        ("SyntaxError", "syntax error at", "occurrence"),
        ("UndefinedTable", "invalid reference to", "occurrence"),
        ("GroupingError", "in the GROUP BY clause", "occurrence"),
        ("NotSupportedError", "is not supported", "occurrence"),
    ]

    def __init__(self, desc: dict, _set_orig_attr: bool = True):
        self.desc = desc
        self.orig = None
        self.message = desc.get("Error", "")
        super().__init__(self.message)

        if _set_orig_attr:
            msg = self.message.split(":", 1)[-1].lstrip()
            self.orig = self.classify_error(msg)
            self.message = f"{self.orig.__class__.__name__}: {msg}"
            self.orig.message = self.message

    def classify_error(self, message: str) -> "RedshiftDataError":
        for error_type, pattern, kind in self._error_patterns:
            if kind == "pattern" and pattern.search(message):
                return globals()[error_type](self.desc, False)
            if kind == "occurrence" and pattern in message:
                return globals()[error_type](self.desc, False)
        return UnknownError(self.desc, False)

    def __str__(self):
        return self.message


class UnknownError(RedshiftDataError):
    """Raise when an unknown error occurs"""


class SyntaxError(RedshiftDataError):
    """Raise when a syntax error occurs"""


class AmbiguousColumn(RedshiftDataError):
    """Raise when a column reference is ambiguous"""


class UndefinedColumn(RedshiftDataError):
    """Raise when a column does not exist"""


class UndefinedTable(RedshiftDataError):
    """Raise when a table does not exist"""


class UndefinedFunction(RedshiftDataError):
    """Raise when a function does not exist"""


class GroupingError(RedshiftDataError):
    """Raise when an error occurs in the GROUP BY clause"""


class NotSupportedError(RedshiftDataError):
    """Raise when a feature is not supported"""


class InternalError(RedshiftDataError):
    """Raise when an internal error occurs"""


# Just an alias for InternalError
InternalError_ = InternalError
