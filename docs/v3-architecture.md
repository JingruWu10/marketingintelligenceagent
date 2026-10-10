# Marketing Intelligence Agent v3 — architecture extension

Status: **concept / prototype**, not production integration. This document *extends*, never replaces, the architecture documented in the main README and implemented in `src/marketing_intelligence_agent/`.

## Preserved v2 contract

Business objective + constraints → AI question-to-evidence translation → **Analytics-governed semantics / trusted sources** → deterministic calculations and monitoring → cross-system diagnosis → evidence-ranked hypotheses → human validation and business decision → **separate orchestration/API integration layer** → existing systems execute *only approved actions* → outcome measurement → learning loop.

**AI narrows the decision space. Humans make the decision.** The generative layer does not define canonical metrics, bypass authorization, assert unsupported causality, or write to production.

### Preserved architectural layers

1. **Business experience:** role-relevant question, customer objective, context, constraints and decision. Hide query syntax and backend plumbing.
2. **Translation and evidence contract:** clarify grain, metric definition, customer segment, benchmark, timeframe, provenance, quality requirements, and decision.
3. **Governed data and deterministic analytics:** approved semantic views / joins / identities, metric definitions, guardrails, data-quality checks, lineage and permitted exploratory read operations. Existing warehouse, CDP, CRM, commerce, media, experimentation and VOC systems remain source systems.
4. **Intelligence:** proactive monitoring + multi-step investigation + conflicting-evidence evaluation; observed → inferred → hypothesized → validated; small set of competing hypotheses.
5. **Human judgment:** Analytics validates evidence, statistics and methodologies; Business/CX owns prioritization, customer context, strategy, interventions and outcomes. Dual approval applies to experiment evidence promotion and customer-problem closure.
6. **Orchestration:** distinct read/recommend/draft/approved-write capabilities via connector/API/middleware. No production change without designated approval; the agent never replaces execution systems.
7. **Closed-loop learning:** outcome metrics, experiment memory, approved evidence, decision rationale, calibration, unresolved questions, and knowledge freshness.

## v3 customer journey extensions

- **Customer intelligence home:** customer × brand and customer × category journeys, awareness → interest → consideration → purchase → retention, stage-specific next customer action, customer-first prioritized exceptions.
- **Segment explorer:** dynamic intersections, comparative journeys, cohorts, paths, migration, Analytics-only clustering and official segmentation publication.
- **Customer problem workspace:** observed friction, VOC, hypotheses, impacted population, residual friction, opportunity scenarios, shared investigations, dual ownership, initiatives, experiments and partial resolution.
- **Initiative studio:** customer problem → success-metric design conversation → measurement readiness → launch guardrails → outcome validation.
- **Analytics control center:** approved analytical capability catalog, methodology library, SQL governance, data health, review queues, logs, knowledge/evidence promotion and golden-question QA.
- **Customer knowledge:** needs library, journey knowledge map, research / tracking gaps, approved UX/CX best-practice guidance, experiment and decision memory.

## Explicit access boundaries

| Action | Business/CX role | Analytics role |
|---|---|---|
| Ask governed natural-language questions | Allowed | Allowed |
| View permitted summaries/segments | Allowed | Allowed |
| Write, edit or run arbitrary SQL | **Forbidden** | Permitted under policy |
| Trigger governed approved analysis via service | Allowed, where catalog authorizes | Allowed |
| Execute/configure/publish clustering | Forbidden | Governed |
| Approve official metrics, methodologies and instrumentation | Forbidden | Required |
| Approve operational interventions | Designated business owner | Supports measurement; approvals as designated |
| Write to production systems | Never directly | Never without separately authorized execution |

The UI role switch in the static prototype is illustrative only. Production enforcement requires backend identity, authorization per capability, service-level query restrictions, row/column controls, privacy/consent checks, execution quotas, review workflows and audit logging. **Natural-language questions from business users must not become unrestricted SQL execution.**

## Investigation lifecycle

Question → interactive objective / success clarification → analysis plan → risk and capability check → approved read-only exploration → data-quality validation → multi-step cross-source diagnosis → findings with observed vs hypothesized status → customer-problem/initiative decision → human-approved action via existing tools → measured outcome → experimentally grounded learning → recalibration.

When the underlying data are critically unreliable, block affected conclusions; otherwise continue only using independently reliable sources and mark limitations. Persist incomplete investigations and resume when dependencies become available, under renewed permissions and quality checks.

## Incremental implementation plan

**Phase 0 (this branch):** Preserve original Python services, add v3 architecture contract and static interactive prototype using **synthetic data**. No GA4, warehouse, CRM, or production connections.

**Phase 1:** Define typed Journey, Segment, CustomerProblem, Investigation, Initiative, EvidenceRecord, Approval, and CapabilityPermission contracts; reuse deterministic `rules.py`, `agent.py`, and `evaluator.py`; add golden-question tests.

**Phase 2:** Implement authorized semantic-query tools, Analytics-owned capability catalog and methodology registry, plan validation, provenance, data-quality checks, and persistent investigation state.

**Phase 3:** Connect approved data sources, real measurement/experiment services, and cross-system orchestration with separate human-approved write permissions.

**Non-goal:** Claim that a static HTML mockup implements production auth, SQL execution, predictive clustering, causal inference, or a live autonomous agent.

## Relationship to previous implementation

The existing Python prototype and Streamlit versions are kept unchanged. The v3 UI is an additional presentation layer; future backend integration should adapt existing deterministic and structured-AI components rather than fork a competing analytical engine.
