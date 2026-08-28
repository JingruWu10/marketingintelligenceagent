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

## Architecture

```text
Business objective + constraints
            |
            v
Trusted KPI / customer / campaign data
            |
            v
Python deterministic analytics
  - metric calculations
  - segmentation
  - signal detection
  - guardrails
            |
            v
Observed signals + candidate hypotheses
            |
            v
OpenAI synthesis layer (optional)
  - connect signals
  - rank hypotheses
  - identify unknowns
  - propose next analysis
  - translate to business language
            |
            v
Human analyst
  - validate evidence
  - test causality
  - weigh trade-offs
  - approve recommendation
            |
            v
Experiment / action / measurement loop
```

The OpenAI layer receives the deterministic output as its evidence boundary. It does **not** own metric definitions, statistical validation, or causal claims.

## Repository structure

- `src/marketing_intelligence_agent/agent.py` - orchestration and reasoning workflow
- `src/marketing_intelligence_agent/models.py` - typed data models and structured AI output
- `src/marketing_intelligence_agent/rules.py` - deterministic guardrails and analytical rules
- `src/marketing_intelligence_agent/evaluator.py` - golden-insight evaluation
- `src/marketing_intelligence_agent/llm/openai_provider.py` - OpenAI Responses API integration
- `src/marketing_intelligence_agent/prompts/synthesis.py` - synthesis instructions
- `data/synthetic_kpis.csv` - sample KPI inputs
- `data/golden_insights.json` - expected high-quality outputs
- `tests/` - unit tests
- `.github/workflows/tests.yml` - GitHub Actions test workflow

## Quick start: deterministic mode

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python demo.py
```

## OpenAI integration

The OpenAI provider uses the Responses API with Pydantic structured outputs.

1. Install dependencies:

```bash
pip install -e .
```

2. Export your API key. Do not commit it to GitHub:

```bash
export OPENAI_API_KEY="your_api_key_here"
export OPENAI_MODEL="gpt-5.6"
```

3. Run the AI-enabled demo:

```bash
python demo_openai.py
```

The output contains two independently inspectable sections:

- `deterministic`: trusted calculations, signals, hypotheses, and guardrails
- `ai_synthesis`: structured executive summary, observations, inferences, unknowns, next analysis, and recommendations

## What "AI-native" means here

AI-native does not mean sending an underspecified goal like `increase revenue by 100%` to a model and trusting the answer. It also does not mean forcing AI through a rigid checklist that removes its ability to explore.

Instead, the workflow creates an intelligence layer where AI and analysts collaborate at each stage:

1. The analyst grounds the business objective and constraints.
2. Deterministic analytics establish the trusted evidence boundary.
3. AI broadens synthesis across signals and competing hypotheses.
4. AI proposes the smallest decision-changing next analyses.
5. The analyst validates causality, trade-offs, and the final recommendation.
6. Outcomes feed a learning loop and golden-insight evaluation.

## Security and governance

- Never commit API keys; `.env` is ignored.
- Send only data that is appropriate for the configured OpenAI project and organizational policies.
- Keep metric definitions, access controls, lineage, validation, and causal claims outside the generative layer.
- Use structured outputs so downstream applications can validate the model response before acting on it.
