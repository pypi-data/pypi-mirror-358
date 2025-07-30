"""Parser for scripts with S3DataHandler CLI."""

from argparse import ArgumentParser


def cli_parser(
    desc: str | None = None,
    default_bucket_name: str | None = None,
    default_extensions: list[str] | None = None,
) -> ArgumentParser:
    """Create a parser for the S3DataHandler CLI."""
    parser = ArgumentParser(description=desc)
    parser.add_argument(
        "-b",
        "--bucket",
        type=str,
        default=default_bucket_name,
        help="Name of the S3 bucket to download the files from",
    )
    parser.add_argument(
        "-e",
        "--extensions",
        type=str,
        nargs="+",
        default=default_extensions,
        help="List of target extensions to download",
    )
    return parser
