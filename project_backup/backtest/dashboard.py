import json
from pathlib import Path

snap = Path("data/snapshots")
mem_path = snap / "prediction_memory.json"

if not mem_path.exists():
    print("No prediction memory found")
    exit()

memory = json.load(open(mem_path))

records = [r for r in memory if "label" in r]

if not records:
    print("No labeled records to backtest")
    exit()

def bucket_confidence(p):
    if p < 0.5:
        return "low"
    if p < 0.65:
        return "medium"
    return "high"


rows = []
for r in records:
    rows.append({
        "action": r.get("action", "WATCH"),
        "label": r["label"],
        "confidence": bucket_confidence(r.get("predicted_proba", 0.5)),
        "regime": r.get("regime", "unknown"),
    })

stats = {
    "ACT": {"correct": 0, "total": 0},
    "IGNORE": {"correct": 0, "total": 0},
    "WATCH": {"correct": 0, "total": 0},
}

for r in rows:
    action = r["action"]
    label = r["label"]

    if action not in stats:
        continue

    stats[action]["total"] += 1

    if action == "ACT" and label == 1:
        stats[action]["correct"] += 1
    elif action == "IGNORE" and label == 0:
        stats[action]["correct"] += 1

conf_stats = {
    "low": {"correct": 0, "total": 0},
    "medium": {"correct": 0, "total": 0},
    "high": {"correct": 0, "total": 0},
}

for r in rows:
    c = r["confidence"]
    a = r["action"]
    l = r["label"]

    conf_stats[c]["total"] += 1

    if a == "ACT" and l == 1:
        conf_stats[c]["correct"] += 1
    elif a == "IGNORE" and l == 0:
        conf_stats[c]["correct"] += 1

regime_stats = {}

for r in rows:
    reg = r["regime"]
    a = r["action"]
    l = r["label"]

    if reg not in regime_stats:
        regime_stats[reg] = {"correct": 0, "total": 0}

    regime_stats[reg]["total"] += 1

    if a == "ACT" and l == 1:
        regime_stats[reg]["correct"] += 1
    elif a == "IGNORE" and l == 0:
        regime_stats[reg]["correct"] += 1
def rate(block):
    if block["total"] == 0:
        return None
    return round(block["correct"] / block["total"], 3)


report = {
    "total_evaluated": len(rows),
    "action_accuracy": {
        k: {
            "accuracy": rate(v),
            "samples": v["total"]
        } for k, v in stats.items()
    },
    "confidence_accuracy": {
        k: {
            "accuracy": rate(v),
            "samples": v["total"]
        } for k, v in conf_stats.items()
    },
    "regime_accuracy": {
        k: {
            "accuracy": rate(v),
            "samples": v["total"]
        } for k, v in regime_stats.items()
    }
}

out = snap / "backtest_report.json"
json.dump(report, open(out, "w"), indent=2)
print("\n=== Backtest Summary ===")
print("Samples:", report["total_evaluated"])

print("\nAction Accuracy:")
for k, v in report["action_accuracy"].items():
    print(f"{k}: {v['accuracy']} ({v['samples']})")

print("\nConfidence Buckets:")
for k, v in report["confidence_accuracy"].items():
    print(f"{k}: {v['accuracy']} ({v['samples']})")

print("\nRegime Performance:")
for k, v in report["regime_accuracy"].items():
    print(f"{k}: {v['accuracy']} ({v['samples']})")
