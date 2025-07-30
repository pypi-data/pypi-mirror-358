"""Data models for the RAG pipeline."""

from typing import TypedDict

from pydantic import BaseModel, field_validator


class IndexParamSerialized(TypedDict):
    """Index settings for a vector DB."""

    index_type: str
    metric_type: str
    params: dict[str, int]


class EmbedModel(BaseModel):
    """Embedding settings for a vector DB."""

    name: str = "text-embedding-3-large"
    dim: int = 3072

    @field_validator("dim")
    @classmethod
    def validate_dim(cls, value: int) -> int:
        """Validate the embedding dimension."""
        if value < 1:
            raise ValueError("Embedding dimension can't be zero or negative.")
        return value


class IndexParam(BaseModel):
    """Index settings for a vector DB."""

    index_type: str = "IVF_FLAT"
    metric_type: str = "IP"
    nlist: int = 1024

    def serialize(self) -> IndexParamSerialized:
        """Serialize to a dict."""
        return {
            "index_type": self.index_type,
            "params": {"nlist": self.nlist},
            "metric_type": self.metric_type,
        }

    @classmethod
    def from_dict(cls, param: IndexParamSerialized) -> "IndexParam":
        """Create IndexParam model from a dictionary."""
        return cls(
            index_type=param["index_type"],
            metric_type=param["metric_type"],
            nlist=param["params"]["nlist"],
        )


class SearchParam(BaseModel):
    """Search settings for a vector store index."""

    metric_type: str = "IP"
    nprobe: int = 32


class RecursiveCharSplitter(BaseModel):
    """Text splitter settings."""

    chunk_size: int
    chunk_overlap: int

    @field_validator("chunk_size")
    @classmethod
    def validate_chunk_size(cls, value: int) -> int:
        """Validate the chunk size."""
        if value < 16:
            raise ValueError("Too small chunk size.")
        return value


class SentenceWindowSplitter(BaseModel):
    """Text splitter settings."""

    window_size: int
    window_metadata_key: str = "window"
    original_text_metadata_key: str = "original_text"

    @field_validator("window_size")
    @classmethod
    def validate_window(cls, value: int) -> int:
        """Validate the sentence window size."""
        if value < 1:
            raise ValueError("Sentence window size must be at least 1.")
        return value


class HierarchicalSplitter(BaseModel):
    """Hierarchical text splitter settings."""

    chunk_sizes: list[int]
    chunk_overlap: int

    @field_validator("chunk_sizes")
    @classmethod
    def validate_chunk_size(cls, value: list[int]) -> list[int]:
        """Validate the chunk sizes."""
        for i, size in enumerate(value):
            if size < 16:
                raise ValueError(f"Too small chunk size: {value[i]=}.")
        return value


TextSplitter = (
    SentenceWindowSplitter | RecursiveCharSplitter | HierarchicalSplitter
)


class SetupConfig(BaseModel):
    """Configuration for setting up a collection."""

    embed_model: EmbedModel | None = EmbedModel()
    index_param: IndexParam | None = IndexParam()
    search_param: SearchParam | None = SearchParam()
    text_splitter: TextSplitter | None = SentenceWindowSplitter(window_size=4)
    ## Due to bug in FastAPI we can't use a model with all defaults.
    ## At least one attribute should be required.


class UpdateConfig(SetupConfig):
    """Model to update the collection configuration."""

    embed_model: EmbedModel | None = None
    index_param: IndexParam | None = None
    search_param: SearchParam | None = None
    text_splitter: TextSplitter | None = None


class CollectionModel(BaseModel):
    """Collection settings."""

    name: str
    setup_config: SetupConfig = SetupConfig()

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Validate the collection name."""
        if not value:
            raise ValueError("Collection name must not be empty.")
        if " " in value:
            raise ValueError("Collection name must not contain spaces.")
        if value[0].isdigit():
            raise ValueError("Collection name must not start with a digit.")
        if not value.replace("_", "").isalnum() or not value.isascii():
            raise ValueError("Collection name must be alphanumeric and ASCII.")
        return value


class Article(BaseModel):
    """Document model fed to ingestion pipeline."""

    text: str
    metadata: dict[str, str] | None = None


class UserQuery(BaseModel):
    """Model used for retrieval and RAG."""

    text: str


class LLMRerankSpec(BaseModel):
    """Settings for the LLM reranker."""

    choice_batch_size: int = 5
    top_n: int = 5


class AdvancedRAG(BaseModel):
    """Advanced RAG pipeline settings."""

    llm_rerank: LLMRerankSpec | None = LLMRerankSpec()


class UserSpecs(BaseModel):
    """User-specific settings for the RAG pipeline."""

    user_id: str
    collections: list[str]

    similarity_retriever_top_k: int = 5
    similarity_fusion_top_k: int = 5
    fusion_queries: int = 1

    rag_ext: AdvancedRAG | None = None
