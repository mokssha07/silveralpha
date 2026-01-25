# System Invariants (Do Not Break)

1. Narrative discovery is always unsupervised.
2. No labels or prediction feedback may influence clustering.
3. Coherence is decided by semantic structure, not outcomes.
4. Narratives may merge/split only via embedding similarity over time.
5. Prediction is downstream, probabilistic, and optional.
6. If narratives do not change, predictions should not change.
7. Silence is a valid output.

Breaking any of the above invalidates the system design.
