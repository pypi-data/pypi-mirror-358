import os

import pytest
from pymilvus import CollectionSchema, DataType, FieldSchema, MilvusException

from lego.db.vector_db.embed.openai_model import OpenAIEmbedModel
from lego.db.vector_db.milvus import MilvusDBConnector
from lego.db.vector_db.models import MilvusDBSettings
from lego.settings import MilvusConnection

if os.getenv("MILVUS_URI") is None:
    os.environ["MILVUS_URI"] = "http://localhost:19530"

TEST_COLLECTION = "test_collection"
MAXLEN = 128
DIM = 512


def create_db_for_tests(pk_dtype: DataType, **kwargs):
    """Create a MilvusDBConnector instance for testing.

    The function gives a small control over the connector creation:
    - `pk_dtype`: The data type of the primary key field.
    - `kwargs`: Contains defaults of boolean flags used in the connector.
    """
    connection = MilvusConnection()
    settings = MilvusDBSettings(
        collection=TEST_COLLECTION,
        properties={
            "collection.ttl.seconds": kwargs.pop(
                "collection_ttl_seconds", None
            )
        },
    )
    schema = CollectionSchema(
        fields=[
            FieldSchema(
                name="id",
                dtype=pk_dtype,
                is_primary=True,
                max_length=MAXLEN,
            ),
            FieldSchema(name="sql", dtype=DataType.VARCHAR, max_length=MAXLEN),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=DIM),
        ]
    )
    return MilvusDBConnector(
        settings=settings,
        connection=connection,
        embed_model=OpenAIEmbedModel(embed_dim=DIM),
        schema=schema,
        **kwargs,
    )


@pytest.fixture(scope="module")
def db():
    return create_db_for_tests(DataType.VARCHAR)


@pytest.fixture(scope="module", autouse=True)
def setup(db):
    db.drop_collection()
    db.ensure_built()
    yield
    db.drop_partition()
    db.close()


@pytest.mark.order(1)
def test_register_one(db):
    """Test `register_one` method."""
    meta = {
        "id": "provide me the total sales",
        "sql": "SELECT SUM(sales) FROM sales",
    }
    item = meta.copy()
    item["vector"] = item["id"]
    assert db.count() == 0
    assert db.register_one(item)
    assert db.get(
        item["id"], output_fields=["id", "sql"], consistency_level="Session"
    ) == [meta]
    assert db.count() == 1
    assert db.register_one(item) is False
    assert db.count() == 1


@pytest.mark.order(2)
def test_register_many(db):
    """Test `register_many` method."""
    metas = [
        {
            "id": "provide me the total sales",
            "sql": "SELECT SUM(sales) FROM sales",
        },
        {
            "id": "show me the sales by region",
            "sql": "SELECT region, SUM(sales) FROM sales GROUP BY region",
        },
    ]
    items = [meta.copy() for meta in metas]
    ids = [item["id"] for item in metas]
    vecs = db.embed_model(ids)
    for item, vec in zip(items, vecs):
        item["vector"] = vec

    count = db.count()
    assert db.register_many(items) == 1
    assert (
        db.get(ids, output_fields=["id", "sql"], consistency_level="Session")
        == metas
    )
    assert db.count() == count + 1


@pytest.mark.order(3)
def test_register_many_synthetic_sugar(db):
    """Test `register_many`'s behavior when vectors are string or absent."""
    metas = [
        {
            "id": "who is my priority customer",
            "sql": (
                "SELECT customer_id FROM sales GROUP BY customer_id"
                " ORDER BY SUM(sales) DESC LIMIT 1"
            ),
        },
        {
            "id": "who visited my website",
            "sql": "SELECT DISTINCT user_id FROM website_visits",
        },
        {
            "id": "update my sales target",
            "sql": "UPDATE sales SET target = target * 1.1",
        },
    ]
    items = [meta.copy() for meta in metas]
    ids = [item["id"] for item in metas]
    items[0]["vector"] = db.embed_model(items[0]["id"])
    items[1]["vector"] = items[1]["id"]

    count = db.count()
    with pytest.raises(KeyError, match="vector"):
        db.register_many(items)

    assert db.register_many(items, get_embeddings_from_primary_keys=True) == 3
    assert sorted(
        db.get(
            ids,
            output_fields=["id", "sql"],
            consistency_level="Session",
        ),
        key=lambda x: x["id"],
    ) == sorted(metas, key=lambda x: x["id"])
    assert db.count() == count + 3


@pytest.mark.order(4)
def test_safe_guards_for_text(db):
    """Test the `use_guards_for_text` option in the connector.

    When the option is enabled, text symbols like single quote in primary
    key's values will be escaped to prevent parsing errors.
    """
    items = [
        {
            "id": "who'll be my next customer",
            "sql": (
                "SELECT customer_id FROM sales GROUP BY customer_id"
                " ORDER BY SUM(sales) DESC LIMIT 1"
            ),
        },
        {
            "id": """show me clients \ <-- invalid escape sequence
                    who've bought > 10 units""",
            "sql": "SELECT customer_id FROM sales WHERE units > 10",
        },
    ]
    with pytest.raises(MilvusException, match="cannot parse expression"):
        db.get(items[0]["id"], consistency_level="Session")

    with pytest.raises(MilvusException, match="cannot parse expression"):
        db.register_one(items[0])

    with pytest.raises(MilvusException, match="cannot parse expression"):
        db.register_many(items)

    db.register_one(
        {**items[0], "vector": items[0]["id"]},
        use_guards_for_text=True,
    )
    db.register_many(
        items,
        use_guards_for_text=True,
        get_embeddings_from_primary_keys=True,
    )

    ## Should not raise since adding the guards modifies the text in-place
    db.get(items[0]["id"], consistency_level="Session")

    ## With `use_guards_for_text=True` does not raise the error
    db.get(
        "who'll be my next customer",
        consistency_level="Session",
        use_guards_for_text=True,
    )


@pytest.mark.order(5)
def test_delete(db):
    """Test the `delete` method."""
    assert db.delete("who visited my website") == 1
    assert not db.get("who visited my website", consistency_level="Strong")

    ## Not sure whether it is a bug or feature:
    ## but deleting once again will always return 1
    # assert db.delete("who visited my website") == 1

    db.delete()
    assert db.count() == 0


@pytest.mark.order(6)
def test_search_consistency(db):
    """Test that search across the vector DB does actually work."""
    user_prompt = "The quick brown fox jumps over the lazy dog"
    items = [
        {
            "id": "A swift brown fox leaps over a sleepy dog",
            "sql": "1",
        },
        {
            "id": "The agile fox swiftly hops across a tired canine",
            "sql": "2",
        },
        {
            "id": "A small animal moves past a resting pet in a quick motion",
            "sql": "3",
        },
        {
            "id": "An energetic child races past a sleepy cat in the park",
            "sql": "4",
        },
    ]
    db.register_many(items, get_embeddings_from_primary_keys=True)
    similar = db.search(
        user_prompt,
        limit=4,
        output_fields=[],
        consistency_level="Strong",
    )
    similar = [(it["id"], it["distance"]) for it in similar[0]]
    similar = sorted(similar, key=lambda x: x[1])[::-1]
    assert list(zip(*similar))[0] == tuple(it["id"] for it in items)


@pytest.mark.order(7)
def test_different_options():
    """Test the constructor options and some methods default logic."""
    db = create_db_for_tests(DataType.INT64)
    db.drop_collection()
    db.ensure_built()
    items = [
        {
            "id": 1,
            "sql": "SELECT SUM(sales) FROM sales",
        },
        {
            "id": 2,
            "sql": "SELECT region, SUM(sales) FROM sales GROUP BY region",
        },
    ]
    ## Can't register without vectors since ints can't be used as embeddings
    with pytest.raises(KeyError, match="vector"):
        db.register_many(items, get_embeddings_from_primary_keys=True)

    for item in items:
        item["vector"] = item["sql"]

    ## Passing vectors as strings should be OK
    db.register_many(items)

    db = create_db_for_tests(
        DataType.VARCHAR, get_embeddings_from_primary_keys=True
    )
    db.drop_collection()
    db.ensure_built()
    items = [
        {
            "id": "who visited my website",
            "sql": "SELECT DISTINCT user_id FROM website_visits",
        },
        {
            "id": "update my sales target",
            "sql": "UPDATE sales SET target = target * 1.1",
        },
    ]
    ## Now it should be OK to pass w/o vectors
    db.register_many(items)

    db = create_db_for_tests(DataType.VARCHAR, use_guards_for_text=True)
    db.drop_collection()
    db.ensure_built()
    items = [
        {
            "id": "who'll be my next customer",
            "sql": "SELECT customer_id FROM sales GROUP BY customer_id",
            "vector": "who'll be my next customer",
        },
        {
            "id": "show me clients who've bought more than 10 units",
            "sql": "SELECT customer_id FROM sales WHERE units > 10",
            "vector": "show me clients who've bought more than 10 units",
        },
    ]
    ## Should not raise the parsing error
    db.register_one(items[0].copy())
    db.register_many(items)
    db.drop_collection()
    db.close()


@pytest.mark.order(8)
def test_partition_separation(db):
    """Verify that partitions are separated properly."""
    db.ensure_built("p1")
    db.ensure_built("p2")
    items = [
        {
            "id": "set my search path",
            "sql": "SET search_path TO p1;",
        },
        {
            "id": "update my sales target",
            "sql": "UPDATE sales SET target = target * 1.1",
        },
    ]
    db.register_many(
        items, partition="p1", get_embeddings_from_primary_keys=True
    )
    assert db.count("p1") == 2
    assert db.count("p2") == 0

    items = [
        {
            "id": "set my search path",
            "sql": "SET search_path TO p2;",
        },
        {
            "id": "who visited my website",
            "sql": "SELECT DISTINCT user_id FROM website_visits",
        },
    ]

    db.register_many(
        items, partition="p2", get_embeddings_from_primary_keys=True
    )
    assert db.count("p2") == 2
    assert db.count("p1") == 2

    res = db.get("set my search path", partitions="p1")
    assert res[0]["sql"] == "SET search_path TO p1;"

    res = db.get("set my search path", partitions="p2")
    assert res[0]["sql"] == "SET search_path TO p2;"

    db.delete("set my search path", partition="p1")
    res = db.get("set my search path", partitions="p2")
    assert res[0]["sql"] == "SET search_path TO p2;"
    assert db.count("p1") == 1
    assert db.count("p2") == 2

    db.drop_partition("p2")
    assert db.count("p1") == 1


@pytest.mark.order(9)
def test_init_without_schema(db):
    """Test the connector initialization without a schema."""
    connection = MilvusConnection()
    same_db = MilvusDBConnector(
        settings=db.settings,
        connection=connection,
        embed_model=db.embed_model,
    )
    assert same_db.get_schema(db.settings.collection, connection) == db.schema
    with pytest.raises(ValueError, match="does not exist"):
        MilvusDBConnector(
            settings=MilvusDBSettings(collection="non_existent"),
            connection=connection,
            embed_model=db.embed_model,
        )


@pytest.mark.order(10)
def test_collection_ttl():
    """Test the collection TTL option."""
    import time

    db = create_db_for_tests(DataType.VARCHAR, collection_ttl_seconds=2)
    db.drop_collection()
    db.ensure_built()
    items = [
        {
            "id": "who visited my website",
            "sql": "SELECT DISTINCT user_id FROM website_visits",
        },
        {
            "id": "update my sales target",
            "sql": "UPDATE sales SET target = target * 1.1",
        },
    ]
    db.register_many(items, get_embeddings_from_primary_keys=True)
    assert db.count() == 2

    db.flush()
    time.sleep(3)
    db.client.release_collection(db.settings.collection)
    db.client.load_collection(db.settings.collection)
    ## NOTE: flush + release + load is necessary to trigger the TTL

    assert db.count() == 0
    db.drop_collection()
