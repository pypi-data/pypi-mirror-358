"""Miscellaneous endpoints for profiling and measuring performance."""

from fastapi import APIRouter, HTTPException, status

from lego.lego_types import ProfilerSessions
from lego.rag.container import container
from lego.rag.exceptions import CollectionNotRegistered
from lego.rag.mock import CollectionSet
from lego.rag.models import Article
from lego.utils.io import read_articles

router = APIRouter(tags=["misc"])


@router.get("/profile/stats")
def profile_stats():
    """Get the profile stats."""
    return container.resolve(ProfilerSessions)


@router.post("/fs_ingest/{collection}")
async def ingest_documents(datapath: str, collection: str) -> list[str]:
    """
    Add data to the DB from filesystem.

    URI and URL will be added to the chunks metadata.
    """
    try:
        articles = read_articles(datapath)
        articles = [{k: a[k] for k in Article.model_fields} for a in articles]

        return container.resolve(CollectionSet).ingest_documents(
            articles, collection
        )
    except CollectionNotRegistered as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found",
        ) from exc
