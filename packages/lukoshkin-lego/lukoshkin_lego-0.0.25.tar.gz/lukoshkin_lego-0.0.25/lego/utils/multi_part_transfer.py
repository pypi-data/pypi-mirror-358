"""Split a file into compressed chunks for lighter downloading from a server."""

import gzip
import hashlib
import uuid
from pathlib import Path

from lego.logger import logger
from lego.utils.io import write_jsons

CHECKSUMS_FILE = "checksums.json"


def split_file_into_compressed_chunks(
    fname: str, chunk_size: int = 1024 * 1024
) -> str:
    """Split a file into compressed chunks of a given size."""
    zip_path = compress_file(fname)

    fname = Path(fname)
    tmp_dir = fname.parent / f"tmp{uuid.uuid4()}-{fname.name}"
    tmp_dir.mkdir(parents=True)
    check_sums = {}

    chunk_num = 1
    with open(zip_path, "rb") as fd:
        while True:
            chunk = fd.read(chunk_size)
            if not chunk:
                break

            chunk_path = _shard_name(tmp_dir, chunk_num)
            with open(chunk_path, "wb") as chunk_fd:
                logger.debug(f"Saving chunk to {chunk_path}")
                chunk_fd.write(chunk)

            check_sums[chunk_num] = hashlib.md5(chunk).hexdigest()
            chunk_num += 1

    write_jsons(tmp_dir / CHECKSUMS_FILE, check_sums)
    output_dir = tmp_dir.rename(
        fname.parent / f"{fname.name}-split{chunk_num}"
    )
    Path(zip_path).unlink()
    return str(output_dir)


def select_shard(shards_dir: str, chunk_num: int) -> tuple[Path, str]:
    """Select a resource shard number `chunk_num` stored on the server."""
    shard_path = _shard_name(Path(shards_dir), chunk_num)
    return shard_path, shard_path.name


def compress_file(file_path: str):
    """Compress a file using gzip."""
    zip_path = f"{file_path}.gz"
    with (
        open(file_path, "rb") as fd_in,
        gzip.open(zip_path, "wb") as fd_out,
    ):
        fd_out.write(fd_in.read())
    return zip_path


def _shard_name(shards_dir: Path, chunk_num: int) -> Path:
    # ext = Path(str(shards_dir).rsplit("-split", 1)[0]).suffix
    # return shards_dir / f"shard-{chunk_num:04d}{ext}.gz"
    return shards_dir / f"shard-{chunk_num:04d}.gz"
