"""Stateful, read-only launch investigation planner over approved synthetic semantic tools.

No LLM, SQL generator, production auth or external connector. Only explicitly allowlisted
launch/intent analytical queries. Session store holds context, not hidden reasoning.
"""
from __future__ import annotations
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from investigation_engine import investigate, _rows, ALLOWED_LAUNCHES
from semantic_launch import run, synthetic_identity
from hypothesis_engine import assess, golden_review

VERSION = 'stateful-launch-agent-v0.3'
MAX_USER_QUESTIONS = 5
ALLOWED_TOOLS = ['launch_metrics','segment_progression','event_cooccurrence','checkout_mix','launch_comparison']
INTENTS = {'overview','journey','audience','checkout','benchmark','test_plan','source_quality'}


def classify(text: str, current: str | None = None) -> str:
    q = text.lower()
    if re.search(r'\b(test|experiment|hypothes|validate|what should we do|next step)\b', q): return 'test_plan'
    if re.search(r'\b(switch 2|last year|previous launch|historical|benchmark|compar)\b', q): return 'benchmark'
    if re.search(r'\b(checkout|guest|authenticated|login|payment)\b', q): return 'checkout'
    if re.search(r'\b(channel|audience|wrong audience|traffic source|targeting|marketing mix|acquisition)\b', q): return 'audience'
    if re.search(r'\b(instrument|tracking|quality|identit|reliab|data issue|lineage)\b', q): return 'source_quality'
    if re.search(r'\b(journey|progress|discover|explor|pdp|wishlist|cart|search|funnel|losing|understand|friction|why|where)\b', q): return 'journey'
    return current if q in {'what about them?', 'why?', 'and then?', 'tell me more', 'what next?'} and current else 'overview'


def _event_sets(folder: Path, launch_id: str, selected: set[str]):
    from collections import defaultdict
    by_type=defaultdict(set)
    for e in _rows(folder, 'ga4_events.csv'):
        if e['launch_id'] != launch_id: continue
        key=synthetic_identity(e)
        if key in selected: by_type[e['event_name']].add(key)
    return by_type


def _cohort_analysis(folder: Path, launch_id: str) -> dict[str, Any]:
    cohort = {r['customer_key']:r['primary_segment'] for r in _rows(folder,'customer_launch_segments.csv') if r['launch_id']==launch_id}
    cohorts = {}
    for segment in sorted(set(cohort.values())):
        members = {k for k,v in cohort.items() if v==segment}
        ev = _event_sets(folder, launch_id, members)
        reached=members & ev['session_start']
        pdp=reached & ev['view_item']
        cart=reached & ev['add_to_cart']
        wishlist=reached & ev['add_to_wishlist']
        search=reached & ev['search']
        orders=[o for o in _rows(folder,'orders.csv') if o['launch_id']==launch_id and o['order_status']=='completed' and o['customer_key'] in reached]
        buyers={o['customer_key'] for o in orders}
        cohorts[segment]={
            'reached':len(reached),'pdp':len(pdp),'wishlist':len(wishlist),'cart':len(cart),'search':len(search),
            'buyers':len(buyers), 'search_and_pdp':len(search&pdp), 'pdp_and_cart':len(pdp&cart),
            'cart_and_purchase':len(cart&buyers),
            'pdp_rate':round(len(pdp)/len(reached),5) if reached else None,
            'cart_rate':round(len(cart)/len(reached),5) if reached else None,
            'purchase_rate':round(len(buyers)/len(reached),5) if reached else None,
            'cart_given_pdp':round(len(pdp&cart)/len(pdp),5) if pdp else None,
            'purchase_given_cart':round(len(cart&buyers)/len(cart),5) if cart else None,
            'checkout_order_types': {type_:sum(1 for o in orders if o['checkout_type']==type_) for type_ in ('authenticated','guest_checkout')},
        }
    return cohorts


def _missing(intent: str):
    missing=['Verified segment classification and identity coverage','Incremental/causal counterfactual']
    if intent in {'audience','journey','test_plan'}:
        missing+=['Person-level campaign exposures and valid acquisition-source mapping','Inventory availability and customer research/VOC']
    if intent in {'checkout','journey','test_plan'}:
        missing+=['Checkout step/error and abandonment telemetry']
    return missing


def _hypotheses(intent: str):
    options=[
      {'id':'H1','label':'Product understanding / familiarity','status':'unvalidated','evidence_for':'Observed cohort-level differences in exploratory behaviors','counter_evidence_or_gap':'No task-completion or customer research evidence','next_check':'Qualify product browsing/search behavior by segment, then examine customer research'},
      {'id':'H2','label':'Acquisition intent / channel mix','status':'unvalidated','evidence_for':'Cohorts differ in observed engagement and purchasing','counter_evidence_or_gap':'No person-level campaign exposure or source attribution available','next_check':'Request consented campaign-touch mapping, then compare matched channels/products'},
      {'id':'H3','label':'Availability / checkout / tracking friction','status':'unvalidated','evidence_for':'Cart and purchase events allow descriptive checks','counter_evidence_or_gap':'No inventory time series, checkout errors or support feedback','next_check':'Audit product availability, checkout steps, instrumentation and experiment exposure'},
    ]
    if intent=='checkout': return [options[2],options[0],options[1]]
    if intent=='audience': return [options[1],options[0],options[2]]
    return options


def new_session(launch_id='ZELDA_2026'):
    if launch_id not in ALLOWED_LAUNCHES: raise ValueError('Unknown launch')
    return {'version':VERSION,'launch_id':launch_id,'turns':[], 'user_clarifications':0,
            'goal':'Understand customer groups and launch progression','active_intent':None,
            'read_only':True,'approved_actions':[], 'created_at':datetime.now(timezone.utc).isoformat()}


def respond(folder: str | Path, question: str, state: dict | None = None, launch_id='ZELDA_2026') -> tuple[dict,dict]:
    if not question.strip(): raise ValueError('Question cannot be empty')
    folder=Path(folder)
    state=dict(state) if state is not None else new_session(launch_id)
    lid=state['launch_id']
    if lid not in ALLOWED_LAUNCHES: raise ValueError('Unknown launch')
    if state.get('user_clarifications',0)>MAX_USER_QUESTIONS: raise ValueError('Clarification budget exceeded')
    intent=classify(question,state.get('active_intent'))
    if intent not in INTENTS: raise ValueError('Unapproved analytical intent')
    # Existing governed semantic API; all source calculations are deterministic.
    semantic=run(folder,lid)
    cohorts=_cohort_analysis(folder,lid)
    new=cohorts.get('new_to_franchise')
    existing=cohorts.get('existing_zelda_gamer')
    qa=semantic['quality']
    risk=['Synthetic identity convention is not a production customer identity system',
          'Segments are scenario labels and cannot establish customer intent or protected traits']
    if qa['unmapped_pseudo_ids'] or qa['user_id_conflicts'] or qa['order_item_revenue_mismatch']:
        risk.append('Source reconciliation errors detected; hold affected conclusions')
    else: risk.append('Event, identity and revenue reconciliation passed fixture checks')
    insight='Observed launch performance by reached customers and completed purchasing customers.'
    evidence=[]
    if new and existing:
        insight=(f"In the synthetic Zelda fixture, new-to-franchise purchasers are {new['buyers']}/{new['reached']} "
                 f"({100*new['purchase_rate']:.1f}%) versus {existing['buyers']}/{existing['reached']} "
                 f"({100*existing['purchase_rate']:.1f}%) for existing Zelda gamers. This is not an adjusted or causal comparison.")
        evidence=[{'metric':'reached','new_to_franchise':new['reached'],'existing_zelda_gamer':existing['reached']},
                  {'metric':'pdp_rate','new_to_franchise':new['pdp_rate'],'existing_zelda_gamer':existing['pdp_rate']},
                  {'metric':'cart_given_pdp','new_to_franchise':new['cart_given_pdp'],'existing_zelda_gamer':existing['cart_given_pdp']},
                  {'metric':'purchase_given_cart','new_to_franchise':new['purchase_given_cart'],'existing_zelda_gamer':existing['purchase_given_cart']}]
    answered_by_data=True
    if intent=='audience':
        insight+=' The current campaign table has campaign metadata but no customer-level exposure join, so it cannot resolve an audience-quality explanation.'
        answered_by_data=False
    if intent=='benchmark':
        other='SWITCH2_2025' if lid=='ZELDA_2026' else 'ZELDA_2026'
        reference=run(folder,other)
        evidence.append({'launch':other,'reached':reference['metrics']['reached'],
                         'buyers':reference['metrics']['purchasing_customers'],
                         'purchase_per_reached':reference['metrics']['purchase_per_reached']})
        insight+=' The prior launch is only a same-length descriptive benchmark; different product mix and audiences preclude impact attribution.'
    if intent=='checkout':
        evidence.append({'checkout_types':semantic['metrics']['checkout_types']})
        insight+=' Checkout-type counts describe completed orders only and cannot establish abandonment causes.'
    if intent=='test_plan':
        insight+=' First run read-only same-product/customer-group and milestone checks; only propose controlled experiments after verifying exposure eligibility and customer problems.'
    requested_tools=['launch_metrics','segment_progression','event_cooccurrence']
    if intent=='checkout': requested_tools.append('checkout_mix')
    if intent=='benchmark': requested_tools.append('launch_comparison')
    # Intentionally not emitting fabricated campaign, inventory or VOC tool calls.
    hypotheses=_hypotheses(intent)
    small_tests=[
      {'priority':1,'type':'read_only','name':'Validate qualified progression and cohort comparability',
       'action':'Compare governed PDP, search, wishlist, cart and order intersections by cohort and product',
       'success_criterion':'Identify which transition and population merits follow-up with valid identity/event quality',
       'approval':'Analytics review; no external changes'},
      {'priority':2,'type':'conditional_experiment','name':'Customer clarity or landing-context experiment',
       'action':'Only after discriminating evidence, randomize eligible exposure with a holdout and relevant guardrails',
       'success_criterion':'Incremental customer progression and downstream purchasing without guardrail harm',
       'approval':'Business and Analytics approval; NOT executed'}]
    quality_checks={
      'semantic_allowlist':all(x in ALLOWED_TOOLS for x in requested_tools),
      'identity_join_conflicts':qa['user_id_conflicts'],
      'order_item_revenue_reconciles':not qa['order_item_revenue_mismatch'],
      'purchase_event_order_reconciles':qa['completed_orders_without_purchase_event']==0 and qa['purchase_events_without_matching_order']==0,
      'clarification_budget_respected':state.get('user_clarifications',0)<=MAX_USER_QUESTIONS,
      'external_actions_executed':False,
      'causal_claims_supported':False,
    }
    comparison = assess(cohorts, qa, question) if lid == 'ZELDA_2026' else {'status':'unsupported_comparison','hypotheses': [], 'next_analyses': [], 'evidence_matrix': []}
    comparison['golden_insights'] = golden_review(comparison) if lid == 'ZELDA_2026' else {'status':'not_evaluated'}
    if comparison.get('status') == 'blocked_by_quality':
        insight = 'Data quality failures block reliable customer comparison until reconciled. ' + insight
    answer={
      'agent_version':VERSION,'mode':'synthetic_read_only','question':question,'intent':intent,'launch_id':lid,
      'executive_answer':insight,'answered_with_available_data':answered_by_data,
      'evidence':evidence,'cohorts':cohorts if intent in {'journey','overview','checkout','benchmark','test_plan'} else {},
      'hypotheses':hypotheses,'small_list_tests':small_tests,'missing_evidence':_missing(intent),
      'hypothesis_comparison':comparison,
      'semantic_contract':{'version':semantic['semantic_version'],'grain':'distinct synthetic customers per launch and milestone',
            'observation':semantic['evidence']['observation'],'metrics':semantic['metrics'],
            'identity':'fixture-only mapped synthetic customer key','read_only':True,
            'query_allowlist':requested_tools,'causal_claims_permitted':False},
      'golden_insights':{'status':'rule_checks_only','checks':quality_checks,'limitations':risk},
      'orchestration':{'status':'not_connected','outbound_actions':[], 'execution_ids':[],
                       'inbound_telemetry':'not_available'},
      'decision':'Prioritize evidence validation over campaign changes; choose experiment only if hypotheses become testable.',
      'clarification_questions_asked':state.get('user_clarifications',0),'max_clarification_questions':MAX_USER_QUESTIONS,
      'follow_up_suggestions':['Is the gap present after product views?', 'Are we reaching the wrong audience?',
                               'How does this compare with Switch 2?', 'Which small test should we run first?']
    }
    state['active_intent']=intent
    state['turns']=list(state.get('turns',[]))+[{'question':question,'intent':intent,'tools':requested_tools,
                 'read_only':True,'evidence_version':semantic['semantic_version']}]
    return answer,state


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir',required=True)
    parser.add_argument('--question',required=True)
    parser.add_argument('--session',help='Optional JSON session file; persists only explicit investigation state')
    parser.add_argument('--launch-id',default='ZELDA_2026')
    args=parser.parse_args()
    prior=json.loads(Path(args.session).read_text()) if args.session and Path(args.session).exists() else None
    answer,state=respond(args.data_dir,args.question,prior,args.launch_id)
    if args.session: Path(args.session).write_text(json.dumps(state,indent=2)+'\n')
    print(json.dumps(answer,indent=2))

if __name__=='__main__': main()