"""All the RAG functionality but without LLMs."""

import copy

from llama_index.core import Document, VectorStoreIndex
from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.core.node_parser import NodeParser
from llama_index.core.postprocessor import MetadataReplacementPostProcessor
from llama_index.core.schema import BaseNode
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.milvus import MilvusVectorStore
from pymilvus import Collection, connections, utility

from lego.lego_types import JSONDict, OneOrMany
from lego.logger import logger
from lego.rag import mock
from lego.rag.core.ingest_utils import (
    MODEL_TO_LLAMA_PARSER,
    get_emb_size,
    maybe_mend_index,
)
from lego.rag.exceptions import (
    CollectionNotRegistered,
    InconsistentSetupConfig,
    UserAccessError,
)
from lego.rag.models import (
    Article,
    CollectionModel,
    EmbedModel,
    SentenceWindowSplitter,
    SetupConfig,
    UpdateConfig,
)
from lego.rag.rag_types import TextualizedNodes
from lego.settings import MilvusConnection
from lego.utils.llama_casts import cast_to_document


class CollectionSet(mock.CollectionSet):  # noqa: WPS214, WPS230
    """Basic ingestion and retrieval functionality without LLMs."""

    # WPS214 - too many methods
    # WPS230 - too many instance attributes

    def __init__(
        self,
        connection: MilvusConnection,
        embedding_field: str = "embedding",
    ):
        self.conn = connection
        self.emb_field = embedding_field
        connections.connect(uri=connection.uri, token=connection.token)

        self.collections: dict[str, CollectionModel] = {}
        self.up_to_date: dict[str, dict[str, bool]] = {}

        self._indexes: dict[str, VectorStoreIndex] = {}
        self._node_parsers: dict[str, NodeParser] = {}
        self._retrievers: dict[str, BaseRetriever] = {}

    def update_collection(self, collection: str, update_cfg: UpdateConfig):
        """
        Register a new collection or update existing one.

        Allow partial updates if some of the submodels are missing (None).
        """
        if collection not in self.collections:
            if utility.has_collection(collection):
                raise UserAccessError(
                    "You can't access previously created collections.",
                )
            self.collections[collection] = CollectionModel(
                name=collection, setup_config=update_cfg
            )
            self.up_to_date[collection] = {"index": False, "retriever": False}
            return

        if not self.is_consistent_with_existing_setup(collection, update_cfg):
            raise InconsistentSetupConfig(
                "Your collection setup conflicts with"
                " the existing collection configuration"
            )

        cfg = self.collections[collection].setup_config
        for field, new_value in update_cfg:
            if new_value is not None:
                new_value = copy.deepcopy(new_value)
                setattr(cfg, field, new_value)

        self.up_to_date[collection] = {"index": False, "retriever": False}

    def is_consistent_with_existing_setup(
        self, name: str, setup: SetupConfig
    ) -> bool:
        """
        Check if the new collection setup is consistent with the existing one.

        If there is no collection of the same name with which to compare,
        then the setup is considered consistent.

        NOTE: In light of the current implementation, only simple checks are
        included. We know if the collection name in the dict `self.indexes`
        then the corresponding collection in Milvus exists and its populated
        by a few entities due to laziness of the index creation.
        """
        if name not in self._indexes:
            return True

        curr_index_param = Collection(name).index().params
        curr_embed_model = EmbedModel(
            ## WPS437 - protected attribute access
            name=self._indexes[name]._embed_model.model_name,  # noqa: WPS437
            dim=get_emb_size(name, self.emb_field),
        )
        return (
            setup.embed_model == curr_embed_model
            and setup.index_param == curr_index_param
        )

    def drop_collection(self, collections: OneOrMany[str]) -> list[str]:
        """Drop a collection by name."""
        if isinstance(collections, str):
            collections = [collections]

        dropped = []
        for collection_name in collections:
            if self.collections.pop(collection_name, None):
                dropped.append(collection_name)
                if utility.has_collection(collection_name):
                    utility.drop_collection(collection_name)
            else:
                logger.warning(
                    f"Collection '{collection_name}' is not registered.",
                )
        return dropped

    def ingest_documents(
        self,
        documents: OneOrMany[JSONDict | Article | Document],
        collection: str,
    ) -> list[str]:
        """
        Add data to the specified collection in the DB.

        Returns: list of document IDs.
        """
        if collection not in self.collections:
            raise CollectionNotRegistered(
                f"Collection '{collection}' is not registered.",
            )

        if isinstance(documents, (dict, Article, Document)):
            documents = [documents]

        documents = [cast_to_document(doc) for doc in documents]
        self.prepare_to_ingest(collection)
        self._indexes[collection].insert_nodes(
            self._node_parsers[collection].get_nodes_from_documents(documents),
        )
        return [doc.id_ for doc in documents]

    def retrieve(
        self,
        query: str,
        collections: OneOrMany[str],
        similarity_top_k: int = 5,
    ) -> TextualizedNodes:
        """Retrieve documents from the specified collection."""
        if isinstance(collections, str):
            collections = [collections]

        self.build_retrievers(collections, similarity_top_k)
        textualized_nodes: TextualizedNodes = {}
        for collection in collections:
            textualized_nodes[collection] = []
            for node in self._retrievers[collection].retrieve(query):
                textualized_nodes[collection].append(
                    {
                        "text": node.text,
                        "metadata": "\n\n".join(
                            f"{k}:{v}" for k, v in node.metadata.items()
                        ),
                    }
                )
        return textualized_nodes

    def retrieve_llama_nodes(
        self,
        query: str,
        collections: OneOrMany[str],
        similarity_top_k: int = 5,
    ) -> dict[str, list[BaseNode]]:
        """Retrieve documents from the specified collection."""
        if isinstance(collections, str):
            collections = [collections]

        self.build_retrievers(collections, similarity_top_k)
        nodes: dict[str, list[BaseNode]] = {}
        for collection in collections:
            nodes[collection] = self._retrievers[collection].retrieve(query)

        return nodes

    def prepare_to_ingest(self, collections: OneOrMany[str] | None = None):
        """Create indexes and text splitters for the provided collections."""
        if collections is None:
            collections = self.collections.keys()

        if isinstance(collections, str):
            collections = [collections]

        for collect_name in collections:
            if self.up_to_date[collect_name]["index"]:
                continue

            cfg = self.collections[collect_name].setup_config
            if not self.is_consistent_with_existing_setup(collect_name, cfg):
                raise InconsistentSetupConfig(
                    "Your collection setup conflicts with"
                    " the existing collection configuration"
                )
            vector_store = MilvusVectorStore(
                uri=self.conn.uri,
                token=self.conn.token,
                collection_name=collect_name,
                dim=cfg.embed_model.dim,
                embedding_field=self.emb_field,
                similarity_metric=cfg.index_param.metric_type,
                index_config=cfg.index_param.serialize(),
                search_config=cfg.search_param.model_dump(),
                use_async=True,  # not sure if it gives any performance boost
            )
            maybe_mend_index(self.collections[collect_name], self.emb_field)
            self.up_to_date[collect_name]["index"] = True
            self._indexes[collect_name] = VectorStoreIndex.from_vector_store(
                embed_model=OpenAIEmbedding(model=cfg.embed_model.name),
                vector_store=vector_store,
            )
            logger.info(f"Created index for '{collect_name}'.")
            Collection(collect_name).load()

            self._node_parsers[collect_name] = MODEL_TO_LLAMA_PARSER[
                type(cfg.text_splitter)
            ](**cfg.text_splitter.model_dump())

    def list_collections(self) -> dict[str, list[str]]:
        """List all collections and those registered by this class."""
        return {
            "all": utility.list_collections(),
            "registered": list(self.collections.keys()),
        }

    def force_register(self, collection: str, setup_cfg: SetupConfig):
        """Register collection forcefully (SHOULD NOT BE EXPOSED)."""
        if not utility.has_collection(collection):
            raise CollectionNotRegistered(
                f"Collection '{collection}' was never registered."
            )
        self.up_to_date[collection] = {"index": False, "retriever": False}
        self.collections[collection] = CollectionModel(
            name=collection, setup_config=setup_cfg
        )

    def force_drop(self, collection_name: str):
        """
        Drop a collection by name (SHOULD NOT BE EXPOSED).

        In case of dropping collection only on the Milvus side, it still cannot
        be a class method since the Milvus connection should be established in
        the __init__ method first.
        """
        self.collections.pop(collection_name, None)
        if utility.has_collection(collection_name):
            utility.drop_collection(collection_name)

    def build_retrievers(
        self,
        collections: OneOrMany[str],
        similarity_top_k: int | None = None,
    ) -> list[BaseRetriever]:
        """
        Get retrievers for the specified collections.

        It is possible to implement passing top_k per collection.
        """
        if isinstance(collections, str):
            collections = [collections]

        self.prepare_to_ingest(collections)
        for collection_name in collections:
            if self.up_to_date[collection_name]["retriever"]:
                continue

            ts = self.collections[collection_name].setup_config.text_splitter
            self.up_to_date[collection_name]["retriever"] = True
            self._retrievers[collection_name] = self._indexes[
                collection_name
            ].as_retriever(
                similarity_top_k=similarity_top_k,
                node_postprocessors=(
                    MetadataReplacementPostProcessor(
                        target_metadata_key=ts.window_metadata_key,
                    )
                    if isinstance(ts, SentenceWindowSplitter)
                    else None
                ),
            )
        return list(self._retrievers.values())
