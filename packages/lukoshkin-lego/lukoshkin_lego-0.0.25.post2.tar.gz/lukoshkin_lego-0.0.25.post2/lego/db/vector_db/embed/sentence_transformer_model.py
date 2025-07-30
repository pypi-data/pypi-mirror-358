from pymilvus.model.dense import SentenceTransformerEmbeddingFunction

from lego.db.vector_db.models import EmbedModel


class SentenceTransformerModel(EmbedModel):
    """SentenceTransformer embedding model."""

    def __init__(self, model_name: str = "all-mpnet-base-v2", device="cpu"):
        self.embed_fn = SentenceTransformerEmbeddingFunction(
            model_name, device=device
        )
        self.embed_dim = self.inspect_embed_dim()
