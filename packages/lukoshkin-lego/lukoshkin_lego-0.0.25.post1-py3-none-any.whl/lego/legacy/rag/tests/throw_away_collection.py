"""Create a throw away collection for testing purposes."""

from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    connections,
    utility,
)

from lego.settings import MilvusConnection

connection = MilvusConnection()
connections.connect(uri=connection.uri, token=connection.token)


def create_throw_away_collection(name: str):
    """Create a throw away collection for testing purposes."""
    Collection(
        name,
        schema=CollectionSchema(
            fields=[
                FieldSchema(
                    name="id",
                    dtype=DataType.VARCHAR,
                    is_primary=True,
                    max_length=100,
                ),
                FieldSchema(
                    name="embedding",
                    dtype=DataType.FLOAT_VECTOR,
                    dim=100,
                ),
            ]
        ),
    )


def delete_collection(name: str):
    """Delete a collection by name."""
    if utility.has_collection(name):
        utility.drop_collection(name)
