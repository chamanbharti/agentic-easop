"""Tests for the support-intent baseline."""

import json
from pathlib import Path

import pytest

from easop.domain.support_category import SupportCategory
from easop.ml.intent_baseline import (
    evaluate_baselines,
    load_intent_dataset,
)

DATASET_PATH = Path(__file__).parents[2] / "data" / "intent" / "support_intents.jsonl"


def test_dataset_is_balanced_and_contains_expected_labels() -> None:
    examples = load_intent_dataset(DATASET_PATH)

    labels = [example.label for example in examples]

    assert len(examples) == 36
    assert set(labels) == {
        SupportCategory.GENERAL,
        SupportCategory.ORDER,
        SupportCategory.BILLING,
    }

    assert labels.count(SupportCategory.GENERAL) == 12
    assert labels.count(SupportCategory.ORDER) == 12
    assert labels.count(SupportCategory.BILLING) == 12


def test_dataset_does_not_contain_duplicate_text() -> None:
    examples = load_intent_dataset(DATASET_PATH)

    normalized_texts = {example.text.casefold() for example in examples}

    assert len(normalized_texts) == len(examples)


def test_evaluation_is_deterministic() -> None:
    examples = load_intent_dataset(DATASET_PATH)

    first = evaluate_baselines(examples)
    second = evaluate_baselines(examples)

    assert first == second


def test_evaluation_produces_valid_metrics() -> None:
    examples = load_intent_dataset(DATASET_PATH)

    evaluation = evaluate_baselines(examples)

    assert evaluation.dataset_size == 36
    assert evaluation.training_size == 27
    assert evaluation.test_size == 9

    assert 0.0 <= evaluation.dummy.accuracy <= 1.0
    assert 0.0 <= evaluation.dummy.macro_f1 <= 1.0
    assert 0.0 <= evaluation.logistic_regression.accuracy <= 1.0
    assert 0.0 <= evaluation.logistic_regression.macro_f1 <= 1.0


def test_loader_rejects_unknown_label(tmp_path: Path) -> None:
    dataset = tmp_path / "invalid.jsonl"
    dataset.write_text(
        json.dumps(
            {
                "text": "Please process my claim",
                "label": "claims",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="unknown label: claims",
    ):
        load_intent_dataset(dataset)


def test_loader_rejects_invalid_json(tmp_path: Path) -> None:
    dataset = tmp_path / "invalid.jsonl"
    dataset.write_text("{not-valid-json}", encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="Invalid JSON on dataset line 1",
    ):
        load_intent_dataset(dataset)
