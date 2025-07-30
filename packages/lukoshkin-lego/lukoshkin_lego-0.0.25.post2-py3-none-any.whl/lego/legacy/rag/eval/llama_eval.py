"""Evaluation of the RAG pipeline."""

from pathlib import Path

import openai
from llama_index.core import Document
from llama_index.core.evaluation import BatchEvalRunner, CorrectnessEvaluator
from llama_index.core.evaluation.base import EvaluationResult
from llama_index.core.llama_dataset import LabelledRagDataset
from llama_index.core.llama_dataset.generator import RagDatasetGenerator
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.llms.anyscale import Anyscale
from llama_index.llms.openai import OpenAI

from lego.llm.settings import OpenAILikeProvider
from lego.logger import logger
from lego.utils.io import read_articles


def llama_documents_from_datapath(datapath: str | Path) -> list[Document]:
    """Read articles and create `llama_index` documents from them."""
    return [
        Document(
            text=article["body"],
            metadata={"uri": article["uri"], "url": article.get("url")},
        )
        for article in read_articles(datapath)
    ]


async def generate_dataset(
    documents: list[Document],
    llm: OpenAI | Anyscale | None = None,
    cache_at: str | Path | None = None,
    num_questions_per_chunk: int = 1,
    num_workers: int = 8,
) -> LabelledRagDataset:
    """
    Generate QA dataset from the provided documents.

    `num_questions_per_chunk` is the number of question-answer pairs
    to generate per each 512 char chunk of the provided documents.
    """
    if cache_at and Path(cache_at).is_file():
        logger.info(f"Loading the dataset from '{cache_at}'.")
        return LabelledRagDataset.from_json(cache_at)

    openai_provider = OpenAILikeProvider(_env_prefix="openai_")
    openai.api_key = openai_provider.api_key

    dataset_generator = RagDatasetGenerator.from_documents(
        documents,
        llm=llm or OpenAI(temperature=0),
        num_questions_per_chunk=num_questions_per_chunk,
        # show_progress=True,
        workers=num_workers,
    )
    qas = await dataset_generator.agenerate_dataset_from_nodes()

    if cache_at:
        Path(cache_at).parent.mkdir(parents=True, exist_ok=True)
        qas.save_json(cache_at)

    return qas


async def evaluate_on_dataset(
    query_engine: RetrieverQueryEngine,
    documents: list[Document],
    llm: OpenAI | Anyscale | None = None,
    cache_at: str | Path | None = None,
    num_workers: int = 8,
) -> dict[str, list[EvaluationResult]]:
    """Evaluate RAG pipeline on the provided dataset."""
    qas = await generate_dataset(
        documents, llm, cache_at, num_workers=num_workers
    )
    return await BatchEvalRunner(
        {
            "correctness": CorrectnessEvaluator(
                llm=llm or OpenAI(temperature=0)
            )
        },
        workers=num_workers,
    ).aevaluate_queries(
        query_engine,
        queries=[ex.query for ex in qas.examples],
        reference=[ex.reference_answer for ex in qas.examples],
    )
