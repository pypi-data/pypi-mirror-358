"""Multi-part-transfer router."""

from pathlib import Path
from urllib.parse import unquote

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from lego.utils.multi_part_transfer import (
    select_shard,
    split_file_into_compressed_chunks,
)

router = APIRouter(tags=["multi-part-transfer"])


@router.post("/compress_and_split")
async def compress_and_split(
    file_path: str, chunk_size: int = 1024 * 1024
) -> str:
    """
    Compress and split a file into chunks of a given size.

    Returns a path to the directory containing the compressed chunks.
    """
    if not Path(file_path).is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return split_file_into_compressed_chunks(file_path, chunk_size)


@router.get("/download_shard/{shards_dir:path}/{chunk_num}")
async def download_shard(shards_dir: str, chunk_num: int):
    """Download a resource shard number `chunk_num` stored on the server."""

    shard_path, shard_name = select_shard(unquote(shards_dir), chunk_num)
    if not shard_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        shard_path,
        media_type="application/octet-stream",
        filename=shard_name,
    )
