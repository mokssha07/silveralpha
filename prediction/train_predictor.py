import json
import pickle
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


SNAP = Path("data/snapshots")
TRAINING_PATH = SNAP / "training_dataset.json"
MEM_PATH = SNAP / "prediction_memory.json"
TRUST_PATH = SNAP / "regime_trust.json"
FEATURE_PATH = SNAP / "regime_features_neutral.json"
MODEL_PATH = SNAP / "predictor_model.pkl"
METRICS_PATH = SNAP / "predictor_metrics.json"

FEATURES = [
    "market_pressure_index",
    "num_narratives",
    "max_cluster_pressure",
    "mean_cluster_pressure",
    "bullish_share",
    "bearish_share",
    "mean_confidence",
]

MIN_SAMPLES = 8


def load_json(path, default):
    if not path.exists():
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def vector(row):
    return [float(row.get(name, 0.0)) for name in FEATURES]


def signal_trust():
    return load_json(TRUST_PATH, {"signal_trust": 0.5}).get("signal_trust", 0.5)


def latest_feature_row():
    features = load_json(FEATURE_PATH, {})
    return {
        "market_pressure_index": features.get("market_pressure_index", 0.0),
        "num_narratives": features.get("num_narratives", 0),
        "max_cluster_pressure": features.get("max_cluster_pressure", 0.0),
        "mean_cluster_pressure": features.get("mean_cluster_pressure", 0.0),
        "bullish_share": features.get("bullish_share", 0.0),
        "bearish_share": features.get("bearish_share", 0.0),
        "mean_confidence": features.get("mean_confidence", 0.5),
    }


def training_examples():
    payload = load_json(TRAINING_PATH, {"examples": []})
    examples = [
        row for row in payload.get("examples", [])
        if "label" in row and all(name in row for name in FEATURES[:3])
    ]
    return examples


def legacy_memory_examples():
    memory = load_json(MEM_PATH, [])
    examples = []
    for row in memory:
        if "label" not in row:
            continue
        if all(name in row for name in ("market_pressure_index", "num_narratives", "max_cluster_pressure", "mean_confidence")):
            examples.append({
                "market_pressure_index": row["market_pressure_index"],
                "num_narratives": row["num_narratives"],
                "max_cluster_pressure": row["max_cluster_pressure"],
                "mean_cluster_pressure": row.get("mean_cluster_pressure", 0.0),
                "bullish_share": row.get("bullish_share", 0.0),
                "bearish_share": row.get("bearish_share", 0.0),
                "mean_confidence": row["mean_confidence"],
                "label": row["label"],
            })
    return examples


def fit_model(examples):
    X = np.array([vector(row) for row in examples], dtype=float)
    y = np.array([int(row["label"]) for row in examples], dtype=int)

    model = Pipeline([
        ("scale", StandardScaler()),
        ("clf", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)),
    ])
    model.fit(X, y)

    proba = model.predict_proba(X)[:, 1]
    preds = (proba >= 0.5).astype(int)
    metrics = {
        "num_examples": int(len(examples)),
        "positive_rate": round(float(y.mean()), 4),
        "train_accuracy": round(float(accuracy_score(y, preds)), 4),
        "brier_score": round(float(brier_score_loss(y, proba)), 4),
        "features": FEATURES,
    }
    if len(set(y)) == 2:
        metrics["roc_auc"] = round(float(roc_auc_score(y, proba)), 4)

    return model, metrics


def calibrated_probability(raw_proba, trust):
    adjusted = 0.5 + (raw_proba - 0.5) * trust
    return round(float(max(0.01, min(0.99, adjusted))), 3)


def main():
    examples = training_examples() or legacy_memory_examples()
    labels = [row.get("label") for row in examples]
    trust = signal_trust()

    latest = latest_feature_row()

    if len(examples) >= MIN_SAMPLES and len(set(labels)) >= 2:
        model, metrics = fit_model(examples)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(model, f)

        raw_proba = model.predict_proba(np.array([vector(latest)], dtype=float))[0][1]
        predicted_proba = calibrated_probability(raw_proba, trust)
        metrics["prediction_source"] = "trained_model"
        metrics["raw_latest_proba"] = round(float(raw_proba), 3)
        metrics["adjusted_latest_proba"] = predicted_proba
        json.dump(metrics, open(METRICS_PATH, "w", encoding="utf-8"), indent=2)
    else:
        if MODEL_PATH.exists():
            MODEL_PATH.unlink()
        pressure = abs(latest["market_pressure_index"])
        narrative_bonus = min(latest["num_narratives"], 10) / 20
        raw_proba = 0.35 + min(pressure, 1.0) * 0.25 + narrative_bonus
        predicted_proba = calibrated_probability(raw_proba, trust)
        json.dump({
            "num_examples": len(examples),
            "prediction_source": "deterministic_fallback",
            "reason": "need at least 8 labeled examples across both classes",
            "adjusted_latest_proba": predicted_proba,
            "features": FEATURES,
        }, open(METRICS_PATH, "w", encoding="utf-8"), indent=2)

    memory = load_json(MEM_PATH, [])
    latest_record = {
        **latest,
        "predicted_proba": predicted_proba,
        "signal_trust": trust,
    }
    if memory and "label" not in memory[-1]:
        memory[-1] = latest_record
    else:
        memory.append(latest_record)
    json.dump(memory, open(MEM_PATH, "w", encoding="utf-8"), indent=2)

    print(f"Predicted probability of meaningful move: {predicted_proba}")


if __name__ == "__main__":
    main()
