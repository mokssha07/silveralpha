# SilverAlpha Deep Audit Report

Date: June 3, 2026

## 1. Executive Diagnosis

SilverAlpha is a strong concept with a real product thesis:

> Markets do not move only because prices moved. Prices often move after information becomes a narrative, narratives become belief, and belief becomes positioning.

The repository already contains most of the right pieces: RSS ingestion, optional Reddit ingestion, historical Wayback ingestion, cleaning, embeddings, HDBSCAN clustering, semantic centroid matching, FinBERT impact analysis, lifecycle tracking, pressure calculation, regime classification, a prediction wrapper, Django APIs, and a cinematic Next.js/Three.js frontend.

The biggest problem is not a lack of ambition or even a lack of modules. The biggest problem is that the system can look complete while several parts are not yet logically trustworthy.

The critical weaknesses are:

1. Snapshot identity is not carried through the pipeline.
2. Cluster IDs are treated as stable narrative IDs, but HDBSCAN labels are not stable over time.
3. Lifecycle and pressure artifacts can be joined from different velocity sources.
4. New narratives often produce zero pressure because velocity is zero when there is no previous match.
5. Sentiment is still too close to generic positive/negative language, not true silver-market impact.
6. The training dataset currently has zero examples, so the predictor is not trained.
7. The frontend displays a synthetic chart while the backend report contains only one-point time series.
8. Several outputs use serious names like "multi-horizon", "trust", and "regime" while the underlying calculations are simple placeholders.

The project is best described as:

> A compelling demo-grade narrative intelligence prototype whose next phase should focus on temporal correctness, evidence quality, and honest signal validation.

## 2. Current Capability Scorecard

| Area | Current State | Confidence |
|---|---|---|
| Vision and product thesis | Strong and differentiated | High |
| Data ingestion | Works for RSS; weak source coverage and historical fidelity | Medium-low |
| Reddit/community layer | Implemented but inactive without credentials | Low |
| Cleaning and deduplication | Basic cleaning; no robust dedupe or relevance filtering | Low |
| Semantic representation | Good first model choice; no metadata/versioning | Medium |
| Unsupervised clustering | Works; parameters and fallback behavior need tuning | Medium |
| Narrative identity | Fragile; cluster IDs are unstable | Low |
| Evolution/lifecycle | Present but currently inconsistent | Low |
| Sentiment | FinBERT enabled, but market-impact mapping is incomplete | Medium-low |
| Pressure score | Interpretable but overly velocity-dependent | Low-medium |
| Regime classification | Simple threshold placeholder | Low |
| Prediction | Deterministic fallback; no trained model currently | Low |
| Backend API | Functional for demo; refresh behavior risky | Medium |
| Frontend | Visually strong; analytical truthfulness needs work | Medium |
| Testing/validation | Shape validation only; no correctness tests | Low |
| Documentation | Inspiring but overclaims current capability | Medium-low |

## 3. P0 Critical Flaws

These must be fixed before SilverAlpha can honestly claim to track evolving narratives.

### P0.1 Snapshot Identity Is Not Explicit

Evidence:

- `run_pipeline.py` launches each step without passing a snapshot ID after ingestion.
- `preprocessing/clean.py` chooses the latest raw snapshot by modification time.
- `embeddings/embed.py` chooses the lexicographically latest clean snapshot.
- `clustering/cluster.py` chooses the latest embedding and latest clean snapshot independently.
- `analysis/velocity.py` chooses the last two cluster files by filename sort.
- `build_report.py` chooses most artifacts by modification time.

Why this is dangerous:

The pipeline can mix raw data, embeddings, clusters, impact, velocity, pressure, and report files from different timestamps. This is fatal for a system whose core value is time-based narrative evolution.

Concrete example:

`run_pipeline.py 2024-01-15` can produce a historical raw snapshot, but downstream modules may still pick a newer clean snapshot or cluster file because they independently guess "latest".

Fix:

Create a shared `snapshot_id` resolver:

```text
snapshot_id = 2026-06-03_13-15
raw = data/raw/rss_snapshot_{snapshot_id}.json
clean = data/snapshots/clean_snapshot_{snapshot_id}.json
embeddings = data/snapshots/embeddings_{snapshot_id}.npy
clusters = data/snapshots/clusters_{snapshot_id}.json
impact = data/snapshots/impact_{snapshot_id}.json
velocity = data/snapshots/velocity_{snapshot_id}.json
pressure = data/snapshots/final_pressure_{snapshot_id}.json
market = data/snapshots/market_index_{snapshot_id}.json
```

Every module should accept `--snapshot-id`. No analysis step should guess "latest" except a final CLI wrapper or API resolver.

Acceptance criteria:

- Running a historical date never reads a newer snapshot.
- Every output artifact includes `snapshot_id`.
- `final_report.json` includes a `source_artifacts` block listing all exact files used.
- A health check fails if source artifacts are from mixed snapshot IDs.

### P0.2 Lifecycle Uses `velocity_latest.json` Instead of the Current Timestamped Velocity

Evidence:

`analysis/narrative_lifecycle.py` uses:

```python
files = sorted(snap_dir.glob("velocity_*.json"))
return json.load(open(files[-1]))
```

Because `velocity_latest.json` sorts after timestamped files, lifecycle can read `velocity_latest.json`. In the current artifacts, `velocity_latest.json` contains synthetic/simple values:

```json
[
  {"cluster_id": 0, "velocity": -1.9},
  {"cluster_id": 1, "velocity": -1.4},
  {"cluster_id": 2, "velocity": 1.0}
]
```

But the current timestamped `velocity_2026-06-03_13-15.json` contains six clusters with velocity zero and impact scores.

Why this is dangerous:

Lifecycle state and final pressure are joined from different velocity sources. That makes state labels like `growth` or `fade` unreliable.

Fix:

- Ignore `_latest` files unless explicitly requested.
- Use `--snapshot-id`.
- Delete or quarantine generated demo files like `velocity_latest.json`, `final_pressure_latest.json`, and `market_index_latest.json` from the active analytical path.

Acceptance criteria:

- `narrative_lifecycle.json` uses the same snapshot ID as the velocity file used by `final_pressure.py`.
- Lifecycle `current_size` equals the size from the matching velocity row.

### P0.3 Cluster IDs Are Not Narrative IDs

Evidence:

The system stores and matches lifecycle by `cluster_id`. HDBSCAN labels are arbitrary per run.

Why this is dangerous:

Cluster `1` today is not guaranteed to be the same narrative as cluster `1` tomorrow. Any lifecycle, trend, or training feature based on raw cluster labels can be wrong.

Fix:

Introduce persistent `narrative_id`.

Suggested logic:

1. Compute a centroid for every current cluster.
2. Compare current centroids to previous narrative centroids.
3. Assign each current cluster to at most one prior narrative if similarity exceeds a tuned threshold.
4. If no match, create a new `narrative_id`.
5. Store `match_score`, `previous_narrative_id`, and `is_new_narrative`.
6. Allow merges and splits explicitly.

Acceptance criteria:

- Lifecycle state is keyed by `narrative_id`, not `cluster_id`.
- A current narrative can be traced back across snapshots.
- A split or merge is represented explicitly instead of silently overwriting history.

### P0.4 Pressure Direction Is Based on Velocity, Not Final Pressure Sign

Evidence:

`analysis/final_pressure.py` calculates:

```python
raw = velocity * acceleration_factor * impact * temporal_factor
final = raw * stability
```

Then direction is assigned from velocity:

```python
if velocity > 0:
    direction = "up"
elif velocity < 0:
    direction = "down"
else:
    direction = "neutral"
```

Why this is dangerous:

If velocity is positive and impact is negative, final pressure is negative, but direction can still be `"up"`. That is a direct sign contradiction.

Fix:

Direction should be derived from final pressure:

```python
direction = "up" if final > epsilon else "down" if final < -epsilon else "neutral"
```

Also store both:

- `attention_velocity_direction`
- `market_pressure_direction`

These are not the same thing.

Acceptance criteria:

- No artifact has `final_pressure < 0` with `direction = "up"`.
- UI uses market pressure direction for bullish/bearish colors.

### P0.5 Emerging Narratives Often Produce Zero Pressure

Evidence:

When no prior match is found in `analysis/velocity.py`, velocity is set to zero:

```python
if match_result:
    v = c_now["size"] - match["size"]
else:
    v = 0
```

Then final pressure multiplies by velocity, so a new narrative with no history produces zero pressure.

Why this is dangerous:

The product vision is specifically about detecting emerging narratives early. A new narrative should not be neutral merely because it lacks a previous match.

Fix:

Separate pressure components:

- emergence score
- growth score
- persistence score
- novelty score
- impact score
- source confirmation score

Possible formula:

```text
attention_score =
  emergence_weight * is_new * log(1 + size)
  + growth_weight * max(size - previous_size, 0)
  + persistence_weight * duration

market_pressure =
  attention_score
  * market_impact_direction
  * confidence
  * source_diversity
  * novelty
```

Acceptance criteria:

- A new high-confidence, multi-source, market-relevant narrative can produce nonzero pressure on first appearance.

## 4. P1 Major Analytical Flaws

### P1.1 Source Relevance Is Too Weak

Current latest narratives include:

- gold project news
- rare earth metals plant news
- Federal Reserve enforcement actions

These may be indirectly relevant, but the system is supposed to be silver-focused. The current ingestion layer allows general metals and macro noise to dominate.

Fix:

Add a silver relevance layer before clustering:

- Direct silver mention
- Silver synonyms: XAG, bullion, COMEX silver, silver futures
- Demand channels: solar/PV, electronics, EVs, medical, industrial fabrication
- Supply channels: silver mines, byproduct mining, Mexico, Peru, Chile, recycling
- Macro channels: real yields, dollar, inflation, Fed, safe haven, gold-silver ratio

Classify each doc:

```json
{
  "silver_relevance": 0.0,
  "relevance_reason": "macro_indirect",
  "asset_links": ["silver", "gold", "copper"],
  "demand_supply_axis": "supply"
}
```

Do not discard all indirect items, but score them differently.

### P1.2 Generic Sentiment Is Not Silver-Market Impact

FinBERT tells you whether financial language is positive or negative. Silver pressure needs something more specific:

- Supply disruption is negative news but bullish silver.
- Solar manufacturing growth is positive industrial news and bullish silver.
- Strong dollar is often positive for USD but bearish silver.
- Industrial recession fears are negative and bearish silver.
- Fed rate cuts can be bullish silver via real yields.
- Rate hikes can be bearish silver via opportunity cost and USD strength.

Fix:

Build a silver-market impact ontology:

| Narrative Type | Typical Silver Impact |
|---|---|
| Mine shutdown | Bullish |
| Supply deficit | Bullish |
| Solar/PV demand growth | Bullish |
| Safe-haven stress | Bullish |
| ETF inflows | Bullish |
| COMEX inventory drawdown | Bullish |
| Strong dollar | Bearish |
| Real yields rising | Bearish |
| Rate hikes | Bearish |
| Industrial slowdown | Bearish |
| Substitution away from silver | Bearish |
| Oversupply/recycling surge | Bearish |

Store:

- `emotional_sentiment`
- `market_impact_direction`
- `impact_channel`
- `confidence`

### P1.3 Novelty Is Missing

Comparable systems treat novelty as a first-class signal. RavenPack explicitly advertises relevance, novelty, impact, temporal scoring, topic tagging, entity tagging, and event categories. SilverAlpha currently has centroid similarity but no explicit novelty score.

Fix:

Add:

```text
novelty = 1 - max_similarity_to_recent_narratives
```

Track novelty at:

- document level
- cluster level
- narrative level

Use novelty to distinguish:

- genuinely new story
- repeated coverage of old story
- resurfaced old story
- stale RSS feed item

### P1.4 Relevance Is Missing

RavenPack and LSEG MarketPsych both emphasize relevance and structured tagging. SilverAlpha clusters everything after basic cleaning if text is long enough.

Fix:

Add relevance scores before and after clustering:

- document-to-silver relevance
- document-to-narrative relevance
- narrative-to-silver relevance
- source relevance
- event relevance

Low relevance docs should either be excluded or marked as background context.

### P1.5 The Market Index Hides Conflict

`analysis/market_index.py` computes:

```python
market_index = signed_pressure / total_abs_pressure
```

If one strong bullish and one strong bearish narrative exist, they cancel to neutral.

That cancellation is mathematically clean but analytically incomplete. A conflicted market is not the same as a quiet market.

Fix:

Output:

- `net_pressure`
- `gross_pressure`
- `bullish_pressure`
- `bearish_pressure`
- `conflict_index`
- `dominance_ratio`
- `dispersion`

Example:

```json
{
  "net_pressure": 0.05,
  "gross_pressure": 1.90,
  "conflict_index": 0.92,
  "state": "high_conflict"
}
```

### P1.6 Regime Classification Is Placeholder Logic

Current regime:

```python
if mpi > 0.3 and n >= 2:
    regime = "momentum"
elif mpi > 0.1:
    regime = "trending"
elif n == 0:
    regime = "quiet"
else:
    regime = "building"
```

Problems:

- Uses absolute MPI only.
- Ignores gross pressure.
- Ignores conflict.
- Ignores historical percentiles.
- Ignores volatility.
- Ignores source quality.
- Ignores lifecycle distribution.

Fix:

Use adaptive regimes:

| Regime | Definition |
|---|---|
| Quiet | Low gross pressure, low narrative count, low novelty |
| Watching | New narratives appear but source confirmation is weak |
| Building | Narrative count and novelty rising |
| Momentum | Aligned pressure in top historical percentile |
| Conflicted | High gross pressure but opposing directions |
| Exhaustion | High duration, falling velocity, falling novelty |
| Shock | High novelty, high source credibility, fast emergence |

### P1.7 Multi-Horizon Output Is Not Actually Multi-Horizon

Current:

```python
short_term = max_velocity * 0.1
medium_term = avg_velocity * 0.1
long_term = min_velocity * 0.1
```

This is not a time-horizon forecast. It is a scaled summary of velocity extremes.

Fix:

Derive horizons from lifecycle and historical behavior:

- Short term: emergence, novelty, acceleration
- Medium term: persistence, source confirmation, sentiment stability
- Long term: structural theme strength, repeated recurrence, macro alignment

Also store horizon confidence separately.

### P1.8 Confidence Is Not Calibrated

`regime_trust.py` maps regime to fixed trust:

```python
momentum = 0.8
trending = 0.65
quiet = 0.4
building = 0.5
```

This is not confidence. It is a label heuristic.

Fix:

Confidence should combine:

- source diversity
- source credibility
- relevance
- novelty
- sentiment/impact agreement
- cluster coherence
- lifecycle stability
- historical calibration
- data freshness

### P1.9 Validation Script Checks Shape, Not Correctness

`validate_improvements.py` passes if files and fields exist. It does not detect:

- mixed snapshot IDs
- lifecycle using `velocity_latest`
- zero training examples
- wrong pressure direction
- synthetic frontend data
- irrelevant narratives
- stale report inputs

Fix:

Add invariant checks:

- All artifacts in report share one snapshot ID.
- No `_latest` artifact participates in timestamped runs.
- Final pressure sign matches direction.
- Lifecycle sizes match current velocity rows.
- Training examples > minimum threshold when training mode is claimed.
- Report narrative IDs are stable.
- No frontend chart is generated without real time series.

## 5. P2 Data and Ingestion Improvements

### P2.1 Live RSS Needs Time-Window Semantics

Current ingestion keeps every feed entry with `published_dt <= RUN_DATE`. It does not define a lower bound for "this snapshot".

Problem:

Every 4-hour run can repeatedly process old items, creating fake persistence.

Fix:

For each snapshot, store:

- `captured_at`
- `published_at`
- `first_seen_at`
- `last_seen_at`
- `source_snapshot_url`

Use either:

- current feed state as an observation, or
- documents newly seen since previous snapshot

Do not confuse the two.

### P2.2 Wayback Ingestion Is Too Naive

Current Wayback URL:

```python
https://web.archive.org/web/{date}/{url}
```

Problems:

- It may not select the closest available capture.
- It does not verify capture timestamp.
- It does not filter feed entries to the target date.
- It sleeps a fixed 2 seconds per source.
- It silently returns empty for many feeds.

Fix:

Use the Wayback CDX API:

- find nearest captures
- store capture timestamp
- store original URL
- verify content type
- filter articles by published date and seen date

### P2.3 Source Coverage Is Too Narrow

Current active sources are mostly RSS feeds. Many return zero entries.

Add silver-specific and macro-specific sources:

- The Silver Institute
- LBMA
- CME/COMEX notices and inventory data
- CFTC COT reports
- USGS mineral commodity summaries
- mining company press releases
- Mexico/Peru/Chile mining regulators
- solar/PV manufacturing news
- industrial PMI sources
- DXY and real-yield context
- ETF flow data
- bullion dealer commentary
- GDELT for global multilingual news

### P2.4 Reddit Needs Better Querying

Current Reddit:

- hot posts only
- limited comments
- no silver relevance filtering before inclusion
- no time-window filtering
- no subreddit-specific weighting

Fix:

Use:

- subreddit search for silver/XAG/COMEX/solar/mining
- new/rising/top time windows
- comment tree sampling
- spam and meme filtering
- upvote/comment velocity
- author/community credibility
- cross-subreddit spread

### P2.5 Deduplication Is Missing

Current cleaning only fixes text and filters short docs.

Fix:

Deduplicate by:

- canonical URL
- title similarity
- text MinHash/SimHash
- source syndication fingerprints
- near-identical summaries

Store duplicate groups rather than deleting evidence blindly.

### P2.6 Entity and Numeric Preservation

Cleaning lowercases everything. Lowercasing helps embeddings but can hurt:

- tickers
- acronyms
- Fed/FOMC distinctions
- proper nouns
- numeric price levels
- percentage changes
- dates

Fix:

Store both:

- `clean_text_for_embedding`
- `display_text`
- `entities`
- `numbers`
- `tickers`
- `commodities`

## 6. P2 Modeling Improvements

### P2.7 Embedding Model Governance

Current model:

```python
all-MiniLM-L6-v2
```

Good for hackathon speed, but the system needs model metadata:

- model name
- model version/hash
- embedding dimension
- created_at
- text preprocessing config

Consider alternatives:

- stronger sentence-transformer models
- domain-specific financial embeddings
- multilingual models if using GDELT/global sources
- hybrid dense + sparse retrieval

### P2.8 HDBSCAN Needs Tuning and Diagnostics

Current:

```python
min_cluster_size=3
min_samples=2
metric="euclidean"
```

Issues:

- Sentence embeddings are often better compared with cosine distance.
- No parameter search.
- No cluster quality report.
- Fallback puts all docs into one cluster if HDBSCAN finds no clusters, which violates noise filtering.

Fix:

Add diagnostics:

- noise ratio
- cluster count
- size distribution
- silhouette or coherence proxy
- representative docs
- nearest competing cluster

Fallback should produce `no_confident_clusters`, not force all docs into a fake narrative.

### P2.9 Stability Is Inflated

Current stability uses mean pairwise cosine similarity including self-similarities. Self-similarity inflates small clusters.

Fix:

Use non-diagonal pairwise similarity. For small clusters, mark uncertainty explicitly.

### P2.10 Narrative Naming Is Too Raw

Current report uses the first document text truncated to 90 characters.

Fix:

Name narratives using:

- top TF-IDF terms
- representative exemplar docs
- commodity ontology tags
- optional LLM summarization

Example names:

- "Solar Demand Tightens Silver Outlook"
- "Federal Reserve Real Yield Pressure"
- "Mexico Mine Supply Disruption"
- "Industrial Slowdown Demand Risk"

### P2.11 Exemplars Should Be First-Class

Comparable research tools show evidence. SilverAlpha should show:

- top representative article
- most novel article
- most credible source
- most shared Reddit post
- strongest contrary evidence

The backup `project_backup/analysis/exemplars.py` contains an early version of this idea.

### P2.12 Merge and Split Tracking Is Missing

Narratives naturally merge and split:

- "solar demand" may split into "China PV overcapacity" and "US solar buildout".
- "rate cut expectations" may merge with "weaker dollar" into one bullish macro story.

Fix:

Store narrative graph edges:

```json
{
  "event": "split",
  "from": "narrative_12",
  "to": ["narrative_31", "narrative_32"],
  "similarity": 0.72
}
```

### P2.13 Contradiction Detection Should Be Semantic

Current conflict is just bullish count > 0 and bearish count > 0.

Fix:

Detect contradiction by theme:

- same theme with opposing claims
- supply shortage versus oversupply
- safe-haven demand versus risk-on liquidation
- Fed cut expectations versus higher-for-longer

Output conflict within each narrative family, not just market-wide counts.

## 7. P2 Prediction and Backtesting Improvements

### P2.14 Training Dataset Is Empty

Current artifact:

```json
{
  "num_examples": 0,
  "examples": []
}
```

Therefore `prediction/train_predictor.py` uses `deterministic_fallback`.

Fix:

Before claiming prediction:

- repair historical backfill
- ensure point-in-time snapshots
- generate labels
- require minimum examples
- walk-forward validate
- publish metrics

### P2.15 Prediction Target Is Ambiguous for Trading

The current target is probability of a meaningful absolute move:

```text
label = 1 if abs(forward_return) >= threshold
```

That predicts volatility/eventfulness, not bullish/bearish direction.

Fix:

Use three outputs:

- probability of meaningful move
- probability move is bullish
- probability move is bearish

Or use:

- `p_up`
- `p_down`
- `p_large_move`
- `expected_pressure_direction`

### P2.16 Avoid Leakage

Historical data must be point-in-time:

- no articles published after snapshot timestamp
- no revisions pulled later
- no latest feed captured retroactively
- no future price data in features
- no "skip-existing" artifacts generated from synthetic history

Add leakage tests before backtesting.

### P2.17 Backtesting Must Include Baselines

Compare against:

- always neutral
- price momentum
- random signal
- generic sentiment only
- volume of news only
- gold return proxy
- DXY/real-yield proxy

Only claim edge if SilverAlpha beats simple baselines.

### P2.18 Calibration Matters More Than Accuracy

For probabilities, track:

- Brier score
- calibration curve
- log loss
- precision/recall at action thresholds
- confusion matrix for direction
- performance by regime

## 8. P2 Backend and Operations Improvements

### P2.19 API Should Not Run the Full Pipeline Synchronously

`silver_backend/api/views.py` runs `run_pipeline.py` from `maybe_refresh_report()` when stale.

Problems:

- API request can block on RSS, embeddings, and FinBERT.
- Pipeline failure is ignored with `check=False`.
- Public endpoint can trigger expensive work.
- No job status is exposed.

Fix:

Use:

- scheduler/cron for pipeline refresh
- background worker
- job status file
- stale-but-known-good report serving
- manual refresh endpoint with auth

### P2.20 API Needs Snapshot Metadata

Every API response should include:

- `snapshot_id`
- `generated_at`
- `data_freshness`
- `source_count`
- `document_count`
- `pipeline_status`
- `is_golden_dataset`
- `warnings`

### P2.21 Error Handling Is Too Broad

Many endpoints catch `Exception` and return the raw message. That is okay for local dev but weak for production.

Fix:

- log full exceptions
- return stable error codes
- hide internal paths
- expose health warnings separately

### P2.22 Security Defaults Are Development Defaults

Current settings are acceptable for local development but not production:

- `DEBUG` defaults true
- default insecure secret key
- allow-any REST framework permissions
- CORS local only but no deployment story
- auto-refresh can execute expensive pipeline work

Fix:

Add production profile and deployment checklist.

## 9. P2 Frontend Improvements

### P2.23 The Frontend Chart Is Synthetic

`frontend/src/components/GlobeUI.tsx` generates a seeded random graph.

Problem:

It visually implies time-series evidence that does not exist.

Fix:

Use backend `time_series`. If only one point exists, show current metrics and a "history unavailable" state.

### P2.24 Frontend First Screen Is a Landing Deck, Not the Product

The current first experience is cinematic. That is memorable, but the product claim is intelligence.

Fix:

For demo/product mode, first screen should show:

- market pressure index
- top emerging narratives
- bullish/bearish pressure split
- lifecycle distribution
- data freshness
- action state

The 3D globe can remain as exploration mode.

### P2.25 Globe Locations Can Mislead

Location extraction is alias-based. Federal Reserve stories all become Washington, mining stories may become country/city nodes, and source names can trigger places.

Fix:

Show why a node is located there:

- extracted entity
- evidence phrase
- source document
- confidence

Also allow a narrative with no precise location to appear in a non-geographic list.

### P2.26 UI Actions Are Inconsistent

Backend `action_state.json` outputs `WATCH`, `ACT`, or `IGNORE`, while node detail uses `BUY`, `SELL`, or `WATCH` based on local pressure threshold.

Fix:

Separate:

- market-level action
- narrative-level pressure
- trading recommendation

Do not show `BUY` or `SELL` unless backed by calibrated directional confidence.

### P2.27 Analytical UI Views Missing

Add:

- top emerging narratives
- fastest growing narratives
- fading narratives
- conflicted narratives
- source confirmation view
- evidence drawer
- timeline
- narrative genealogy graph
- backtest report view
- health/freshness panel

## 10. P3 Repository Hygiene

### P3.1 Generated Artifacts Are Mixed With Source

The repo includes many generated data files, backup files, pycache files, and build artifacts.

Fix:

- Keep small golden examples.
- Move generated snapshots to ignored runtime storage.
- Archive `project_backup` outside active source or convert useful modules into active code.
- Remove pycache and `.DS_Store`.
- Keep `.next` ignored.

### P3.2 Documentation Overclaims

`COMPLETION_SUMMARY.md` says the vision gap is closed and all critical items are addressed. Current artifacts contradict that.

Fix:

Docs should use levels:

- implemented
- wired into pipeline
- validated with artifacts
- validated historically
- product-ready

### P3.3 Dead or Empty Files

Examples:

- `model_interface.py` is empty.
- `prediction/README.md` is empty.
- `frontend/lib/api.js` appears empty.
- `NARRATIVE_ENGINE_LOCK.md` is empty.

Fix:

Either fill them with useful content or delete them.

### P3.4 Configuration Is Scattered

Thresholds are hard-coded across modules:

- HDBSCAN params
- semantic similarity threshold
- pressure thresholds
- regime thresholds
- Reddit subreddit list
- source weights
- refresh timeout

Fix:

Use `config/silveralpha.yaml` or `settings.py` style config.

## 11. Lessons From Similar Systems

### RavenPack

RavenPack emphasizes sentiment analysis, relevance scoring, novelty tracking, temporal scoring, topic tagging, entity/event categories, broad source coverage, and impact analysis. It also treats structured metadata as core to the product, not an afterthought.

Lesson for SilverAlpha:

Do not stop at clustering. Add structured metadata:

- entities
- event types
- relevance
- novelty
- temporal fields
- impact channel

Source:

- https://www.ravenpack.com/products/edge/data/news-analytics

### LSEG MarketPsych

LSEG MarketPsych emphasizes real-time, multi-language news/social data, point-in-time historical coverage, stable entity identifiers, emotion scores, financial language, topic scores, and updates at regular intervals.

Lesson for SilverAlpha:

Stable identifiers, point-in-time data, emotion/urgency/topic scores, and historical backtesting are the real moat.

Source:

- https://www.lseg.com/en/data-analytics/market-data/quantitative-economic-data-solutions/marketpsych-analytics-and-models

### Dataminr

Dataminr focuses on the earliest credible signals of market-moving events, real-time public data, entity/location tags, and integration into workflows. It explicitly highlights commodities and supply chain disruption intelligence.

Lesson for SilverAlpha:

Early signal detection should include event extraction, credibility, location, source confirmation, and workflow integration, not only sentiment.

Source:

- https://www.dataminr.com/use-cases/financial-services/

### AlphaSense

AlphaSense is less of a trading-signal engine and more of a trusted research workflow. It emphasizes auditability, trusted financial/expert intelligence, discovery, reasoning, and deliverable generation.

Lesson for SilverAlpha:

Every pressure signal should have an audit trail: sources, representative docs, why it was classified bullish/bearish, and what changed from the last snapshot.

Source:

- https://www.alpha-sense.com/

### GDELT

GDELT offers global multilingual news/event/story/entity infrastructure and a newer API surface designed for dashboards, monitoring, and ad-hoc search.

Lesson for SilverAlpha:

Use GDELT or similar event/story APIs for global coverage, entity linking, multilingual context, and event clustering instead of relying only on RSS feeds.

Sources:

- https://gdelt.github.io/
- https://docs.gdeltcloud.com/api-reference

## 12. Complete Improvement Backlog

### Foundation

1. Add snapshot resolver.
2. Pass `--snapshot-id` to every module.
3. Add artifact manifest per run.
4. Add health check for mixed artifacts.
5. Ignore or remove `_latest` files from analytical paths.
6. Add point-in-time data rules.
7. Add config file for thresholds.
8. Add structured logging.

### Data Collection

1. Add silver relevance filters.
2. Add lower-bound time windows.
3. Add first-seen/last-seen tracking.
4. Add canonical URLs.
5. Add dedupe.
6. Add source reliability.
7. Add Reddit search/rising/new.
8. Add GDELT.
9. Add mining company releases.
10. Add solar/PV sources.
11. Add COMEX/CME inventory and notices.
12. Add CFTC COT.
13. Add ETF flows.
14. Add macro context: DXY, real yields, Fed expectations.
15. Add source outage reporting.

### Text Processing

1. Preserve display text separately from embedding text.
2. Extract entities.
3. Extract commodities.
4. Extract numbers.
5. Extract dates.
6. Extract tickers/contracts.
7. Extract event types.
8. Extract causal language.
9. Extract forecast language.
10. Add spam/boilerplate filtering.

### Narratives

1. Use persistent `narrative_id`.
2. Store centroid history.
3. Store match score.
4. Add merge tracking.
5. Add split tracking.
6. Add novelty.
7. Add relevance.
8. Add narrative names.
9. Add exemplars.
10. Add contrary evidence.
11. Add source spread.
12. Add lifecycle state.
13. Add narrative family taxonomy.

### Impact and Pressure

1. Separate emotional sentiment from market impact.
2. Add silver-market ontology.
3. Add supply/demand/macro/safe-haven channels.
4. Add emergence pressure.
5. Add persistence pressure.
6. Add acceleration pressure.
7. Add contradiction pressure.
8. Add confidence intervals.
9. Add uncertainty reason.
10. Derive direction from final pressure sign.
11. Add gross/net/conflict index.
12. Add per-horizon logic.

### Prediction

1. Fix training dataset generation.
2. Add walk-forward validation.
3. Add baselines.
4. Add leakage tests.
5. Separate `p_move`, `p_up`, and `p_down`.
6. Add calibration.
7. Add ablation tests.
8. Add prediction explainability.
9. Add outcome update process.
10. Add model versioning.

### Backend

1. Remove synchronous auto-refresh from public GET endpoints.
2. Add job status.
3. Add snapshot metadata.
4. Add health endpoint.
5. Add source coverage endpoint.
6. Add top narratives endpoint.
7. Add narrative detail by `narrative_id`.
8. Add historical timeline endpoint.
9. Add backtest metrics endpoint.
10. Add proper error codes.

### Frontend

1. Replace synthetic chart.
2. Show product dashboard first.
3. Add evidence drawer.
4. Add freshness warnings.
5. Add top emerging narratives.
6. Add lifecycle timeline.
7. Add conflict view.
8. Add narrative genealogy.
9. Add source confirmation view.
10. Add backtest/report page.
11. Add loading/error/empty states.
12. Make mobile layout usable.

### Testing

1. Unit test snapshot parsing.
2. Unit test artifact resolver.
3. Unit test pressure sign/direction.
4. Unit test lifecycle size matching.
5. Unit test market-impact ontology.
6. Integration test full pipeline on golden data.
7. Integration test historical run.
8. API tests for report loading.
9. Frontend build test.
10. Backtest leakage tests.

## 13. Recommended Build Sequence

### Sprint 1: Make The Core Correct

1. Implement `utils/snapshots.py`.
2. Add `--snapshot-id` to all pipeline modules.
3. Fix lifecycle `_latest` bug.
4. Derive pressure direction from final pressure.
5. Add artifact manifest and health check.
6. Update `validate_improvements.py` to catch correctness failures.

Expected result:

The pipeline can prove that one report is built from one coherent snapshot.

### Sprint 2: Make Narratives Real Over Time

1. Add persistent `narrative_id`.
2. Rework velocity around semantic matching with unique assignments.
3. Rework lifecycle around `narrative_id`.
4. Add emergence pressure.
5. Add real narrative time series.

Expected result:

SilverAlpha can answer: "What is emerging, persisting, growing, fading, and why?"

### Sprint 3: Make Silver Impact Credible

1. Add silver relevance classifier.
2. Add market-impact ontology.
3. Separate sentiment from impact.
4. Add source credibility.
5. Add novelty and relevance.

Expected result:

Signals become silver-aware rather than generic-news-aware.

### Sprint 4: Make Predictions Honest

1. Repair historical backfill.
2. Generate nonzero training examples.
3. Add walk-forward backtest.
4. Add baselines.
5. Expose calibrated `p_move`, `p_up`, `p_down`.

Expected result:

The prediction layer can be shown with metrics, not just a fallback.

### Sprint 5: Make The Product Convincing

1. Replace synthetic frontend chart.
2. Add evidence-first dashboard.
3. Add freshness and health indicators.
4. Add narrative detail by stable ID.
5. Add demo/golden mode.

Expected result:

The frontend becomes a truthful intelligence interface, not only a cinematic wrapper.

## 14. Non-Negotiable Invariants

Keep the project identity clear:

1. Clustering remains unsupervised.
2. Price outcomes never feed upstream into narrative discovery.
3. Prediction is downstream and optional.
4. Narrative identity is semantic and temporal, not label-based.
5. Every signal must be explainable through source evidence.
6. Silence is valid. No signal is better than fake confidence.
7. Demo mode must be clearly marked if it uses synthetic or golden data.

## 15. Most Important Single Insight

SilverAlpha should not try to become "a trading bot with news sentiment."

Its strongest version is:

> A silver-specific narrative intelligence engine that discovers, names, tracks, and scores market stories with point-in-time evidence, then optionally estimates whether those stories create bullish, bearish, conflicted, or uncertain pressure.

The system will become much more impressive by becoming more honest and evidence-rich, not by adding more dramatic predictions.
