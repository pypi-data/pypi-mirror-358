from typing import Callable, Literal, Protocol

from numpy.typing import NDArray
from pydantic import BaseModel, model_validator

from lego.lego_types import JSONDict, OneOrMany


class MilvusDBSettings(BaseModel):
    """Settings for MilvusDBConnector."""

    collection: str
    partition: str = "_default"
    index_params: JSONDict = {"index_type": "AUTOINDEX", "metric_type": "IP"}
    search_params: JSONDict = {"metric_type": "IP"}
    primary_key: str = "id"
    embedding_field: str = "vector"
    properties: JSONDict = {"collection.ttl.seconds": None}
    consistency_level: Literal[
        "Eventually", "Bounded", "Strong", "Session"
    ] = "Bounded"

    ## likely, redundant settings since we have `radius` and `range_filter`
    # sim_threshold_to_add: float | None = None
    # more_similar_op: str = "gt"  # x (more_similar_op) threshold

    @model_validator(mode="after")
    def validate_properties(self):
        """Remove properties with None values."""
        self.properties = {
            key: value
            for key, value in self.properties.items()
            if value is not None
        }
        return self


class EmbedModel(Protocol):
    """Embedding model protocol."""

    embed_fn: Callable
    embed_dim: int

    def __call__(self, texts: OneOrMany[str]) -> list[NDArray[float]]:
        """Return embeddings for the input texts."""
        return self.embed_fn(texts)

    def inspect_embed_dim(self) -> int:
        """Measure the embedding dimension."""
        return self.embed_fn(["test"])[0].shape[0]
