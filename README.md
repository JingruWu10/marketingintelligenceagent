# Marketing Intelligence Agent

A Python-based, GitHub-ready prototype for AI-assisted marketing analytics.

## Purpose

The agent is designed as a decision partner, not a dashboard narrator. It takes business context and KPI signals, then helps move through:

**Objective -> segmentation -> signal detection -> diagnosis -> hypotheses -> next analysis -> recommendation -> measurement**

The design intentionally keeps human judgment in the loop. AI accelerates exploration and synthesis; analysts retain ownership of validation, experimentation, causal claims, and business decisions.

## Core principles

- Diagnose before recommending.
- Segment before interpreting aggregate changes.
- Treat channels as roles in a customer journey, not isolated silos.
- Separate observed facts from inference, hypotheses, and recommendations.
- Use AI broadly, but constrain it with trusted context, metric definitions, and validation.
- Prefer the smallest next analysis that would change the decision.

## Repository structure

- `src/marketing_intelligence_agent/agent.py` - orchestration and reasoning workflow
- `src/marketing_intelligence_agent/models.py` - typed data models
- `src/marketing_intelligence_agent/rules.py` - deterministic guardrails and analytical rules
- `src/marketing_intelligence_agent/evaluator.py` - golden-insight evaluation
- `data/synthetic_kpis.csv` - sample KPI inputs
- `data/golden_insights.json` - expected high-quality outputs
- `tests/` - unit tests
- `.github/workflows/tests.yml` - GitHub Actions test workflow

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python demo.py
```

## AI integration

The repo is provider-agnostic by design. `agent.py` exposes a place to connect an LLM provider such as OpenAI or Anthropic. For interview/demo purposes, the default path uses deterministic heuristic reasoning over synthetic data so the prototype can run without API keys.

## What 'AI-native' means here

AI-native does not mean sending an underspecified goal like `increase revenue by 100%` to a model and trusting the answer. It also does not mean forcing AI through a rigid checklist that removes its ability to explore.

Instead, the workflow creates an intelligence layer where AI and analysts collaborate at each stage:

1. Business objective and constraints are grounded by the analyst.
2. AI scans a broad KPI and segment surface area.
3. AI proposes competing hypotheses and the smallest discriminating analyses.
4. Deterministic rules and trusted metric definitions constrain the reasoning.
5. The analyst validates causality, tradeoffs, and the final recommendation.
6. Outcomes feed a learning loop and golden-insight evaluation.

