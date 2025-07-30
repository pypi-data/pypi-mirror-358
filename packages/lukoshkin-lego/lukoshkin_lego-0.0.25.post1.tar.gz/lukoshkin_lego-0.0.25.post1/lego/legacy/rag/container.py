"""A container for the RAG pipeline."""

from collections import defaultdict

from rodi import Container

from lego.rag import mock
from lego.rag.container_types import ProfilerSessions, UseProfiler
from lego.rag.core.ingest import CollectionSet
from lego.rag.core.retrieve import RAGQueryEngine
from lego.settings import MilvusConnection

container = Container()
container.register(UseProfiler, instance=True)
container.register(ProfilerSessions, instance=defaultdict(dict))
container.register(
    mock.CollectionSet, instance=CollectionSet(MilvusConnection())
)
container.register(
    mock.SourcedQueryEngine,
    instance=RAGQueryEngine(container.resolve(mock.CollectionSet)),
)
