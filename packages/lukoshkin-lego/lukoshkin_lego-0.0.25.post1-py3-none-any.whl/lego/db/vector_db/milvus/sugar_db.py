"""
Enhanced Milvus database adapter module.

This module provides a more powerful adapter for Milvus database operations,
extending the functionality of the basic MilvusDBConnector. It includes
utilities for managing collections and partitions, handling TTL settings,
and parsing specialized drop string formats for batch operations.

The main class, MilvusDB, offers a higher-level interface for working with
Milvus collections, including methods for checking build status, ensuring
collections are properly built, and dropping collections or partitions.
"""

from collections import defaultdict
import traceback

from pydantic import BaseModel
from pymilvus import CollectionSchema, MilvusClient

from lego.db.vector_db.embed.openai_model import OpenAIEmbedModel
from lego.db.vector_db.milvus import MilvusDBConnector
from lego.db.vector_db.models import MilvusDBSettings
from lego.lego_types import OneOrMany
from lego.logger import logger
from lego.settings import MilvusConnection
from lego.utils.ttl import ExpireTime


class DropStringFormat(BaseModel):
    """The parsed drop string format."""

    collections: list[str]
    partitions: dict[str, list[str]]


class IrrelevantCollectionError(ValueError):
    """Raised when trying to connect to an irrelevant collection."""


class MilvusDB:
    """A more powerful adapter than MilvusDBConnector."""

    primary_key = "id"
    embedding_field = "vector"
    dynamic_fields: list[str] = []
    metric_type = "IP"

    def __init__(
        self,
        collection_name: str,
        collection_ttl: int | str | None = None,
        schema: CollectionSchema | None = None,
    ) -> None:
        """
        Initialize the MilvusDB instance.

        Args:
        :param collection_name: Name of the collection.
        :param collection_ttl: Time to live for the collection. If provided
            - as an integer, it is treated as seconds.
            - as a string (1s, 1m, 1h) ─ parsed using ExpireTime to seconds.
            - as None, the collection will not expire.
        :param schema: CollectionSchema object. If not provided, it will be
            fetched from the database by the collection name.
        """
        self.collection_ttl = ExpireTime.parse(collection_ttl)
        if "," in collection_name or ";" in collection_name:
            raise ValueError("Collection name cannot contain ',' or ';'")
        self._is_built: dict[str, bool] = {}
        connection = MilvusConnection()
        if schema is None:
            schema = MilvusDBConnector.get_schema(collection_name, connection)

        self.all_fields_but_embedding: list[str] = self.dynamic_fields.copy()
        embed_dim = None
        for field in schema.fields:
            if field.name == self.embedding_field:
                embed_dim = field.dim
                continue

            self.all_fields_but_embedding.append(field.name)

        if embed_dim is None:
            raise IrrelevantCollectionError(
                "Trying to connect to irrelevant collection."
            )
        try:
            self.db = MilvusDBConnector(
                connection=connection,
                settings=self.settings(collection_name, self.collection_ttl),
                embed_model=OpenAIEmbedModel(embed_dim=embed_dim),
                schema=schema,
                use_guards_for_text=True,
                get_embeddings_from_primary_keys=True,
            )
        except Exception as exc:
            logger.error(f"Failed to initialize MilvusDBConnector: {exc}")
            logger.debug(traceback.format_exc())

    def is_built(self, partition: str) -> bool:
        """Check if the connector is built and ready."""
        return self._is_built.get(partition, False)

    def try_to_build_if_not_built(self, partition: str = "_default") -> None:
        """Ensure the connector is built and ready."""
        if not self.is_built(partition):
            try:
                self.db.ensure_built(partition)
                self._is_built[partition] = True
            except Exception as exc:
                logger.error(f"Failed to build partition {partition}: {exc}")
                logger.debug(traceback.format_exc())

    @classmethod
    def settings(
        cls,
        collection_name: str,
        collection_ttl: int | str | None = None,
    ) -> MilvusDBSettings:
        """Get the settings object for the Milvus DB."""
        return MilvusDBSettings(
            collection=collection_name,
            primary_key=cls.primary_key,
            embedding_field=cls.embedding_field,
            search_params={"metric_type": cls.metric_type},
            properties={
                "collection.ttl.seconds": ExpireTime.parse(collection_ttl)
            },
        )

    @classmethod
    def drop_collections_or_partitions(
        cls,
        collections: OneOrMany[str] | None = None,
        partition_dict: dict[str, list[str]] | None = None,
    ) -> dict[str, DropStringFormat]:
        """Drop partitions or entire collection from the Milvus DB."""
        partition_dict = (partition_dict or {}).copy()
        if isinstance(collections, str):
            collections = [collections]

        collections = collections or []
        requested = DropStringFormat(
            collections=collections, partitions=partition_dict
        )
        client = MilvusClient(**MilvusConnection().model_dump())
        dropped_partitions: dict[str, list[str]] = {}
        dropped_collections: list[str] = []

        for name in collections:
            if not client.has_collection(collection_name=name):
                logger.info(f"Collection {name} does not exist.")
                continue

            logger.info(f"Dropping collection {name}.")
            client.drop_collection(collection_name=name)
            dropped_collections.append(name)
            if partition_dict.pop(name, None):
                logger.error("Incorrectly parsed 'drop_string'")

        for col, partitions in partition_dict.items():
            if client.has_collection(collection_name=col):
                dropped_partitions[col] = []
                partitions = [
                    pt
                    for pt in partitions
                    if client.has_partition(
                        collection_name=col, partition_name=pt
                    )
                ]
            else:
                logger.info(f"Collection {col} does not exist.")
                continue

            if partitions:
                client.release_partitions(
                    collection_name=col, partition_names=partitions
                )
            for pt in partitions:
                logger.info(f"Dropping partition {pt} from {col}.")
                client.drop_partition(collection_name=col, partition_name=pt)
                dropped_partitions[col].append(pt)
        client.close()
        return {
            "requested": requested,
            "dropped": {
                "collections": dropped_collections,
                "partitions": dropped_partitions,
            },
        }

    @classmethod
    def drop_using_drop_string(
        cls, drop_string: str
    ) -> dict[str, DropStringFormat]:
        """
        Drop collections or partitions using the "drop" string.

        The "drop" string should in the comma-colon-semicolon format:
            "c1:p1,p2,p3;c2;c3:p2"
        This will result in dropping:
        - p1, p2, p3 partitions from collection c1
        - collection c2 as a whole
        - only p2 partition from collection c3
        """
        collection_list = []
        partition_dict = defaultdict(list)
        for collection in drop_string.split(";"):
            if ":" not in collection.strip(":"):
                collection_list.append(collection)
                continue

            collection, partitions = collection.split(":")
            for partition in partitions.split(","):
                partition_dict[collection].append(partition)

        return cls.drop_collections_or_partitions(
            collections=collection_list, partition_dict=partition_dict
        )
