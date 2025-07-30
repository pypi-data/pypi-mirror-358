"""Utility functions used at the evaluation stage."""


def raw_metrics(scores) -> dict[str, int | float]:
    """Compute raw metrics from a list of scores."""
    metrics = {
        "sum": sum(scr / 100 for scr in scores),
        "length": len(scores),
    }
    metrics["accuracy"] = metrics["sum"] / max(len(scores), 1)
    return metrics
