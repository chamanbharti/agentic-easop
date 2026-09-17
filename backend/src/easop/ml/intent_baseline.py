"""Train and evaluate the first support-intent classification baseline."""

import argparse
import json
from collections import Counter
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from easop.domain.support_category import SupportCategory

RANDOM_STATE = 42


@dataclass(frozen=True, slots=True)
class IntentExample:
    text: str
    label: SupportCategory


@dataclass(frozen=True, slots=True)
class ModelMetrics:
    accuracy: float
    macro_f1: float


@dataclass(frozen=True, slots=True)
class BaselineEvaluation:
    dataset_size: int
    training_size: int
    test_size: int
    class_counts: dict[str, int]
    dummy: ModelMetrics
    logistic_regression: ModelMetrics


def load_intent_dataset(path: Path) -> list[IntentExample]:
    """Load and validate a JSONL intent dataset."""

    examples: list[IntentExample] = []

    with path.open(encoding="utf-8") as dataset:
        for line_number, raw_line in enumerate(dataset, start=1):
            line = raw_line.strip()

            if not line:
                continue

            try:
                payload: Any = json.loads(line)
            except json.JSONDecodeError as exception:
                raise ValueError(
                    f"Invalid JSON on dataset line {line_number}"
                ) from exception

            if not isinstance(payload, dict):
                raise ValueError(f"Dataset line {line_number} must contain an object")

            text = payload.get("text")
            label = payload.get("label")

            if not isinstance(text, str) or not text.strip():
                raise ValueError(f"Dataset line {line_number} has invalid text")

            if not isinstance(label, str):
                raise ValueError(f"Dataset line {line_number} has invalid label")

            try:
                category = SupportCategory(label)
            except ValueError as exception:
                raise ValueError(
                    f"Dataset line {line_number} has unknown label: {label}"
                ) from exception

            examples.append(
                IntentExample(
                    text=text.strip(),
                    label=category,
                )
            )

    if not examples:
        raise ValueError("Intent dataset must not be empty")

    return examples


def calculate_metrics(
    expected: Sequence[str],
    predicted: Sequence[str],
) -> ModelMetrics:
    """Calculate deterministic classification metrics."""

    return ModelMetrics(
        accuracy=float(accuracy_score(expected, predicted)),
        macro_f1=float(
            f1_score(
                expected,
                predicted,
                average="macro",
                zero_division=0,
            )
        ),
    )


def evaluate_baselines(
    examples: Sequence[IntentExample],
) -> BaselineEvaluation:
    """Evaluate dummy and TF-IDF logistic-regression classifiers."""

    texts = [example.text for example in examples]
    labels = [example.label.value for example in examples]

    class_counts = Counter(labels)

    if len(class_counts) < 2:
        raise ValueError("At least two intent classes are required")

    if min(class_counts.values()) < 4:
        raise ValueError("Every intent class requires at least four examples")

    train_texts, test_texts, train_labels, test_labels = train_test_split(
        texts,
        labels,
        test_size=0.25,
        random_state=RANDOM_STATE,
        stratify=labels,
    )

    dummy = DummyClassifier(
        strategy="most_frequent",
        random_state=RANDOM_STATE,
    )
    dummy.fit(train_texts, train_labels)
    dummy_predictions = dummy.predict(test_texts)

    classifier = Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    ngram_range=(1, 2),
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )
    classifier.fit(train_texts, train_labels)
    classifier_predictions = classifier.predict(test_texts)

    return BaselineEvaluation(
        dataset_size=len(examples),
        training_size=len(train_texts),
        test_size=len(test_texts),
        class_counts=dict(sorted(class_counts.items())),
        dummy=calculate_metrics(
            test_labels,
            dummy_predictions.tolist(),
        ),
        logistic_regression=calculate_metrics(
            test_labels,
            classifier_predictions.tolist(),
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate the EASOP support-intent baseline"
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        required=True,
        help="Path to the support-intent JSONL dataset",
    )
    arguments = parser.parse_args()

    examples = load_intent_dataset(arguments.dataset)
    evaluation = evaluate_baselines(examples)

    print(json.dumps(asdict(evaluation), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
