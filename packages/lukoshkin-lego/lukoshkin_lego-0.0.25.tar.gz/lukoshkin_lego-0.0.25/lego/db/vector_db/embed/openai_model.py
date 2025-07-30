from loguru import logger
from pymilvus.model.dense import OpenAIEmbeddingFunction

from lego.db.vector_db.models import EmbedModel
from lego.llm.utils.build import openai_like_provider


class OpenAIEmbedModel(EmbedModel):
    """OpenAI embedding model."""

    def __init__(
        self,
        model_name: str = "text-embedding-3-small",
        openai_api_key: str | None = None,
        embed_dim: int = 512,
    ):
        if openai_api_key is None:
            openai_api_key = openai_like_provider("openai").api_key

        if openai_api_key is None:
            logger.warning("Not found OpenAI API key among env vars")
            raise ValueError("OpenAI API key is required")

        self.embed_fn = OpenAIEmbeddingFunction(
            api_key=openai_api_key,
            model_name=model_name,
            dimensions=embed_dim,
        )
        self.model_name = model_name
        self.embed_dim = self.inspect_embed_dim()
        if self.embed_dim != embed_dim:
            logger.warning(f"Provided embed_dim {embed_dim} was ignored")
