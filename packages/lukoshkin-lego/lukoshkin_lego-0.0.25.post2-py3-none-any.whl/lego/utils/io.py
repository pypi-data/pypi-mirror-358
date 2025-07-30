"""I/O operations."""

import json
from pathlib import Path

from lego.constants import JSON_INDENT
from lego.lego_types import JSONDict, OneOrMany


def read_json(path: str | Path) -> JSONDict:
    """Read a json file."""
    with open(path, encoding="utf-8") as fd:
        return json.load(fd)


def _read_jsons_in_dir(
    folder: str | Path, recursive_search: bool = False
) -> list[JSONDict]:
    """Read json files found in a `folder`."""
    articles = []
    for file_path in json_files(folder, recursive_search):
        parsed = read_json(file_path)
        if isinstance(parsed, list):
            articles.extend(parsed)
        else:
            articles.append(parsed)
    return articles


def read_jsons(path: str | Path) -> list[JSONDict]:
    """
    Read either a JSON or many JSONs in a folder.

    Supported formats:
    - a json file with an article given as a dict
    - a json file with a list of articles (batched)
    - directory of json articles
    - directory of jsons with batched articles.
    """
    path = Path(path)

    if path.is_file():
        py_obj = read_json(path)
        return py_obj if isinstance(py_obj, list) else [py_obj]

    if path.is_dir():
        return _read_jsons_in_dir(path)

    raise FileNotFoundError(f"Not found: {path}")


def json_files(
    folder: str | Path, recursive_search: bool = False
) -> list[Path]:
    """Form a list of json files in a `folder`."""
    folder = Path(folder)
    file_gen = (
        folder.rglob("*.json") if recursive_search else folder.glob("*.json")
    )
    return [path for path in file_gen if path.is_file()]


def write_jsons(
    path: str | Path | None = None, py_obj: OneOrMany[JSONDict] | None = None
) -> None:
    """
    Write json-like object to the filesystem.

    The function takes care of the folder creation.
    If path is given w/o ".json" extension and `py_obj` is a list with more
    than one article, then `path` will be treated as a directory and each
    article will be written to a separate file.
    """
    ## If nothing or nowhere to write, quit early and silently.
    if not path or not py_obj:
        return

    path = Path(path)
    ## Treat as a directory path if `path` is with ".json" extension
    ## and there is more than one article in `py_obj`.
    if path.suffix != ".json" and isinstance(py_obj, list):
        path.mkdir(parents=True, exist_ok=True)
        for article in py_obj:
            name = path / f"{article['uri']}.json"
            ## fh - file handler, fd - file descriptor. We use fh here
            ## only to suppress flake8 warning about block variables overlap.
            with open(name, "w", encoding="utf-8") as fh:
                json.dump(article, fh, indent=JSON_INDENT, ensure_ascii=False)
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path.with_suffix(".json"), "w", encoding="utf-8") as fd:
        json.dump(py_obj, fd, indent=JSON_INDENT, ensure_ascii=False)
