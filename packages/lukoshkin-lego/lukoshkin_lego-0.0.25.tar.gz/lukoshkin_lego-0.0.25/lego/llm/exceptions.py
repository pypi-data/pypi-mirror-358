"""Custom exceptions used in the llm package."""


class RouterExhaustedRetries(Exception):
    """Router exceeded all available retry options and attempts."""
