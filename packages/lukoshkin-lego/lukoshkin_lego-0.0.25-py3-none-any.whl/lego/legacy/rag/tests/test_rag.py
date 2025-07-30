"""Tests for the RAG pipeline."""

import random
from pathlib import Path

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from lego.lego_types import JSONDict
from lego.rag.app import URL_PREFIX, app
from lego.rag.tests.throw_away_collection import (
    create_throw_away_collection,
    delete_collection,
)
from lego.utils.io import read_articles

client = TestClient(app)
TEST_COLLECTION1 = "_TEST_COLLECTION_"
TEST_COLLECTION2 = "_TEST2_COLLECTION_"
NON_EXISTING_COLLECTION = "_NON_EXISTING_COLLECTION_"
FORBIDDEN_COLLECTION = "_FORBIDDEN_COLLECTION_"
TEXT_SPLITTERS: dict[str, JSONDict] = {
    "window": {
        "window_size": 2,
        "original_text_metadata_key": "original_text",
        "window_metadata_key": "window",
    },
    "char_recursive": {"chunk_size": 512, "chunk_overlap": 64},
    "hierarchical": {"chunk_sizes": [128, 512, 2048], "chunk_overlap": 64},
}


@pytest.fixture(scope="session", autouse=True)
def setup_and_cleanup(request):
    """Set up everything for tests and clean up after them."""
    create_throw_away_collection(FORBIDDEN_COLLECTION)
    yield
    delete_collection(TEST_COLLECTION1)
    delete_collection(TEST_COLLECTION2)
    delete_collection(FORBIDDEN_COLLECTION)


def _random_setup_cfg() -> JSONDict:
    digits = random.sample(range(16, 100), 5)  # chunk_size cannot be < 16
    strings = [str(digit) for digit in random.sample(range(100, 1000), 4)]
    char_recursive = TEXT_SPLITTERS["char_recursive"].copy()
    char_recursive["chunk_size"] = digits[3]
    char_recursive["chunk_overlap"] = digits[4]
    return {
        "embed_model": {"name": strings[0], "dim": digits[0]},
        "index_param": {
            "index_type": strings[1],
            "metric_type": strings[2],
            "nlist": digits[1],
        },
        "search_param": {"metric_type": strings[3], "nprobe": digits[2]},
        "text_splitter": char_recursive,
    }


@pytest.mark.first
def test_create_collection():
    """
    Test a /create/ handle.

    Test it creates a correct collection and returns the conflict error
    when trying to create a collection that already exists.
    """
    json_dict = {
        "name": FORBIDDEN_COLLECTION,
        "setup_config": _random_setup_cfg(),
    }
    endpoint = f"{URL_PREFIX}/collections/create"
    response = client.post(endpoint, json=json_dict)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    json_dict["name"] = TEST_COLLECTION1
    response = client.post(endpoint, json=json_dict)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == json_dict

    response = client.post(endpoint, json=json_dict)
    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.second
def test_update_collection():
    """
    Test an /setup of an existing collection.

    Tests the following aspects:
        - it can do partial updates,
        - it can update the whole collection settings,
        - returns the "not found" error when trying to update a non-existing
          collection.
    """
    setup_config = _random_setup_cfg()
    json_dict = {"name": TEST_COLLECTION1, "setup_config": setup_config}
    base = f"{URL_PREFIX}/collections/setup"

    response = client.put(f"{base}/{TEST_COLLECTION1}", json=setup_config)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == json_dict

    new_setup_cfg = {"index_param": _random_setup_cfg()["index_param"]}
    response = client.put(f"{base}/{TEST_COLLECTION1}", json=new_setup_cfg)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "name": TEST_COLLECTION1,
        "setup_config": setup_config | new_setup_cfg,
    }
    response = client.put(f"{base}/{NON_EXISTING_COLLECTION}", json=json_dict)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.third
def test_drop_collection():
    """
    Test a /drop handle.

    Test cases:
        - dropping an existing collection (return status 200),
        - dropping a non-existing collection (return status 404).
    """
    endpoint = f"{URL_PREFIX}/collections/drop/{TEST_COLLECTION1}"

    response = client.delete(endpoint)
    assert response.status_code == status.HTTP_200_OK

    response = client.delete(endpoint)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.fourth
def test_ingest_collection():
    """
    Test an /ingest handle.

    Test cases:
        - ingest a collection (return status 200),
        - ingest a non-existing collection (return status 404).
    """
    base = f"{URL_PREFIX}/ingest"
    create_endpoint = f"{URL_PREFIX}/collections/create"
    collection_dict: dict[str, JSONDict] = {
        "name": TEST_COLLECTION1,
        "setup_config": {
            "embed_model": {"dim": 3072, "name": "text-embedding-3-large"},
            "index_param": {
                "index_type": "IVF_FLAT",
                "metric_type": "IP",
                "nlist": 1024,
            },
            "search_param": {"metric_type": "IP", "nprobe": 32},
            "text_splitter": TEXT_SPLITTERS["window"],
        },
    }
    client.post(create_endpoint, json=collection_dict)

    articles1 = read_articles(Path(__file__).parent / "john_doe1.json")
    response = client.post(f"{base}/{TEST_COLLECTION1}", json=articles1)
    assert response.status_code == status.HTTP_200_OK

    collection_dict["name"] = TEST_COLLECTION2
    collection_dict["setup_config"]["text_splitter"] = TEXT_SPLITTERS[
        "hierarchical"
    ]
    client.post(create_endpoint, json=collection_dict)

    articles2 = read_articles(Path(__file__).parent / "john_doe2.json")
    response = client.post(f"{base}/{TEST_COLLECTION2}", json=articles2)
    assert response.status_code == status.HTTP_200_OK

    response = client.post(f"{base}/{NON_EXISTING_COLLECTION}", json=articles1)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.fifth
def test_rag_query():
    """
    Test a /rag_query handle.

    Test cases:
        - query a collection (return status 200),
        - query a non-existing collection (return status 404).
    """
    endpoint = f"{URL_PREFIX}/index/rag_query"
    json_dict: dict[str, JSONDict] = {
        "query": {
            "text": "What does Elizabeth like to do? And who is John Doe?"
        },
        "specs": {
            "user_id": "0",
            "collections": [TEST_COLLECTION1, TEST_COLLECTION2],
            "similarity_retriever_top_k": 3,
            "similarity_fusion_top_k": 4,
        },
        "llm_settings": {
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "temperature": 0,
            "max_tokens": 3000,
        },
    }
    response = client.post(endpoint, json=json_dict)
    assert response.status_code == status.HTTP_200_OK

    json_dict["specs"].update({"collections": [NON_EXISTING_COLLECTION]})
    response = client.post(endpoint, json=json_dict)
    assert response.status_code == status.HTTP_404_NOT_FOUND
