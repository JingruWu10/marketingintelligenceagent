# Integrated Marketing Intelligence Agent v0.3 — Executive launch dashboard

This integration runs a **local browser UI and a real read-only Python analysis service**. Unlike the earlier static `demo/customer-journey-v3.html` example, the integrated executive view calls the v0.3 Semantic Layer and stateful Investigation Engine for its metrics and follow-up answers.

## Quick start

1. Download the conversation artifact **Zelda_Agent_Integrated_v0.3.zip**. It includes synthetic CSVs, Python engines, tests, and the same integrated frontend/server committed here.
2. Extract the ZIP.
3. In a terminal, run from the extracted **zelda_agent_v03** directory:

   ```sh
   python integrated/server.py --data-dir . --host 127.0.0.1 --port 8787
   ```

4. Open **http://127.0.0.1:8787** in your browser.
5. Try "Why are new-to-franchise customers buying less?" then "Is it product understanding or the wrong audience?" — the second question reuses the same investigation session.

### Running from this GitHub branch

The source files are at `demo/launch_agent_v03/`. The synthetic fixture CSVs are deliberately distributed in the ZIP rather than committed to GitHub. Extract the ZIP and either run it directly as above or pass its `zelda_agent_v03` directory to the repo version:

```sh
python demo/launch_agent_v03/integrated/server.py --data-dir /path/to/zelda_agent_v03 --host 127.0.0.1 --port 8787
```

The following files are committed: `conversation_agent.py`, `investigation_engine.py`, `semantic_launch.py`, `hypothesis_engine.py`, `integrated/server.py`, `integrated/executive.html`. This extension does **not** modify the original v2 engine or replace the existing static v3 demo.

## Runtime API contract

- `GET /api/health`: local service status.
- `GET /api/overview?launch_id=ZELDA_2026`: recalculates governed metrics from the local synthetic CSVs.
- `POST /api/investigate`: JSON `{"launch_id":"ZELDA_2026","question":"Is it product understanding or the wrong audience?","session_id":null}`. Returns a new `session_id`, the analysis, and a turn count. Resubmit `session_id` to retain context.
- The UI resets the conversation when the user switches launches.
- Data metrics and hypothesis comparison are deterministic and provenance-aware; v0.3 still **proposes**, but does not execute, its product-by-cohort read-only next-analysis plan.

## Evidence and permissions

The fixture uses an explicit synthetic pseudo-ID convention, **not** production identity resolution. The executive view displays independent milestone participation, customer-segment comparisons, supporting/contradictory hypothesis evidence, proposed small tests, missing sources, deterministic Golden Insights rule checks, and read-only orchestration status. A cohort difference is not causal evidence, and fixture gifting / suspected resale labels are not verified customer traits.

This is **not production-ready**: no authorization, consent enforcement, rate limits, LLM tool planning, production API connections, autonomous actions, independent Golden Insights model evaluation or durable shared session store. By default the service binds to localhost. Do not expose it to the internet or load real customer data.

## Verification

The v0.3 unit suite passed **25 tests** in the local package. A local HTTP smoke test verified `/api/health`, Zelda overview (53 purchasers), and consecutive `/api/investigate` requests retaining 2 turns and returning 8 evidence-matrix rows.

Integration commits affect only the v3 feature branch and its existing PR; `main` remains unchanged.
