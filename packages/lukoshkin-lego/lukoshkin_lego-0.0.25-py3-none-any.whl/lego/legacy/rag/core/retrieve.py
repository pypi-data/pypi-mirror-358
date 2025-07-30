"""Basic RAG functionality (generation part)."""

from easydict import EasyDict
from llama_index.core import ChatPromptTemplate
from llama_index.core.postprocessor import LLMRerank
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.llms.anyscale import Anyscale
from llama_index.llms.openai import OpenAI

from lego.constants import ANYSCALE_MODELS, OPENAI_MODELS
from lego.llm.settings import LlamaLLMChatSettings, OpenAILikeProvider
from lego.logger import logger
from lego.rag.exceptions import CollectionNotRegistered, LLMSetupError
from lego.rag.mock import CollectionSet, SourcedQueryEngine
from lego.rag.models import UserQuery, UserSpecs

SYSTEM_MESSAGE = (
    "Based on the provided context, answer a user question. "
    "If there is no way to answer the question using the context, write "
    " that there is no information available in the databases."
)
USER_PROMPT = (
    "Context information is below.\n---\n{context_str}\n---\nGiven the "
    "context information and not the prior knowledge, answer shortly the "
    "question: {query_str}\n"
)


class RAGQueryEngine(SourcedQueryEngine):  # noqa: WPS214
    """Wrapper for the LLM model and the retrieval engine."""

    # WPS214 - too many methods

    def __init__(self, collections: CollectionSet):
        self.collections = collections
        self.per_user_cache = EasyDict(
            {"specs": {}, "llm_settings": {}, "llm": {}, "query_engine": {}}
        )

    def query(
        self,
        query: UserQuery,
        specs: UserSpecs,
        llm_settings: LlamaLLMChatSettings,
    ) -> str:
        """Generate response from relevant text chunks from `collections`."""
        query_engine = self.update_query_engine(specs, llm_settings)
        return query_engine.query(query.text)

    async def aquery(
        self,
        query: UserQuery,
        specs: UserSpecs,
        llm_settings: LlamaLLMChatSettings,
    ) -> str:
        """Async version of `self.query`."""
        query_engine = self.update_query_engine(specs, llm_settings)
        return await query_engine.aquery(query.text)

    @classmethod
    def list_supported_models(cls) -> set[str]:
        """List the supported models for the LLM."""
        return ANYSCALE_MODELS | OPENAI_MODELS

    def update_query_engine(
        self, specs: UserSpecs, llm_settings: LlamaLLMChatSettings
    ) -> RetrieverQueryEngine:
        """Build, update, or return from the cache the query engine."""
        for collection in specs.collections:
            if collection not in self.collections.collections:
                raise CollectionNotRegistered(
                    f"Collection '{collection}' is not registered.",
                )
        if self._is_engine_update_required(specs, llm_settings):
            logger.info("Updating the query engine..")
            self._build_query_engine(specs, llm_settings)
        return self.per_user_cache.query_engine[specs.user_id]

    def _cache_up(
        self,
        specs: UserSpecs,
        llm_settings: LlamaLLMChatSettings,
        llm: Anyscale | OpenAI,
        query_engine: RetrieverQueryEngine,
    ):
        """Remember specs and llm_settings to reuse the engine and llm."""
        self.per_user_cache.specs[specs.user_id] = specs
        self.per_user_cache.llm_settings[specs.user_id] = llm_settings
        self.per_user_cache.llm[specs.user_id] = llm
        self.per_user_cache.query_engine[specs.user_id] = query_engine

    def _build_query_engine(
        self, specs: UserSpecs, llm_settings: LlamaLLMChatSettings
    ):
        """Build the query engine."""
        llm = self._set_up_llm(specs.user_id, llm_settings)
        node_postprocessors = []
        if specs.rag_ext and specs.rag_ext.llm_rerank:
            node_postprocessors.append(
                LLMRerank(**specs.rag_ext.llm_rerank.model_dump()),
            )
        engine = RetrieverQueryEngine.from_args(
            QueryFusionRetriever(
                self.collections.build_retrievers(
                    specs.collections, specs.similarity_retriever_top_k
                ),
                llm=llm,
                similarity_top_k=specs.similarity_fusion_top_k,
                num_queries=specs.fusion_queries,
            ),
            node_postprocessors=node_postprocessors,
            text_qa_template=ChatPromptTemplate.from_messages(
                [("system", SYSTEM_MESSAGE), ("user", USER_PROMPT)]
            ),
        )
        self._cache_up(specs, llm_settings, llm, engine)

    def _is_engine_update_required(
        self, specs: UserSpecs, llm_settings: LlamaLLMChatSettings
    ) -> bool:
        """Determine whether a user query_engine should be updated."""
        if specs.user_id not in self.per_user_cache.query_engine:
            return True

        if self.per_user_cache.specs[specs.user_id] != specs:
            return True

        if self.per_user_cache.llm_settings[specs.user_id] != llm_settings:
            return True

        for collection in specs.collections:
            if not self.collections.up_to_date[collection]["retriever"]:
                return True

        return False

    def _set_up_llm(
        self, user_id: str, llm_settings: LlamaLLMChatSettings
    ) -> Anyscale | OpenAI:
        """Set up the LLM model for the response generation."""
        if (
            user_id in self.per_user_cache.llm
            and llm_settings == self.per_user_cache.llm_settings[user_id]
        ):
            return self.per_user_cache.llm[user_id]

        if llm_settings.model not in self.list_supported_models():
            raise LLMSetupError(
                f"Model {llm_settings.model} is not supported.",
            )
        if llm_settings.model in ANYSCALE_MODELS:
            llm_provider = OpenAILikeProvider(_env_prefix="anyscale_")
            provider_class = Anyscale
        else:
            llm_provider = OpenAILikeProvider(_env_prefix="openai_")
            provider_class = OpenAI

        return provider_class(
            api_key=llm_provider.api_key,
            api_base=llm_provider.base_url,
            **llm_settings.model_dump(),
        )
