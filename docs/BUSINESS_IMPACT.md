# Business Impact Analysis

## Problem Statement

Manual property valuation by agents is slow, inconsistent across agents, and
hard to audit. A well-calibrated, always-available prediction service lets
agents, buyers, and internal analytics teams get a defensible price estimate
in under 20ms, with a transparent confidence interval instead of a single
point guess.

## Value Delivered

| Metric | Estimate | Basis |
|---|---|---|
| Prediction accuracy | R² = 0.982, MAPE = 6.18% | Ensemble model on held-out validation set |
| Response latency | ~18ms average (measured in this repo's test run) | FastAPI + in-memory model, no external DB round-trip |
| Time saved per valuation | Minutes → milliseconds | Replaces manual comps research for a first-pass estimate |
| Scalability | 3–10 replicas via HPA | Kubernetes autoscaling on CPU utilization |
| Auditability | Every prediction logged with model version | SQLite `predictions` table |

## Where the ROI Comes From

1. **Faster first-pass estimates** — agents get an instant, defensible
   starting number instead of manually pulling comparable sales, freeing
   time for higher-value client work.
2. **Consistency** — the same inputs always produce the same estimate,
   removing agent-to-agent valuation variance that can erode client trust.
3. **Scalable self-service** — the API/dashboard split means the same model
   can power an internal tool, a customer-facing web widget, and a partner
   integration without duplicating logic.
4. **Lower model-risk** — the CI/CD quality gate and versioned registry mean
   a bad retrain can't silently degrade live predictions; rollback is a
   one-command operation (see `DEPLOYMENT.md`).

## Caveats & Honest Limitations

- The dataset backing this capstone is **synthetic** (seeded, not scraped
  from a live listings API), so the specific accuracy numbers above describe
  performance on this dataset's distribution, not a claim about real-world
  Hyderabad property prices. The architecture and MLOps practices transfer
  directly to real data; the headline accuracy number would need
  re-validation against real transactions before being used for actual
  pricing decisions.
- A single confidence-interval margin (±8%, derived from validation MAPE) is
  a simplification — a production system would ideally produce
  per-prediction uncertainty (e.g., via quantile regression) rather than a
  flat percentage band.
- No claim is made about "revenue impact" in currency terms, since that
  depends on a real deployment's actual usage volume and conversion
  behavior, which isn't something a capstone project can responsibly
  estimate in advance.
