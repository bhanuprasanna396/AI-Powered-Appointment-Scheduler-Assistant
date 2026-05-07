from typing import Iterable


def clamp_confidence(value: float) -> float:
    return max(0.0, min(1.0, round(value, 2)))


def average_confidence(scores: Iterable[float]) -> float:
    values = list(scores)
    if not values:
        return 0.0
    return clamp_confidence(sum(values) / len(values))
