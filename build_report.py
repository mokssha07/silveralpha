import json
from pathlib import Path
from datetime import datetime, timezone

snap = Path("data/snapshots")


def load_latest(pattern, default):
    files = sorted(snap.glob(pattern))
    if not files:
        return default
    timestamped = [path for path in files if not path.stem.endswith("_latest")]
    if timestamped:
        files = timestamped
    latest = max(files, key=lambda path: path.stat().st_mtime)
    return json.load(open(latest))


def pressure_for(cluster):
    return cluster.get("final_pressure", cluster.get("pressure", 0.0))


def direction_for(pressure):
    if pressure > 0:
        return "up"
    if pressure < 0:
        return "down"
    return "neutral"


def build_narratives(market):
    cluster_files = sorted(snap.glob("clusters_*.json"), key=lambda path: path.stat().st_mtime)
    if not cluster_files:
        return []

    clusters = json.load(open(cluster_files[-1]))
    market_by_cluster = {
        c.get("cluster_id"): c
        for c in market.get("clusters", [])
    }
    narratives = []

    for cluster in clusters:
        market_cluster = market_by_cluster.get(cluster.get("cluster_id"), {})
        pressure = pressure_for(market_cluster) or pressure_for(cluster)
        docs = cluster.get("documents", [])
        sources = sorted({d.get("source", "Unknown") for d in docs if d.get("source")})
        sample_text = docs[0].get("text", "") if docs else cluster.get("narrative", "")
        narrative = cluster.get("narrative") or sample_text[:90].strip()
        if not narrative:
            continue

        narratives.append({
            "cluster_id": cluster.get("cluster_id"),
            "narrative": narrative,
            "size": cluster.get("size", len(docs)),
            "stability": cluster.get("stability", 0.0),
            "pressure": pressure,
            "direction": direction_for(pressure),
            "sources": sources,
            "source_count": len(sources),
            "locations": cluster.get("locations", []),
            "time_series": [{"time": 0, "value": cluster.get("size", len(docs))}],
        })

    return narratives


market = load_latest(
    "market_index_*.json",
    {"market_pressure_index": 0.0, "clusters": []}
)

report = {
    "market": market,
    "confidence": load_latest(
        "confidence_adj_*.json",
        {"confidence": 0.5}
    ),
    "regime": load_latest(
        "regime.json",
        {"regime": "quiet"}
    ),
    "signal_trust": load_latest(
        "regime_trust.json",
        {"signal_trust": 0.5}
    ),
    "conflict": load_latest(
        "narrative_conflict.json",
        {"conflict": False}
    ),
    "multi_horizon": load_latest(
        "multi_horizon.json",
        {"short_term": 0.0, "medium_term": 0.0, "long_term": 0.0}
    ),
    "action_state": load_latest(
        "action_state.json",
        {"action": "WATCH", "predicted_proba": 0.5}
    ),
    "predictor": load_latest(
        "predictor_metrics.json",
        {"prediction_source": "untrained"}
    ),
    "narratives": build_narratives(market),
    "timestamp": datetime.now(timezone.utc).isoformat()
}

out_path = snap / "final_report.json"
json.dump(report, open(out_path, "w"), indent=2)

print("Final report generated")
