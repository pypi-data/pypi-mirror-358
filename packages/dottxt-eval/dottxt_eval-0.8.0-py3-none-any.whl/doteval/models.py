import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Optional, Union

from doteval.metrics import Metric


@dataclass
class Sample:
    prompt: str
    scores: list["Score"]

    def __init__(self, prompt: str, scores: Union["Score", list["Score"]]):
        self.prompt = prompt
        if isinstance(scores, list):
            self.scores = scores
        else:
            self.scores = [scores]


@dataclass
class Score:
    name: str
    value: Any
    metrics: list[Metric]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationResult:
    """Results of a single evaluation step"""

    sample: Sample
    item_id: int
    dataset_row: dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


class EvaluationSummary:
    """Aggregated results of a full evaluation"""

    def __init__(self, results: list[EvaluationResult]):
        self.results = results
        self.summary = self.compute_summary()

    def compute_summary(self):
        summary = defaultdict(dict)

        # First pass: determine the expected score structure from successful results
        expected_scores = []
        for result in self.results:
            if result.error is None and result.sample.scores:
                expected_scores = [
                    (score.name, score.metrics) for score in result.sample.scores
                ]
                break

        # Regorganize the results by evaluator and metric
        aggregated_results = defaultdict(lambda: defaultdict(list))
        for result in self.results:
            if result.error is not None:
                # For error cases, add False values for each expected score
                for score_name, metrics in expected_scores:
                    for metric in metrics:
                        aggregated_results[score_name][metric].append(False)
            else:
                # For successful cases, use actual scores
                for score in result.sample.scores:
                    for metric in score.metrics:
                        aggregated_results[score.name][metric].append(score.value)

        for evaluator_name, metrics_values in aggregated_results.items():
            for metrics, values in metrics_values.items():
                summary[evaluator_name][metrics.__name__] = metrics(values)

        return summary
