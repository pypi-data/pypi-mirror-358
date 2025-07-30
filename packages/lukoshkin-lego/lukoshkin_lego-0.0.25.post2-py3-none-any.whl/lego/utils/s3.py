"""Utilities for downloading content from an S3 Bucket."""

import hashlib
from pathlib import Path
from typing import Generator, Protocol

from boto3.s3.transfer import TransferConfig
from boto3.session import Session

from lego.logger import logger
from lego.settings import S3Connection

FlatParamConfig: TypeAlias = dict[str, str | int | float | bool]


class ObjectSummary(Protocol):
    """Since I don't know whether there is a way to import it directly."""

    key: str
    e_tag: str

    ## Returning generics here kills the sense of using Protocol
    def get(self) -> dict:  # type: ignore[misc]
        """Get the object from the bucket."""


class S3DataHandler:
    """Base class for S3 Data Handlers."""

    def __init__(self, bucket_name: str, settings: S3Connection):
        self.bucket = (
            Session(
                aws_access_key_id=settings.access_key,
                aws_secret_access_key=settings.secret_key,
            )
            .resource("s3")
            .Bucket(bucket_name)
        )

    def filter(
        self,
        prefix: str | Path | None = None,
        extensions: list[str] | None = None,
    ) -> Generator[ObjectSummary, None, None]:
        """Filter files in the bucket by prefix and extensions."""
        for obj in (
            self.bucket.objects.filter(Prefix=prefix)
            if prefix
            else self.bucket.objects.all()
        ):
            if not obj.key.endswith("/"):
                if not extensions or Path(obj.key).suffix in extensions:
                    yield obj


class S3DataInspector(S3DataHandler):
    """S3 Bucket content inspector."""

    def find(
        self,
        substring: str,
        prefix: str | Path | None = None,
        extensions: list[str] | None = None,
    ) -> Generator[ObjectSummary, None, None]:
        """Find files in the bucket containing a substring."""
        for obj in self.filter(prefix, extensions):
            if substring in obj.key:
                yield obj

    def inspect(self, obj: ObjectSummary, encoding: str = "utf-8"):
        """Inspect files in the bucket."""
        return obj.get()["Body"].read().decode(encoding=encoding)


class S3DataRetriever(S3DataHandler):
    """S3 Bucket content retriever."""

    md5_chunk_size: int = 2**20

    def __init__(
        self,
        bucket_name: str,
        settings: S3Connection,
        save_prefix: str | Path,
        config: TransferConfig | FlatParamConfig | None = None,
    ):
        super().__init__(bucket_name, settings)
        self.save_prefix = save_prefix
        self.config = (
            config
            if isinstance(config, TransferConfig)
            else TransferConfig(**(config or {}))
        )

    def fetch(
        self,
        download_prefix: str | None = None,
        strip_prefix: str | None = None,
        extension_filters: list[str] | None = None,
        dry_run: bool = False,
    ):
        """
        Download files from S3 bucket.

        :param download_prefix: Prefix to filter files.
        :param strip_prefix: Prefix to strip from the remote path when saving.
        :param extension_filters: List of extensions to filter files.
        """
        save_prefix = Path(self.save_prefix)
        for obj in self.filter(download_prefix, extension_filters):
            remote_path = Path(obj.key)
            remote_e_tag = obj.e_tag.strip('"')
            local_path = self._maybe_strip_prefix(remote_path, strip_prefix)
            local_path = save_prefix / local_path
            if local_path.exists() and remote_e_tag == self.md5sum(local_path):
                self._debug_log(f"Skipping {local_path}", dry_run)
                continue

            self._download_file(obj.key, local_path, dry_run)

    @classmethod
    def md5sum(cls, local_path: Path) -> str:
        """Compute md5 sum of a local file by chunks."""
        md5 = hashlib.md5(usedforsecurity=False)
        with open(local_path, "rb") as fd:
            for chunk in iter(lambda: fd.read(cls.md5_chunk_size), b""):
                md5.update(chunk)
        return md5.hexdigest()

    def _maybe_strip_prefix(
        self, path: Path, strip_prefix: str | None
    ) -> Path:
        """Strip path prefix if `strip_prefix` is set."""
        return path.relative_to(strip_prefix) if strip_prefix else path

    def _debug_log(self, msg: str, dry_run: bool):
        """Log a message when in the dry-run mode."""
        if dry_run:
            logger.debug(msg)

    def _download_file(
        self, remote_path: str, local_path: Path, dry_run: bool
    ):
        """Download a single file from the bucket."""
        if dry_run:
            print(local_path)
            return

        local_path.parent.mkdir(parents=True, exist_ok=True)
        self.bucket.download_file(remote_path, local_path, Config=self.config)
