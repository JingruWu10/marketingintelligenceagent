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

## V2 foundations restored as first-class v3 architecture

The v3 architecture **does not replace v2 with a journey dashboard**. The foundation is a governed, proactive, role-based business decision intelligence and orchestration system. Customer Journey Intelligence is a cross-cutting analytical capability of that system.

### End-to-end architecture and feedback paths

```text
Role-based business experience / customer objectives / proactive exceptions
                  |
                  v
AI Intelligence Engine (question-to-evidence contract; <=5 clarification questions;
proactive business + process monitoring; cross-source, customer-first diagnosis)
                  | governed read requests and factual evidence
                  v
FIRST-CLASS ANALYTICS-OWNED SEMANTIC LAYER
  canonical metric/dimension dictionary, grain, customer/identity/journey states,
  approved joins, attribution/comparison rules, benchmarks, lineage,
  freshness, permissions and deterministic analytical/query capabilities
                  | authorized read boundary (never unrestricted business SQL)
                  v
Existing systems: warehouse, web/app, CRM/CDP, commerce, MAP/email, media,
experimentation, support/VOC (remain systems of record)
                  |
                  v
Intelligence Engine synthesizes VERIFIED OBSERVATIONS vs INFERENCES vs UNKNOWNS
                  |
                  v
HYPOTHESIS INTELLIGENCE -> competing explanations -> evidence for/against
-> small list of 2-3 ranked hypotheses with confidence and uncertainties
                  |
                  v
SMALL-LIST TESTING -> 1-3 decision-changing validation/experiment options
-> smallest useful analysis or customer-facing test, primary metric,
leading indicators, guardrails, comparison/holdout, stopping/decision rules
                  |
                  v
Analytics methodology/evidence validation + Business/CX priority/approval
                  |
                  v
BIDIRECTIONAL ORCHESTRATION + HEALTH (separate permissioned boundary)
  outbound: read -> recommend -> draft -> human-approved execute
  outbound: signals, test plans, audiences, draft actions, approvals
  inbound: acceptance/IDs, configuration, execution status, delivery and
  tracking integrity, operational/process health, exposure, customer outcomes
                  |                      ^
                  v                      |
Existing campaign/CRM/CDP/MAP/ads/experiment tools (execution remains there)
                  |
                  v
OUTCOME + DECISION MEMORY -> causal validation, customer outcomes,
operational integrity, action status, validated and unresolved learnings
                  |
                  +----> governed evidence and future monitoring/diagnosis
                  +----> next hypothesis ranking and test prioritization

GOLDEN INSIGHTS & AI HEALTH: INDEPENDENT, CROSS-CUTTING evaluation of
signal selection, evidence use, competing hypotheses, test quality,
action/operational integrity, outcome claims, regression and autonomy gates.
It inspects every stage, not only after an action or as a dashboard QA card.
```

### A. Semantic Layer — first-class governed facts and analytical capabilities

The **Semantic Layer is an independent foundational service**, not a small Analytics Control Center feature. Analytics owns and versions its definitions; the agent uses them, but cannot invent or silently redefine canonical facts.

- **Business metric dictionary:** exact KPI formulas, numerator/denominator, identity, grain (customer, journey, category, campaign, product, channel, session), dimensions, eligible population and canonical benchmarks.
- **Customer/journey semantics:** customer × brand and customer × category state; explainable stage and cohort definitions, migration/transition and customer need signals, identity uncertainty.
- **Cross-system relationships:** approved joins, keys, campaign/audience/experiment mappings, attribution and comparison rules.
- **Governed capability/query catalog:** deterministic calculations, approved segmentation, cohort/path analyses and valid experiment retrieval, with documented parameters and allowed roles. AI may select capabilities through an authorized service, not access unrestricted SQL.
- **Reliability contract:** freshness, completeness, instrumentation, lineage, quality flags, consent, privacy, policies and limitations returned with every answer.
- **Approval and change control:** new metrics, methods, sources and identity rules require Analytics validation, publication, versioning and regression checks.

**Separate semantics from knowledge:** the Semantic Layer establishes how the business reliably *defines, joins and measures* facts; the Knowledge and Decision Memory layer stores *what previous investigations and experiments suggested or validated*, with context and expiry/revalidation rules.

### B. AI Intelligence — two initiation paths, one governed engine

- **Business-initiated:** objectives, customer questions, constraints and a small question budget (usually 2–3, absolute max 5), then evidence-aware plan and actual approved investigation if connected.
- **AI-initiated:** continuous monitoring detects important customer, business, automation and process gaps, prioritizing decision-impacting exceptions rather than flooding users with anomalies.
- **Cross-system diagnosis:** investigate competing explanations using approved semantic evidence; separate observed, inferred, hypothesized and validated statements. Do not assume a customer outcome is caused by the channel recording the conversion.
- **Role-based decision views:** Executive, CRM, Product, Integrated Marketing, Performance Marketing, Agency and Analyst/Admin consume the same governed intelligence at different levels of depth and within permissions.

### C. Hypothesis Intelligence and Small-List Testing — explicit engines

1. **Generate broadly:** multiple plausible, potentially contradictory explanations, including measurement/process failures and customer-experience causes.
2. **Narrow intentionally:** present typically **2–3 ranked hypotheses**, each with supporting/contradicting evidence, remaining unknowns, confidence, customer impact, testability, reversibility and estimated business importance. No fabricated evidence or impact estimates.
3. **Propose a short test list:** typically **1–3** evidence-discriminating options; the smallest useful next step may be read-only analytical validation rather than customer-facing action.
4. **Separate questions:** hypothesis validation asks whether an explanation is credible; intervention experiments ask whether a change *causally* improves the desired outcome.
5. **Make tests decision-ready:** eligible audience, treatment/control or comparison, outcome and guardrail definitions, readiness/power caveats, stop/decision rules and what decision changes with each result. Analytics validates methods, Business approves prioritization/activation.

### D. Bidirectional Orchestration and Operational Health — continuous, not a one-way send

Orchestration is a separate service boundary above existing execution tools, connected through native connectors, APIs, webhooks or workflow middleware. It **does not replace** existing CRM, CDP, MAP/email, media, web/product or experimentation tools.

- **Outbound:** authorized insight signals; suggested tests and drafts; scoped targets; human approval record; idempotent execution request with target system, object, risk level, reason/evidence ID and rollback requirements.
- **Inbound acknowledgement:** actual system execution IDs, destination configuration, audience and experiment assignment state, accepted/rejected requests, partial failures, retries and delivery status.
- **Operational health:** freshness, suppression/consent, audience overlap, conflicting workflows, tracking integrity, exposure delivery, lead ownership/routing/SLA when applicable, process handoffs and experiment guardrails. Detect recommendations never executed, campaigns without benchmarks, tests launched without control, and actions with missing outcome tracking.
- **Outcomes:** governed retrieval of downstream customer response and commercial outcomes, including treatment/control evidence where appropriate; no automatic causal attribution to a click or platform self-report.
- **Health-driven escalation:** failed, unmeasurable or contradictory execution triggers appropriate alert/manual review or bounded rollback where authorized, not an unsupported success claim.
- **Autonomy ladder:** Read -> Recommend -> Draft -> Human-approved Execute. Material sends, targeting, launch/pause, budget, routing and high-risk changes are approval-gated. Monitoring is not authorization to write.

### E. Golden Insights & AI Health — independent evaluation and two learning loops

**Golden Insights is a first-class, cross-cutting evaluation system**, not merely an Analytics UI card or a final summary of campaign results.

- **Insight quality:** did the agent prioritize the right meaningful exception, grounded in customer/business context?
- **Hypothesis quality:** were alternatives considered and evidence for/against reported faithfully, with meaningful confidence and unknowns?
- **Small-test quality:** was the smallest discriminating test proposed with defensible metrics, controls, guardrails and decision criteria?
- **Execution/health quality:** did requests observe permissions, reach the correct destination, execute as intended and report operational problems?
- **Outcome/learning quality:** are incrementality and experience claims supported, are negative/null findings retained, and do lessons represent conditional precedent rather than permanent truth?
- **Independent gates:** golden-question/golden-insight suites, deterministic checks, adversarial and regression evaluations, observability/audit trails, and approval gates before promoting metrics, evidence, new tools or greater autonomy.

Maintain **two distinct loops**:
1. **Business/customer outcome loop:** signal -> test/action -> operational telemetry -> customer outcomes and guardrails -> validated effect -> business decision.
2. **Agent intelligence quality loop:** evidence selection -> hypothesis/test quality -> execution correctness -> Golden Insights evaluations -> error analysis/QA -> approved changes to prompts, capability definitions and evaluation criteria.

A test with no positive uplift can still be an excellent test and good agent behavior; positive business results do not establish sound agent reasoning. Persist an **Experiment & Decision Memory** entry linking original goal/signal, semantics version, evidence, hypotheses, alternatives, approved test, execution-system IDs, health telemetry, measured outcome, limits, owner and reviewed learning. No unchecked self-modification of canonical facts or autonomy.

### F. V3 customer intelligence as an extension of the foundation

Customer Journey Intelligence enriches the intelligence and hypothesis engines with customer × brand/category stages, cross-touchpoint customer needs and journey friction, segmentation and migration, VOC and customer problems, priorities and experiment outcomes. It must not narrow the whole system to web analytics or become a replacement for role-based decision intelligence, semantic services, small-list testing, orchestration or Golden Insights.

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

## Five-question interaction budget (v3 requirement)

For each customer/business investigation, the agent may ask **at most five user-facing clarification questions total** (not five per subtopic). Aim for **two or three** and **stop sooner** as soon as an actionable evidence contract can be created. Questions must be decision-changing, concise, and one at a time; avoid splitting the same decision into several repetitive questions. Never ask users to provide facts that can be obtained from sources they are authorized to query.

1. **Reuse context first:** count and carry forward earlier answers in the same investigation. Do not restart the budget after switching screens, roles, or threads that preserve the investigation.
2. **Gate each question:** ask only when its answer would materially change the target population, customer outcome, evidence needed, decision rule, or experimental design. Otherwise use an explicit provisional assumption (with uncertainty and rationale).
3. **Early exit:** after two or three answers, present the draft analytical plan once it is useful. Provide an optional 'Analyze now' path even before the budget is used.
4. **Hard stop at five:** no sixth intake question. Deliver an evidence-aware decision brief: business objective, customer outcome, eligible cohort, primary/secondary KPIs and guardrails, comparisons, likely explanations as *hypotheses*, next governed data checks, feasible incrementality design, assumptions, and unresolved blockers.
5. **Availability and safety:** do not claim to have queried data that is unavailable; if authorized sources exist, perform permitted read-only exploration. Lack of permission or critical data quality blocks source-dependent conclusions rather than eliciting endless questions. Production write actions still require human approval.
6. **Follow-up is user-led:** users may voluntarily provide more context after the brief; the agent can continue analysis, but must not autonomously start another questionnaire to evade the cap.

**Example: email retention** — Given 'improve email CTR' → 'strengthen customer retention' → 'active existing customers' → 'personalized ongoing value' → 'repeat product purchase', there is already enough to draft an investigation. Do not ask for purchase cadence: calculate historical repurchase windows by cohort and category using approved sources, or label that analysis pending. Click rate is a supporting diagnostic; incremental repeat-purchase rate may be a candidate primary KPI, subject to Analytics approval. Compare a randomized email treatment vs holdout if ethical, feasible and properly powered; protect unsubscribe, complaint, fatigue and customer-experience guardrails. No conversion or causal impact is presumed without data.

**Implementation note:** The static browser prototype demonstrates a front-end question counter and sample guided flow. A future service must enforce this budget server-side on persisted investigation state, not by trusting a client-side counter.

## Live local v0.3 integration (executive investigation)

**Integration added to feature branch:** `demo/launch_agent_v03/` now contains the read-only Python Semantic Layer (`semantic_launch.py`), multi-turn investigation router (`conversation_agent.py`), hypothesis and Golden Insights rule evaluation (`hypothesis_engine.py`), investigation helper (`investigation_engine.py`), a localhost HTTP backend (`integrated/server.py`) and a new executive interface (`integrated/executive.html`). The two are connected with HTTP `/api/overview` and `/api/investigate`, with an in-memory session ID preserving the context of follow-up questions. See `demo/launch_agent_v03/README.md` for ZIP data fixtures and startup instructions. The original static `demo/customer-journey-v3.html` is unchanged and remains a separate illustrative demo; the integrated interface is a new, runnable local experience, not a public hosted application.

**Verified locally:** all 25 v0.3 engine unit tests passed. An HTTP smoke test returned the Zelda overview (53 purchasers), then answered two consecutive questions under one session and produced an eight-row descriptive evidence matrix. A matching smoke-test script is committed alongside the backend. The bundled CSV fixture ZIP remains distributed outside GitHub, so running this branch requires pointing the backend at that synthetic data directory.

**Outstanding:** safe real-user authentication and permissions, production semantic adapters, robust identity resolution, secure session persistence, autonomous *execution* of next read-only investigative analyses, LLM tool planning, live orchestration/health telemetry, independent Golden Insights grading, and deployment. In particular, the current rule-based agent **suggests** product-by-cohort investigation but has not yet executed that additional analysis. No production writes exist.
