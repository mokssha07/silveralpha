import json
from pathlib import Path
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

snap_dir = Path("data/snapshots")
analyzer = SentimentIntensityAnalyzer()

bullish_terms = [
    "shortage", "deficit", "supply crunch", "mine shutdown",
    "demand surge", "solar", "expansion", "tight supply"
]

bearish_terms = [
    "oversupply", "demand collapse", "liquidation",
    "rate hike", "strong dollar", "substitution"
]


def market_score(text):
    score = 0
    t = text.lower()
    for w in bullish_terms:
        if w in t:
            score += 1
    for w in bearish_terms:
        if w in t:
            score -= 1
    return score


if __name__ == "__main__":
    files = sorted(snap_dir.glob("clusters_*.json"))
    if not files:
        print("No clusters found")
        exit()

    path = files[-1]

    with open(path, "r", encoding="utf-8") as f:
        clusters = json.load(f)

    output = []

    for c in clusters:
        texts = [d["text"] for d in c["documents"]]

        sentiment = sum(
            analyzer.polarity_scores(t)["compound"]
            for t in texts
        ) / len(texts)

        mscore = sum(market_score(t) for t in texts) / len(texts)

        impact = 0.6 * sentiment + 0.4 * mscore

        output.append({
            "cluster_id": c["cluster_id"],
            "size": c["size"],
            "stability": c["stability"],
            "impact_score": round(float(impact), 3),
            "direction": "Bullish" if impact > 0 else "Bearish"
        })

    out_file = path.name.replace("clusters", "impact")

    with open(snap_dir / out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("Impact analysis complete")
