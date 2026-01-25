import json
from pathlib import Path
import numpy as np

snap = Path("data/snapshots")
mem_path = snap / "prediction_memory.json"

if not mem_path.exists():
    print("No memory available")
    exit()

memory = json.load(open(mem_path))

pairs = [
    (r["predicted_proba"], r["label"])
    for r in memory
    if "predicted_proba" in r and "label" in r
]

if len(pairs) < 10:
    print("Not enough data for calibration")
    exit()

probs, labels = zip(*pairs)

avg_pred = float(np.mean(probs))
avg_real = float(np.mean(labels))

scale = 1.0
if avg_pred > 0:
    scale = avg_real / avg_pred

out = {
    "scale": round(scale, 3),
    "avg_pred": round(avg_pred, 3),
    "avg_real": round(avg_real, 3)
}

json.dump(out, open(snap / "probability_calibration.json", "w"), indent=2)
print("Probability calibration updated")
