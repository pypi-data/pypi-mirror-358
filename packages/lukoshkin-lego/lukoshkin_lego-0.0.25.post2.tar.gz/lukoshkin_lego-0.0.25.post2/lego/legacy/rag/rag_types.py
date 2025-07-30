"""Types used across the RAG pipeline submodule."""

from typing import TypeAlias

TextualizedNodes: TypeAlias = dict[str, list[dict[str, str]]]
