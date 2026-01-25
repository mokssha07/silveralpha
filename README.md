Silver Alpha — Narrative Intelligence for Market Analysis
"The market moves on narratives. We made them measurable."

An AI system that reads the news so you don't have to.

---

Hackathon Details

- Event: Echelon 2.0cd
- Team Name: Team Phoenix
- Repository: Echelon2.0_TeamPhoenix
- Built: January 2026

---

What This Product Does

Most trading systems react to price movements — by then, the opportunity is gone.

Silver Alpha works one layer earlier.

It continuously reads hundreds of financial news articles, detects emerging narratives, tracks how fast they grow, and converts narrative momentum into actionable market signals — often days before price reacts.

Think of it as a 24×7 research analyst that:
- Reads everything
- Ignores noise
- Surfaces only what actually matters

---

How It Works (Plain English)

End-to-End Pipeline

1. Collect News
   Articles from Reuters, Financial Times, Mining.com, Yahoo Finance, and historical archives

2. Clean & Normalize
   Removes boilerplate, ads, duplicates, formatting noise

3. Semantic Encoding
   Each article → numerical vector using sentence embeddings

4. Unsupervised Clustering
   Similar stories grouped into narratives (no labels, no bias)

5. Narrative Dynamics
   - Velocity: how fast mentions grow
   - Stability: persistence vs volatility
   - Source Diversity: independent confirmation

6. Pressure Calculation
   Multiple aligned narratives = compounding pressure

7. Regime Classification
   - Quiet
   - Building
   - Momentum
   - Trending

8. Signal Generation
   - WATCH → neutral
   - BUY → bullish pressure
   - SELL → bearish pressure

No black magic. Just applied ML on what people are actually talking about.

---

Visual Intelligence (Frontend)

- Interactive 3D globe
- Green nodes → bullish narratives
- Red nodes → bearish narratives
- Click any node to see:
  - Narrative breakdown
  - Trust level
  - Indicators
  - Time-series evolution
  - Recommended action

Built for exploration, not spreadsheets.

---

Technical Stack

Machine Learning
- SentenceTransformers — semantic understanding
- HDBSCAN — unsupervised clustering
- Custom algorithms for:
  - Narrative velocity
  - Pressure accumulation
  - Regime detection

Backend
- Python
- Django REST Framework
- Stateless JSON APIs

Frontend
- React (Next.js)
- Three.js / WebGL
- Framer Motion for animations

Data
- Live RSS feeds
- Internet Archive (Wayback Machine)
- Stored snapshots for reproducibility

---

Repository Structure (Important)

```
silveralpha/
│
├── silver_backend/        # Django API
├── frontend/              # React + Three.js UI
├── analysis/              # Core ML logic
├── clustering/            # Narrative clustering
├── ingestion/             # News ingestion
├── prediction/            # Signal logic
├── preprocessing/         # Cleaning pipeline
├── example_data/          # Example input/output data
├── requirements.txt       # Python dependencies
└── README.md
```

---

Example Data (Included)

To make evaluation easy, we include example data:

```
example_data/
├── sample_articles.json
├── sample_clusters.json
├── sample_output.json
```

These files demonstrate:
- Input news articles
- Generated narratives
- Final signals & indicators

No external setup required to understand the flow.

---

Setup Instructions

1. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

2. Run the ML Pipeline

```bash
python run_pipeline.py
```

This:
- Ingests news
- Generates embeddings
- Clusters narratives
- Produces signals

3. Start Backend API

```bash
cd silver_backend
python manage.py runserver
```

API runs at:
```
http://127.0.0.1:8000/api/
```

4. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

UI available at:
```
http://localhost:3000
```

---

API Endpoints (JSON)

Health Check
```
GET /api/status/
```

Globe Nodes
```
GET /api/globe/nodes/
```

Narrative Detail
```
GET /api/node/{id}/
```

Dashboard Summary
```
GET /api/dashboard/summary/
```

---

Real-World Impact

Who this helps
- Traders → early signals
- Portfolio managers → narrative awareness
- Research teams → automated synthesis
- Anyone drowning in market news

Why it's different
- Not price-reactive
- Not keyword-based sentiment
- Fully unsupervised
- Narrative-first intelligence

---

What's Next
- Backtesting vs price action
- Multi-asset expansion
- Real-time streaming (WebSockets)
- Deeper NLP intensity scoring



