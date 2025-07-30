"""Utils for `rag.core.ingest` module."""

from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from llama_index.core.node_parser import (
    HierarchicalNodeParser,
    LangchainNodeParser,
    SentenceWindowNodeParser,
)
from pymilvus import Collection, utility

from lego.logger import logger
from lego.rag.exceptions import InconsistentSetupConfig
from lego.rag.models import (
    CollectionModel,
    HierarchicalSplitter,
    RecursiveCharSplitter,
    SentenceWindowSplitter,
)


def recurisve_char_splitter_couterpart(*args, **kwargs) -> LangchainNodeParser:
    """Return Llama compatible recursive char text splitter from langchain."""
    return LangchainNodeParser(RecursiveCharacterTextSplitter(*args, **kwargs))


MODEL_TO_LLAMA_PARSER = {
    SentenceWindowSplitter: SentenceWindowNodeParser,
    RecursiveCharSplitter: recurisve_char_splitter_couterpart,
    HierarchicalSplitter: HierarchicalNodeParser.from_defaults,
}


def get_emb_size(collection_name: str, embedding_field: str) -> int:
    """
    Get the embedding size of a PyMilvus collection.

    Inspect the collection schema to find the size of the embedding field.
    If there is no such field (embedding field named differently), or the
    collection was not populated by any data, then returns 0.
    """
    if not utility.has_collection(collection_name):
        return 0

    collection = Collection(collection_name)
    if collection.num_entities == 0:
        return 0

    for field in collection.schema.fields:
        if field.name == embedding_field:
            return field.params["dim"]

    return 0


def maybe_mend_index(setup: CollectionModel, embedding_field: str):
    """
    Create a new index if LlamaIndex failed to create an appropriate one.

    LlamaIndex is buggy (at least at the time of reporting it): it may drop
    some "deep" fields in the param config due to shallow copying. It may also
    not be able to create an index if it was dropped externally.
    """
    if not utility.has_collection(setup.name):
        logger.error("Wrong use of the function")
        return

    collection = Collection(setup.name)
    index_param_to_set = setup.setup_config.index_param.serialize()

    if (
        collection.has_index()
        and index_param_to_set == collection.index().params
    ):
        return

    if collection.has_index():
        if collection.num_entities == 0:
            logger.info("Dropping index")
            collection.release()
            collection.drop_index()
        else:
            logger.error("Implementation uncovered case")
            raise InconsistentSetupConfig("Index param is inconsistent.")

    ## Let's NOT rely on `MilvusVectorStore._create_index_if_required`.
    collection.create_index(embedding_field, index_params=index_param_to_set)
