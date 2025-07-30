"""Data ingestion router (with a dummy retrieval) for the RAG pipeline."""

from fastapi import APIRouter, HTTPException, status

from lego.rag.container import container
from lego.rag.exceptions import (
    CollectionNotRegistered,
    InconsistentSetupConfig,
    UserAccessError,
)
from lego.rag.mock import CollectionSet
from lego.rag.models import Article, CollectionModel, UpdateConfig

router = APIRouter(tags=["ingest"])


@router.post("/collections/create", status_code=status.HTTP_201_CREATED)
def create_collection(collection: CollectionModel) -> CollectionModel:
    """Create indexes for the provided collection setup."""
    setup = container.resolve(CollectionSet)
    if collection.name in setup.collections:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Collection already exists",
        )
    try:
        setup.update_collection(collection.name, collection.setup_config)
    except UserAccessError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can't access collections created in another session.",
        ) from exc
    return setup.collections[collection.name]


@router.put("/collections/setup/{collection}")
def update_collection(collection: str, cfg: UpdateConfig) -> CollectionModel:
    """
    Set up collection.

    Specify the collection name, embedding model, node parser, index
    and search params that will be used for index creation.

    One can call multiple times to overwrite an existing collection setup.
    """
    setup = container.resolve(CollectionSet)
    if collection not in setup.collections:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
        )
    try:
        setup.update_collection(collection, cfg)
    except InconsistentSetupConfig as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Inconsistent embedding model",
        ) from exc
    return setup.collections[collection]


@router.get("/collections/list")
def list_collections() -> dict[str, list[str]]:
    """List all collections in the DB and those created by a user."""
    return container.resolve(CollectionSet).list_collections()


@router.delete("/collections/drop/{collection}")
def drop_collection(collection: str) -> str:
    """Drop a collection by name."""
    try:
        dropped = container.resolve(CollectionSet).drop_collection(collection)
        if not dropped:
            raise CollectionNotRegistered

        return dropped[0]
    except CollectionNotRegistered as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
        ) from exc


@router.post("/ingest/{collection}")
def ingest_documents(docs: list[Article], collection: str) -> list[str]:
    """
    Add data to the DB.

    URI will be added to the chunks metadata.
    """
    try:
        container.resolve(CollectionSet).ingest_documents(docs, collection)
    except CollectionNotRegistered as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
        ) from exc
    return [doc.uri for doc in docs]
