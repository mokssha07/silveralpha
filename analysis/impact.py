import json
from pathlib import Path
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

snap_dir = Path("data/snapshots")
analyzer = SentimentIntensityAnalyzer()

# Market signal keywords (bullish/bearish)
bullish_terms = [
    "shortage", "deficit", "supply crunch", "mine shutdown",
    "demand surge", "solar", "expansion", "tight supply",
    "bullish", "upside", "growth", "strong demand"
]

bearish_terms = [
    "oversupply", "demand collapse", "liquidation",
    "rate hike", "strong dollar", "substitution",
    "bearish", "downside", "recession", "weakness"
]

# FinBERT model for financial sentiment (with fallback to VADER)
try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch
    
    finbert_model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
    finbert_tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
    use_finbert = True
except Exception as e:
    print(f"FinBERT not available ({e}), falling back to VADER only")
    use_finbert = False


def get_vader_sentiment(text):
    """Get VADER sentiment score (-1 to 1)."""
    if not text:
        return 0.0
    return analyzer.polarity_scores(text)["compound"]


def get_finbert_sentiment(text):
    """Get FinBERT sentiment: -1 (negative), 0 (neutral), 1 (positive)."""
    if not use_finbert or not text:
        return 0.0
    
    try:
        inputs = finbert_tokenizer(text[:512], return_tensors="pt", truncation=True)
        with torch.no_grad():
            logits = finbert_model(**inputs).logits
        
        # FinBERT output: [negative, neutral, positive]
        probs = torch.softmax(logits, dim=1)[0]
        neg, neu, pos = probs.cpu().numpy()
        
        # Convert to -1 to 1 scale
        sentiment = float(pos - neg)
        return sentiment
    except Exception:
        return 0.0


def get_sentiment_and_confidence(text):
    """
    Get sentiment score and confidence.
    Uses FinBERT for financial domain, with VADER fallback.
    
    Returns: (sentiment: -1 to 1, confidence: 0 to 1)
    """
    if not text or len(text.strip()) < 10:
        return 0.0, 0.3
    
    if use_finbert:
        sentiment = get_finbert_sentiment(text)
        # FinBERT is more reliable for financial text
        confidence = 0.8
    else:
        sentiment = get_vader_sentiment(text)
        confidence = 0.7
    
    # Boost confidence if market keywords present
    text_lower = text.lower()
    keyword_score = 0
    for term in bullish_terms:
        if term in text_lower:
            keyword_score += 0.1
    for term in bearish_terms:
        if term in text_lower:
            keyword_score -= 0.1
    
    # Combine with keyword signal
    if abs(keyword_score) > 0.2:
        confidence = min(1.0, confidence + 0.1)
        sentiment = (sentiment + keyword_score) / 2
    else:
        market_score = keyword_score
        sentiment = (sentiment * 0.7) + (market_score * 0.3)
    
    return sentiment, confidence


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
        texts = [d.get("text", "") for d in c.get("documents", []) if d.get("text")]
        if not texts and c.get("narrative"):
            texts = [c["narrative"]]
        if not texts:
            continue

        # Compute average sentiment and confidence
        sentiments = []
        confidences = []
        for t in texts:
            sent, conf = get_sentiment_and_confidence(t)
            sentiments.append(sent)
            confidences.append(conf)
        
        avg_sentiment = np.mean(sentiments) if sentiments else 0.0
        avg_confidence = np.mean(confidences) if confidences else 0.5
        sentiment_volatility = np.std(sentiments) if len(sentiments) > 1 else 0.0
        
        # A1: Source diversity weighting
        # Multiple independent sources = higher confidence
        sources = sorted({d.get("source") for d in c.get("documents", []) if d.get("source")})
        source_count = len(sources)
        source_diversity_boost = {
            1: 1.0,
            2: 1.15,
            3: 1.35,
            4: 1.65,
            5: 2.0
        }.get(source_count, 2.0)
        
        avg_confidence = min(1.0, avg_confidence * source_diversity_boost)
        
        # Impact combines sentiment direction and confidence
        impact = avg_sentiment * avg_confidence
        
        # Higher volatility = lower reliability
        reliability_adjustment = max(0.5, 1.0 - sentiment_volatility)
        impact = impact * reliability_adjustment

        output.append({
            "cluster_id": c["cluster_id"],
            "size": c["size"],
            "stability": c["stability"],
            "impact_score": round(float(impact), 3),
            "direction": "up" if impact > 0 else "down" if impact < 0 else "neutral",
            "sentiment": round(avg_sentiment, 3),
            "sentiment_confidence": round(avg_confidence, 3),
            "sentiment_volatility": round(sentiment_volatility, 3)
        })

    out_file = path.name.replace("clusters", "impact")

    with open(snap_dir / out_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("Impact analysis complete (FinBERT enabled)" if use_finbert else "Impact analysis complete (VADER only)")
