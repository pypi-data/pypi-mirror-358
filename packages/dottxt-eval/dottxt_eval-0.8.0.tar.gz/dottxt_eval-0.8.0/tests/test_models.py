from doteval.metrics import accuracy
from doteval.models import EvaluationResult, EvaluationSummary, Sample, Score


def test_summary_empty_results():
    results = []
    summary = EvaluationSummary(results)
    assert isinstance(summary.summary, dict)
    assert len(summary.summary) == 0


def test_summary_simple():
    sample1 = Sample(prompt="test1", scores=[Score("match", True, [accuracy()])])
    sample2 = Sample(prompt="test2", scores=[Score("match", True, [accuracy()])])
    results = [
        EvaluationResult(sample1, 1),
        EvaluationResult(sample2, 2),
    ]
    summary = EvaluationSummary(results)
    assert isinstance(summary.summary, dict)
    assert summary.summary == {"match": {"accuracy": 1.0}}


def test_summary_two_scores_result():
    sample1 = Sample(
        prompt="test1",
        scores=[
            Score("match_1", True, [accuracy()]),
            Score("match_2", False, [accuracy()]),
        ],
    )
    sample2 = Sample(
        prompt="test2",
        scores=[
            Score("match_1", True, [accuracy()]),
            Score("match_2", False, [accuracy()]),
        ],
    )
    results = [
        EvaluationResult(sample1, 1),
        EvaluationResult(sample2, 2),
    ]
    summary = EvaluationSummary(results)
    assert isinstance(summary.summary, dict)
    assert summary.summary == {
        "match_1": {"accuracy": 1.0},
        "match_2": {"accuracy": 0.0},
    }
