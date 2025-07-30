"""Query generation router with augmented retrieval."""

from fastapi import APIRouter, HTTPException, status

from lego.llm.settings import LlamaLLMChatSettings
from lego.rag.container import container
from lego.rag.exceptions import CollectionNotRegistered
from lego.rag.mock import CollectionSet, SourcedQueryEngine
from lego.rag.models import UserQuery, UserSpecs
from lego.rag.rag_types import TextualizedNodes

router = APIRouter(tags=["retrieve"])


@router.post("/index/retrieve")
def retrieve_documents(query: UserQuery, specs: UserSpecs) -> TextualizedNodes:
    """Retrieve from the DB chunks similar to the query."""
    return container.resolve(CollectionSet).retrieve(
        query.text,
        specs.collections,
        specs.similarity_retriever_top_k,
    )


@router.post("/index/rag_query")
async def rag(
    query: UserQuery,
    specs: UserSpecs,
    llm_settings: LlamaLLMChatSettings,
):
    """Retrieve relevant to a query chunks to generate a response with a LLM."""
    try:
        return await container.resolve(SourcedQueryEngine).aquery(
            query, specs, llm_settings
        )
    except CollectionNotRegistered as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
