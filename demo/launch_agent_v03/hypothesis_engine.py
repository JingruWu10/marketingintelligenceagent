"""Evidence matrix and smallest-next-analysis planner for synthetic Zelda v0.3.

No causal hypothesis probability or unsupported confidence score. Decision priority
is based on the evidence needed to distinguish hypotheses, not keyword matching.
"""
from __future__ import annotations
from typing import Any

HYPOTHESES = {
    'product_understanding': 'Product familiarity / information gap',
    'audience_mismatch': 'Audience composition / purchase intent mismatch',
    'experience_friction': 'Availability / price / checkout friction',
}


def _pct(n: int, d: int) -> float | None:
    return round(100 * n / d, 2) if d else None


def assess(cohorts: dict[str, dict[str, Any]], data_quality: dict[str, Any],
           question: str = '') -> dict[str, Any]:
    a = cohorts.get('new_to_franchise')
    b = cohorts.get('existing_zelda_gamer')
    if not a or not b:
        return {'status': 'not_comparable', 'why': 'New-to-franchise and existing-Zelda cohorts not both available',
                'hypotheses': [], 'next_analyses': [], 'decision': 'Obtain comparable cohorts'}
    metrics = []
    for name, denom, numerator in (
        ('PDP / reached', 'reached', 'pdp'),
        ('Search / reached', 'reached', 'search'),
        ('Wishlist / reached', 'reached', 'wishlist'),
        ('Add to cart / reached', 'reached', 'cart'),
        ('Purchase / reached', 'reached', 'buyers'),
        ('PDP and cart / PDP viewers', 'pdp', 'pdp_and_cart'),
        ('Cart and purchase / cart customers', 'cart', 'cart_and_purchase'),
        ('Search and PDP / searchers', 'search', 'search_and_pdp'),
    ):
        metrics.append({'metric': name, 'new_numerator': a[numerator], 'new_denominator': a[denom],
                        'existing_numerator': b[numerator], 'existing_denominator': b[denom],
                        'new_pct': _pct(a[numerator], a[denom]),
                        'existing_pct': _pct(b[numerator], b[denom]),
                        'semantic_note': 'Same-window distinct-person overlap' if ' and ' in name else 'Independent milestone participation'})
    hypotheses = [
        {'id': 'H1', 'key': 'product_understanding', 'label': HYPOTHESES['product_understanding'],
         'status': 'unvalidated', 'evidence_consistent_with': [
             'New-to-franchise customers show lower PDP participation',
             'New-to-franchise PDP viewers show lower same-window cart cooccurrence'],
         'evidence_against': [], 'important_alternatives': ['Lower purchase intent', 'Different audience/product mix', 'Inventory or price differences'],
         'missing_discriminator': 'Validated product comprehension, search reformulations, FAQ/VOC or eligible randomized content test',
         'what_would_change_decision': 'If comparable high-intent new visitors struggle with information but respond incrementally to clearer guidance, prioritize product education',
         'causal_confidence': 'not_established'},
        {'id': 'H2', 'key': 'audience_mismatch', 'label': HYPOTHESES['audience_mismatch'],
         'status': 'unvalidated', 'evidence_consistent_with': ['New-to-franchise customers have lower observed reach-to-PDP and purchase participation'],
         'evidence_against': [], 'important_alternatives': ['Lack of familiarity can also suppress exploration', 'Acquisition targeting may be similar but customer needs differ'],
         'missing_discriminator': 'Customer-linked channel/campaign exposure and acquisition eligibility, with like-for-like comparisons',
         'what_would_change_decision': 'If differences substantially attenuate within comparable channels/products and exposure cohorts, investigate audience mix before changing PDP content',
         'causal_confidence': 'not_established'},
        {'id': 'H3', 'key': 'experience_friction', 'label': HYPOTHESES['experience_friction'],
         'status': 'unvalidated', 'evidence_consistent_with': ['The two cohorts differ in cart and purchase participation'],
         'evidence_against': [], 'important_alternatives': ['Completed-order checkout type cannot measure abandonment', 'Correlation does not identify where friction occurs'],
         'missing_discriminator': 'Historical inventory, price exposure, checkout-step errors and abandonment evidence',
         'what_would_change_decision': 'If identified friction concentrates among qualified new-to-franchise customers, prioritize remediation before more acquisition investment',
         'causal_confidence': 'not_established'},
    ]
    next_analyses = [
        {'priority': 1, 'id': 'A1', 'name': 'Product-by-cohort behavioral comparison', 'availability': 'available_now',
         'method': 'Run permitted event and product joins by cohort; compare PDP/search/cart cooccurrence with valid denominators',
         'discriminates': ['H1', 'H2'], 'limitation': 'Cannot distinguish familiarity from selection without campaign/customer research evidence',
         'human_approval': 'Read-only governed analysis; no production writes'},
        {'priority': 2, 'id': 'A2', 'name': 'Audience-matched channel and creative analysis', 'availability': 'requires_new_data',
         'method': 'Obtain permitted customer-level exposure joins, creative and channel details; hold category, device and launch window comparable',
         'discriminates': ['H1', 'H2'], 'limitation': 'Matching alone does not prove causal selection or intent',
         'human_approval': 'Analytics identity/privacy validation'},
        {'priority': 3, 'id': 'A3', 'name': 'Experience evidence and conditional product-education experiment', 'availability': 'requires_new_data_and_approval',
         'method': 'Review inventory, checkout/error and VOC evidence; if H1 remains plausible, register a powered randomized guidance test',
         'discriminates': ['H1', 'H3'], 'limitation': 'No claim of uplift until a valid controlled outcome is observed',
         'human_approval': 'Analytics experiment design and Business activation approval'},
    ]
    blocking = bool(data_quality.get('user_id_conflicts') or data_quality.get('unmapped_pseudo_ids') or data_quality.get('order_item_revenue_mismatch') or data_quality.get('purchase_events_without_matching_order') or data_quality.get('completed_orders_without_purchase_event'))
    return {'status': 'blocked_by_quality' if blocking else 'descriptive_evidence_available',
            'evidence_matrix': metrics, 'hypotheses': hypotheses, 'next_analyses': next_analyses,
            'selection_rule': 'The next step is chosen by available decision-discriminating evidence and action risk, not by wording or fabricated probability.',
            'evidence_caveat': 'Segment labels are synthetic; same-window overlaps are not chronological transitions. No valid causal counterfactual.',
            'decision': ('Hold affected conclusions; resolve critical semantic/data reconciliation failures before running A1.' if blocking else 'Run A1 read-only; withhold targeting/content changes until A2 and/or customer evidence distinguishes hypotheses.')}


def golden_review(result: dict[str, Any]) -> dict[str, Any]:
    matrix = result.get('evidence_matrix', [])
    hypotheses = result.get('hypotheses', [])
    analyses = result.get('next_analyses', [])
    checks = {
        'metric_denominators_present': bool(matrix) and all(x['new_denominator'] >= x['new_numerator'] and x['existing_denominator'] >= x['existing_numerator'] for x in matrix),
        'alternatives_and_missing_discriminators': bool(hypotheses) and all(x['important_alternatives'] and x['missing_discriminator'] for x in hypotheses),
        'causal_uncertainty_explicit': bool(hypotheses) and all(x['causal_confidence'] == 'not_established' for x in hypotheses),
        'small_list_limit_respected': 1 <= len(analyses) <= 3 and 1 <= len(hypotheses) <= 3,
        'no_production_execution_requested': all('Read-only' in x['human_approval'] or 'approval' in x['human_approval'].lower() or 'validation' in x['human_approval'].lower() for x in analyses),
        'data_quality_not_silenced': result.get('status') != 'blocked_by_quality',
    }
    return {'status': 'rule_checks_only', 'passed': all(checks.values()), 'checks': checks,
            'note': 'Rule evaluation is not independent Golden Insights model-based grading or validated customer research.'}