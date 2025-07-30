from dataclasses import dataclass


@dataclass
class ExpireTime:
    """Time constants and parsing for context expiration."""

    SECOND = 1
    MINUTE = 60
    HOUR = 3600
    DAY = 86400
    WEEK = 604800

    @classmethod
    def from_str(cls, time: str) -> int:
        """Convert a time string to seconds."""
        if time.isdigit():
            return int(time)

        if time[-1] not in {"w", "d", "h", "m", "s"}:
            raise ValueError(
                f"Invalid time format: {time}."
                " Must end with one of: w, d, h, m, s."
            )

        time = time.lower()
        num = int(time[:-1])

        if time.endswith("w"):
            return num * cls.WEEK
        if time.endswith("d"):
            return num * cls.DAY
        if time.endswith("h"):
            return num * cls.HOUR
        if time.endswith("m"):
            return num * cls.MINUTE
        if time.endswith("s"):
            return num * cls.SECOND

        raise ValueError(f"Invalid time format: {time}.")

    @classmethod
    def parse(cls, time: object) -> int | None:
        """Parse a time string or integer to seconds."""
        match time:
            case None:
                return None
            case str():
                return cls.from_str(time)
            case int():
                return time
            case _:
                raise ValueError(
                    f"Invalid time type: {type(time)}. "
                    "Must be an int or a string."
                )
