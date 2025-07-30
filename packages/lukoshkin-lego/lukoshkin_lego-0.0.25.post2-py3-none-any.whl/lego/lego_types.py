"""Types common to all lego submodules."""

from typing import Any, TypeAlias, TypeVar, Union

_T = TypeVar("_T")
OneOrMany = Union[_T, list[_T]]
JSONDict: TypeAlias = dict[str, Any]  # type: ignore[misc]
