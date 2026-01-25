# Silver Alpha - Narrative-Driven Market Intelligence

## Overview

Silver Alpha is an unsupervised machine learning system that detects emerging market regimes through real-time narrative analysis from global news sources.

### Innovation

Unlike traditional price-prediction models, Silver Alpha:
- **Narrative-First Architecture**: Analyzes news semantics before price movements
- **Unsupervised Learning**: No labeled training data required
- **Multi-Horizon Analysis**: Short/Medium/Long-term signal decomposition
- **Regime Detection**: Identifies market states (Quiet/Building/Momentum/Trending)

---

## Technical Architecture

### Pipeline Flow
```
News Sources (RSS/Wayback)
    ↓
Text Cleaning & Normalization
    ↓
Semantic Embeddings (SentenceTransformer)
    ↓
Unsupervised Clustering (HDBSCAN)
    ↓
Narrative Impact Analysis
    ↓
Velocity Computation (temporal delta)
    ↓
Pressure Accumulation
    ↓
Market Index Aggregation
    ↓
Regime Classification
    ↓
Multi-Horizon Prediction
    ↓
Action State (BUY/SELL/WATCH)
```

### Core Technologies

- **ML Framework**: scikit-learn, HDBSCAN
- **NLP**: SentenceTransformers (all-MiniLM-L6-v2)
- **Backend**: Django REST Framework
- **Frontend**: React + Three.js + WebGL
- **Data Sources**: Internet Archive Wayback Machine, RSS feeds

---

## Key Features

### 1. Narrative Clustering
- Automatic topic detection from raw news
- Cluster stability tracking
- Source diversity analysis

### 2. Velocity & Pressure Metrics
- **Velocity**: Rate of narrative size change
- **Pressure**: Accumulated momentum with decay
- **Direction**: Bullish/Bearish/Neutral classification

### 3. Regime Classification
Adaptive thresholds detect:
- **Quiet**: Low market pressure (< 0.05)
- **Building**: Emerging pressure (0.05 - 0.15)
- **Momentum**: Active movement (0.15 - 0.3)
- **Trending**: Strong directional bias (> 0.3)

### 4. Multi-Horizon Signals
- **Short-term**: 1-3 day outlook
- **Medium-term**: 1-2 week outlook  
- **Long-term**: 2-4 week outlook

---

## Installation & Setup

### Prerequisites
```bash
Python 3.10+
pip install -r requirements.txt
```

### Quick Start

1. **Run ML Pipeline**
```bash
python run_pipeline.py
```

2. **Start Backend API**
```bash
cd silver_backend
python manage.py runserver
```

3. **Start Frontend** (separate terminal)
```bash
cd frontend
npm start
```

---

## API Endpoints

Base URL: `http://localhost:8000/api/`

- `GET /status/` - Health check
- `GET /globe/nodes/` - Intelligence nodes for globe visualization
- `GET /node/{id}/` - Detailed narrative analysis
- `GET /dashboard/summary/` - Market summary metrics
- `GET /dashboard/chart/` - Sentiment distribution

---

## Model Performance

### Training Data
- 6-month historical window
- ~45 snapshots (every 4th day)
- 30-60 articles per snapshot from Wayback Machine

### Output Metrics
- **Market Pressure Index**: -1.0 (bearish) to +1.0 (bullish)
- **Signal Trust**: 0.4 (quiet) to 0.85 (momentum)
- **Prediction Confidence**: Regime-adjusted probability

---

## Real-World Impact

### Use Cases
1. **Institutional Traders**: Early regime detection for position sizing
2. **Risk Management**: Narrative conflict identification
3. **Research Analysts**: Automated topic tracking across sources
4. **Retail Investors**: Simplified market sentiment dashboard

### Advantages Over Traditional Models
- No lag from price-only indicators
- Detects narrative shifts before price moves
- Source diversity prevents single-point manipulation
- Unsupervised = adapts to new market conditions

---

## Future Enhancements

- Real-time streaming data integration
- Cross-asset narrative correlation (Gold, Oil, USD)
- Sentiment intensity scoring (BERT fine-tuning)
- Historical backtesting with price validation
- Mobile app deployment

---

## Team

Silver Alpha Partners | 2026

---

## License

Proprietary - All Rights Reserved
