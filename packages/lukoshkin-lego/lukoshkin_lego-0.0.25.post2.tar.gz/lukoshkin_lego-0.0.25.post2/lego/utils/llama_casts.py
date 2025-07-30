"""Cast JSON article or Article model to LlamaIndex Document."""

from llama_index.core import Document

from lego.lego_types import JSONDict
from lego.rag.models import Article


def document_from_json_article(article: JSONDict) -> Document:
    """Create a Document instance from a json article."""
    ## TODO: read key names from 'lego/rag/params.yaml'
    return Document(
        text=article["body"],
        metadata={"uri": article["uri"], "url": article.get("url")},
    )


def document_from_article(article: Article) -> Document:
    """Convert json articles to Article instances."""
    return Document(text=article.text, metadata=article.metadata)


def cast_to_document(doc: JSONDict | Article | Document) -> Document:
    """Cast an article to a Document instance."""
    if isinstance(doc, Document):
        return doc
    if isinstance(doc, Article):
        return document_from_article(doc)
    return document_from_json_article(doc)
