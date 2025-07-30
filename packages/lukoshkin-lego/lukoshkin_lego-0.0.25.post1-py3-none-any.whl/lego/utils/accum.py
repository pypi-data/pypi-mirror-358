from collections.abc import Container
from typing import Any, Literal


class ValueAccum:
    """Accumulates values, merging containers (lists and dictionaries)."""

    def __init__(
        self,
        omit_empty: bool = True,
        collect_dicts_via: Literal["update", "append_in_list"] = "update",
    ):
        """
        Initializes the accumulator.

        Args:
        :param omit_empty: If True, empty values or `None`s are not added
        """
        if collect_dicts_via not in ["update", "append_in_list"]:
            raise ValueError(
                "Unsupported method for combining dictionaries: "
                f"{collect_dicts_via}"
            )
        self.omit_empty = omit_empty
        self.collect_dicts_via = collect_dicts_via
        self._acc: dict[str, Any] = {}

    def is_container(self, val: object) -> bool:
        """Check if a value is a container (excluding strings)."""
        return isinstance(val, Container) and not isinstance(val, str)

    def _merge_list(self, key: str, new_val: object):
        """Merge a value into an existing list."""
        if self.is_container(new_val):
            self._acc[key].extend(new_val)
        else:
            self._acc[key].append(new_val)

    def _merge_dict(self, key: str, new_val: object):
        """Merge a value into an existing dictionary."""
        if self.is_container(new_val):
            if self.collect_dicts_via == "append_in_list":
                if isinstance(self._acc[key], list):
                    self._acc[key].append(new_val)
                else:
                    self._acc[key] = [self._acc[key], new_val]
            else:
                self._acc[key].update(new_val)
        else:
            raise ValueError(f"Key {key} expects a dictionary, got {new_val}")

    def add(self, chunk: dict) -> None:
        """Add a chunk of data to the accumulator."""
        for key, val in chunk.items():
            target = self._acc.get(key)
            if self.omit_empty and not str(val):
                continue

            match target:
                case None:
                    self._acc[key] = val
                case list():
                    self._merge_list(key, val)
                case dict():
                    self._merge_dict(key, val)
                case _:
                    if self.is_container(target):
                        raise ValueError(
                            f"Unsupported container: {type(target)}"
                        )
                    self._acc[key] = [target, val]

    def __call__(self):
        """Returns the accumulated data."""
        return self._acc
