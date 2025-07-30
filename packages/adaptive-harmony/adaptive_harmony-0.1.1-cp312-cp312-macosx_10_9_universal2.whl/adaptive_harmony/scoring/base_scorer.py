from abc import ABC, abstractmethod
from adaptive_harmony import StringThread
from typing import Any, Callable, Awaitable
from dataclasses import dataclass, field


@dataclass
class ScoreWithMetadata:
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


class Scorer(ABC):
    """
    BaseScorer to inherit from when building a scoring function.
    """

    @abstractmethod
    async def score(self, sample: StringThread) -> ScoreWithMetadata:
        """
        Score a single sample.
        Returns a single float score, with optional metadata.
        Metadata can be useful for evals when LLM reasoning regarding the score is available.
        """
        pass

    async def score_without_metadata(self, sample: StringThread) -> float:
        """
        Returns only the float score from .score
        """
        return (await self.score(sample)).score

    @classmethod
    def from_function(cls, async_fn: Callable[[StringThread], Awaitable[float]]) -> "Scorer":
        class FunctionScorer(cls):
            async def score(self, sample: StringThread) -> ScoreWithMetadata:
                result = await async_fn(sample)
                return ScoreWithMetadata(score=result, metadata={})

        return FunctionScorer()
