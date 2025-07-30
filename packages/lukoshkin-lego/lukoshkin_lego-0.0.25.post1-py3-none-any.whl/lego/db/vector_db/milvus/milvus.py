"""
MilvusDB connector

By default, connects to an existing collection with the _default or specified
partition or creates a new one.
"""

import re
from typing import Any, Literal

from loguru import logger
from pymilvus import Collection, CollectionSchema, MilvusClient, connections
from pymilvus.client.types import ExtraList
from pymilvus.exceptions import SchemaNotReadyException

from lego.db.vector_db.models import EmbedModel, MilvusDBSettings
from lego.lego_types import OneOrMany
from lego.settings import MilvusConnection


class MilvusDBConnector:
    """
    A Vector index that works with just one partition.

    If no partition specified, it will use the default partition.
    """

    register_consistency = "Session"
    partition_instruction = (
        " `ensure_built`, `register_one`, `register_many`, and `delete`"
        " methods accept 'partition'. While `get`, `query`, and `search`"
        " expect 'partitions'."
    )

    def __init__(
        self,
        connection: MilvusConnection,
        settings: MilvusDBSettings,
        embed_model: EmbedModel,
        schema: CollectionSchema | None = None,
        use_guards_for_text: bool = False,
        get_embeddings_from_primary_keys: bool = False,
    ):
        """
        Initialize the connector.

        :param schema: The collection schema with the fields and their types.
        :param settings: The settings for the MilvusDB (all basic information
            like collection name, primary key, embedding field, etc.).
        :param connection: The connection settings for the MilvusDB.
            (URI and optionally token).
        :param embed_model: The model to embed the text into vectors.
        :param use_guards_for_text: Whether to escape text symbols that
            may cause issues in the queries (like single quotes).
        :param get_embeddings_from_primary_keys: Whether to get the embeddings
            from primary keys the former are absent and the latter are strings.
        """
        self.client = MilvusClient(**connection.model_dump())
        self.connection = connection
        self.settings = settings
        self.embed_model = embed_model
        self.schema = schema

        if schema is None:
            self.schema = self.get_schema(settings.collection, connection)

        self._sanity_checks(self.schema, settings, embed_model)
        self._is_pk_str = self.schema.primary_field.dtype == 21  # VARCHAR

        self._use_guards_for_text = use_guards_for_text
        self._get_embs_from_pks = get_embeddings_from_primary_keys
        self._guard_re = re.compile(
            r"(?<!\\)[\n']|(?<!\\)\\(?!\S)", re.IGNORECASE
        )
        ## Likely, redundant settings since we have `radius` and `range_filter`
        # self.sim_threshold_to_add = settings.sim_threshold_to_add
        # self._more_similar_op = settings.more_similar_op

    @staticmethod
    def get_schema(
        collection_name: str, connection: MilvusConnection
    ) -> CollectionSchema:
        """Get the schema of the collection."""
        try:
            connections.connect(**connection.model_dump())
            return Collection(name=collection_name).schema
        except SchemaNotReadyException as exc:
            raise ValueError("The collection does not exist.") from exc

    @staticmethod
    def create_collection(
        client: MilvusClient,
        schema: CollectionSchema,
        settings: MilvusDBSettings,
    ):
        """Create the collection using the client, schema, and settings."""
        client.create_collection(
            schema=schema,
            collection_name=settings.collection,
            consistency_level=settings.consistency_level,
            properties=settings.properties,
        )

    def ensure_built(self, partition: str | None = None) -> None:
        """Build the collection, partition, and index."""
        partition = partition or self.settings.partition
        if not self.client.has_collection(self.settings.collection):
            self.create_collection(self.client, self.schema, self.settings)
        if not self.client.has_partition(
            collection_name=self.settings.collection,
            partition_name=partition,
        ):
            self.client.create_partition(
                collection_name=self.settings.collection,
                partition_name=partition,
            )
        if self.settings.properties:
            self.client.alter_collection_properties(
                collection_name=self.settings.collection,
                properties=self.settings.properties,
            )
        if self.settings.embedding_field not in self.client.list_indexes(
            self.settings.collection, self.settings.embedding_field
        ):
            index_params = self.client.prepare_index_params()
            index_params.add_index(
                self.settings.embedding_field,
                **self.settings.index_params,
            )
            self.client.create_index(
                self.settings.collection,
                index_params=index_params,
                sync=True,
            )
        return self.client.load_partitions(self.settings.collection, partition)

    def register_one(
        self,
        item: dict[str, Any],
        partition: str | None = None,
        use_guards_for_text: bool | None = None,
    ) -> bool:
        """
        Add an item to the collection.

        NOTE: empty string primary key is not allowed.
        """
        if use_guards_for_text is None:
            use_guards_for_text = self._use_guards_for_text

        if self._is_pk_str and use_guards_for_text:
            item[self.settings.primary_key] = self._add_guards_for_text(
                item[self.settings.primary_key]
            )
        if not self.get(
            ids=item[self.settings.primary_key],
            partitions=partition or self.settings.partition,
            output_fields=[self.settings.primary_key],
            consistency_level=self.register_consistency,
            use_guards_for_text=False,
        ):
            self.client.insert(
                collection_name=self.settings.collection,
                partition_name=partition or self.settings.partition,
                data=self._embed_string_vector_field(item),
            )
            return True
        return False

    def register_many(
        self,
        items: list[dict[str, Any]],
        partition: str | None = None,
        get_embeddings_from_primary_keys: bool | None = None,
        use_guards_for_text: bool | None = None,
    ) -> int:
        """
        Add multiple items to the collection.

        NOTE: empty string primary key is not allowed.
        safe_guard
        """
        if use_guards_for_text is None:
            use_guards_for_text = self._use_guards_for_text

        if self._is_pk_str and use_guards_for_text:
            for item in items:
                item[self.settings.primary_key] = self._add_guards_for_text(
                    item[self.settings.primary_key]
                )
        existing_ids = {
            d[self.settings.primary_key]
            for d in self.get(
                [item[self.settings.primary_key] for item in items],
                partitions=partition or self.settings.partition,
                output_fields=[self.settings.primary_key],
                consistency_level=self.register_consistency,
                use_guards_for_text=False,
            )
        }
        data = [
            item
            for item in items
            if item[self.settings.primary_key] not in existing_ids
        ]
        self.client.insert(
            collection_name=self.settings.collection,
            partition_name=partition or self.settings.partition,
            data=self._embed_string_vector_field(
                data, get_embeddings_from_primary_keys
            ),
        )
        return len(data)

    def get(
        self,
        ids: OneOrMany[str | int],
        partitions: OneOrMany[str] | None = None,
        use_guards_for_text: bool | None = None,
        **kwargs,
    ) -> ExtraList:
        """Get items by their IDs."""
        if kwargs.get("partition", None):
            raise ValueError(
                ".get() does not accept 'partition' as a keyword argument."
                " Did you mean 'partitions' instead?\n"
                f"{self.partition_instruction}"
            )
        if isinstance(partitions, str):
            partitions = [partitions]

        if use_guards_for_text is None:
            use_guards_for_text = self._use_guards_for_text

        if self._is_pk_str and use_guards_for_text:
            if isinstance(ids, (str, int)):
                ids = [ids]

            ids = [self._add_guards_for_text(id_) for id_ in ids]

        return self.client.get(
            collection_name=self.settings.collection,
            partition_names=partitions or [self.settings.partition],
            ids=ids,
            **kwargs,
        )

    def query(
        self,
        text_filter: tuple[str, str] | None = None,
        partitions: OneOrMany[str] | None = None,
        filter: str = "",
        **kwargs,
    ) -> ExtraList:
        """Query the partition."""
        if kwargs.get("partition", None):
            raise ValueError(
                ".query() does not accept 'partition' as a keyword argument."
                " Did you mean 'partitions' instead?"
                f"{self.partition_instruction}"
            )
        if isinstance(partitions, str):
            partitions = [partitions]

        prefix = ""
        if text_filter:
            key, value = text_filter
            safe_text = self._add_guards_for_text(value)
            prefix = f"{key} == '{safe_text}'"

        if prefix:
            filter = f"{prefix} && {filter}" if filter else prefix

        return self.client.query(
            collection_name=self.settings.collection,
            partition_names=partitions or [self.settings.partition],
            filter=filter,
            **kwargs,
        )

    def search(
        self,
        texts: OneOrMany[str],
        partitions: OneOrMany[str] | None = None,
        filter: str = "",
        limit: int = 10,
        **kwargs,
    ) -> ExtraList:
        """Search for similar items in the collection."""
        if kwargs.get("partition", None):
            raise ValueError(
                ".search() does not accept 'partition' as a keyword argument."
                " Did you mean 'partitions' instead?"
                f"{self.partition_instruction}"
            )
        if isinstance(partitions, str):
            partitions = [partitions]

        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return []

        if "" in texts:
            raise ValueError("Empty query text is not allowed.")

        return self.client.search(
            collection_name=self.settings.collection,
            partition_names=partitions or [self.settings.partition],
            data=self.embed_model(texts),
            filter=filter,
            limit=limit,
            anns_field=self.settings.embedding_field,
            search_params=kwargs.pop("search_params", {})
            or self.settings.search_params,
            **kwargs,
        )

    def delete(
        self,
        ids: OneOrMany[str | int] | None = None,
        partition: str | None = None,
        filter: str = "",  # may be better to make it `str | None = None`
        **kwargs,
    ) -> int:
        """
        Delete items by their IDs.

        NOTE: Deletes all items if no args are provided.
        NOTE: For some reason, deleting an item again will return 1.

        Returns the number of items deleted.
        """
        if kwargs.get("partitions", None):
            raise ValueError(
                ".delete() does not accept 'partitions' as a keyword argument."
                " Did you mean 'partition' instead?\n"
                f"{self.partition_instruction}"
            )
        if not ids and not filter:
            filter = f'{self.settings.primary_key} != ""'

        return self.client.delete(
            collection_name=self.settings.collection,
            partition_name=partition or self.settings.partition,
            ids=ids,
            filter=filter,
            **kwargs,
        ).get("delete_count", 0)

    def count(
        self,
        partition: str | None = None,
        consistency_level: (
            Literal["Session", "Strong", "Bounded", "Eventual"] | None
        ) = None,
    ) -> int:
        """
        Count the number of items in the collection.

        The consistency level is set to `register_consistency` by default.
        """
        return self.client.query(
            collection_name=self.settings.collection,
            partition_names=[partition or self.settings.partition],
            output_fields=["count(*)"],
            consistency_level=consistency_level or self.register_consistency,
        )[0]["count(*)"]

    def drop_collection(self, **kwargs) -> None:
        """Drop the collection."""
        if not self.client.has_collection(self.settings.collection):
            logger.warning(
                f"Collection '{self.settings.collection}' cannot be removed"
                ", since not found."
            )
            return
        self.client.release_collection(self.settings.collection, **kwargs)
        self.client.drop_collection(self.settings.collection)

    def drop_partition(
        self, partition: OneOrMany[str] | None = None, **kwargs
    ) -> None:
        """Drop the partition."""
        if kwargs.get("partition", None):
            raise ValueError(
                ".drop_partition() does not accept 'partitions' as a keyword"
                " argument. Did you mean 'partition' instead?\n"
                f"{self.partition_instruction}"
            )
        partition = partition or self.settings.partition
        if partition == "_default":
            logger.warning("Cannot drop the default partition.")
            logger.info("Dropping the collection instead.")
            self.drop_collection()
            return

        self.client.release_partitions(
            self.settings.collection,
            partition,
            **kwargs,
        )
        self.client.drop_partition(
            self.settings.collection,
            partition,
        )

    def flush(self, timeout: float | None = None) -> None:
        """
        Flush the added or deleted data.

        NOTE: it is redundant in almost all of the cases.
        """
        self.client.flush(
            collection_name=self.settings.collection, timeout=timeout
        )

    def close(self) -> None:
        """Close the connection."""
        self.client.close()

    @staticmethod
    def _sanity_checks(
        schema: CollectionSchema,
        settings: MilvusDBSettings,
        embed_model: EmbedModel,
    ) -> None:
        """Perform sanity checks on the settings and schema."""
        schema_dict = {f.name: f for f in schema.fields}
        if settings.embedding_field not in schema_dict:
            raise ValueError(
                f"Embedding field '{settings.embedding_field=}'"
                " not found in the schema."
            )
        if settings.primary_key not in {f.name for f in schema.fields}:
            raise ValueError(
                f"Primary key '{settings.primary_key=}'"
                " not found in the schema."
            )
        if schema_dict[settings.embedding_field].dim != embed_model.embed_dim:
            raise ValueError(
                f"Embedding field '{settings.embedding_field=}' dimension"
                f" mismatch: {schema_dict[settings.embedding_field].dim}"
                f" != {embed_model.embed_dim}."
            )

    def _embed_string_vector_field(
        self,
        items: OneOrMany[dict[str, Any]],
        get_embeddings_from_primary_keys: bool | None = None,
    ) -> list[dict[str, Any]]:
        """Embed the string vector field in the item."""
        if get_embeddings_from_primary_keys is None:
            get_embeddings_from_primary_keys = self._get_embs_from_pks

        pk = self.settings.primary_key
        ef = self.settings.embedding_field
        if isinstance(items, dict):
            items = [items]

        for item in items:
            if not str(item[pk]):
                raise ValueError(
                    f"Primary key '{pk}' must be a non-empty string.\n"
                    f"Received item: {item}"
                )
            if self._is_pk_str and get_embeddings_from_primary_keys:
                item[ef] = item[pk]

        vecs = {it[pk]: it[ef] for it in items if isinstance(it[ef], str)}
        if not vecs:
            return items

        logger.warning(
            "Note: some embeddings were passed as a string, and thus,"
            " will be converted automatically. In light of this,"
            " the order of items won't be preserved."
        )
        vecs = dict(zip(vecs.keys(), self.embed_model(vecs.values())))
        return [
            {**it, ef: vecs[it[pk]]} if it[pk] in vecs else it for it in items
        ]

    def _add_guards_for_text(self, text: str) -> str:
        """Escape the forbidden text symbols."""

        def escape_replacement(match_: re.Match) -> str:
            token = match_.group(0)
            match token:
                case "'":
                    return r"\'"
                case "\n":
                    return r"\n"
                case "\\":
                    return r"\\"
                case _:
                    raise ValueError(f"Unexpected token: {token}")

        return self._guard_re.sub(escape_replacement, text)
