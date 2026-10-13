"""Read-only semantic metrics for the SYNTHETIC Zelda/Switch 2 fixtures.

Run: python semantic_launch.py --data-dir /path/to/unzipped/csvs
No AI-generated SQL or live production connectors. Definitions are explicit and versioned.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from datetime import date
import json
from pathlib import Path
import re
from typing import Any

SCHEMA_VERSION = 'launch-semantic-v0.1'
EVENT_MAP = {'reached': 'session_start', 'pdp_viewers': 'view_item',
             'wishlist_customers': 'add_to_wishlist', 'cart_customers': 'add_to_cart',
             'search_customers': 'search', 'promo_click_customers': 'select_promotion',
             'purchase_event_customers': 'purchase'}
PSEUDO_RE = re.compile(r'^P(\d{5})_\d+$')
FILES = {'launches': ('launch_id','launch_date','window_end'),
         'segments': ('launch_id','customer_key','primary_segment'),
         'events': ('launch_id','event_timestamp','event_name','user_pseudo_id','user_id','product_id','transaction_id'),
         'orders': ('launch_id','order_id','transaction_id','customer_key','order_status','net_revenue_usd','checkout_type'),
         'order_items': ('launch_id','order_id','product_id','quantity','line_revenue_usd'),
         'products': ('launch_id','product_id','item_name')}
FILENAME = {'launches': 'launches.csv','segments':'customer_launch_segments.csv',
            'events':'ga4_events.csv','orders':'orders.csv','order_items':'order_items.csv',
            'products':'products.csv'}


def read_table(folder: Path, name: str) -> list[dict[str,str]]:
    path = folder / FILENAME[name]
    with path.open(encoding='utf-8-sig',newline='') as fd:
        reader = csv.DictReader(fd)
        missing = set(FILES[name]) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f'{path.name}: missing {sorted(missing)}')
        return list(reader)


def synthetic_identity(event: dict[str,str]) -> str | None:
    """FIXTURE-ONLY identity rule; never apply to real GA4 without approval."""
    match = PSEUDO_RE.fullmatch(event['user_pseudo_id'])
    return 'C' + match.group(1) if match else None


def run(data_dir: str | Path, launch_id: str, segment: str='ALL') -> dict[str,Any]:
    folder=Path(data_dir)
    tables={k:read_table(folder,k) for k in FILES}
    launches={r['launch_id']:r for r in tables['launches']}
    if launch_id not in launches: raise ValueError('Unknown launch_id')
    launch=launches[launch_id]
    from_date=date.fromisoformat(launch['launch_date'])
    through_date=date.fromisoformat(launch['window_end'])
    if (through_date-from_date).days != 13:
        raise ValueError('Fixture contract expects inclusive launch days 0-13')
    segment_rows=[r for r in tables['segments'] if r['launch_id']==launch_id]
    segment_by_customer={r['customer_key']:r['primary_segment'] for r in segment_rows}
    if len(segment_by_customer)!=len(segment_rows): raise ValueError('Duplicate launch/customer segment assignment')
    known_segments=set(segment_by_customer.values())
    if segment!='ALL' and segment not in known_segments: raise ValueError('Unknown customer segment')
    eligible=lambda customer: customer in segment_by_customer and (segment=='ALL' or segment_by_customer[customer]==segment)

    users_by_event:dict[str,set[str]]=defaultdict(set)
    by_product:dict[str,dict[str,set[str]]]=defaultdict(lambda:defaultdict(set))
    event_transactions=set()
    quality=Counter()
    all_launch_events=0
    for e in tables['events']:
        if e['launch_id']!=launch_id: continue
        if not from_date <= date.fromisoformat(e['event_timestamp'][:10]) <= through_date: continue
        all_launch_events+=1
        person=synthetic_identity(e)
        if not person: quality['unmapped_pseudo_ids']+=1;continue
        if person not in segment_by_customer: quality['missing_segment_assignments']+=1;continue
        if e['user_id'] and e['user_id']!='U'+person[1:]:quality['user_id_conflicts']+=1
        if not eligible(person):continue
        users_by_event[e['event_name']].add(person)
        if e['product_id']:
            by_product[e['product_id']][e['event_name']].add(person)
        if e['event_name']=='purchase' and e['transaction_id']:
            event_transactions.add(e['transaction_id'])

    orders=[r for r in tables['orders'] if r['launch_id']==launch_id and r['order_status']=='completed' and eligible(r['customer_key'])]
    orderids=set()
    transactions=set()
    for o in orders:
        if o['order_id'] in orderids:quality['duplicate_order_ids']+=1
        if o['transaction_id'] in transactions:quality['duplicate_transaction_ids']+=1
        orderids.add(o['order_id']);transactions.add(o['transaction_id'])
    purchased={o['customer_key'] for o in orders}
    order_revenue=round(sum(float(o['net_revenue_usd']) for o in orders),2)
    checkout=Counter(o['checkout_type'] for o in orders)
    itemrows=[r for r in tables['order_items'] if r['launch_id']==launch_id and r['order_id'] in orderids]
    item_rev=round(sum(float(x['line_revenue_usd']) for x in itemrows),2)
    if abs(item_rev-order_revenue)>0.01:quality['order_item_revenue_mismatch']=1
    product_meta={r['product_id']:r['item_name'] for r in tables['products'] if r['launch_id']==launch_id}
    products=[{'product_id':pid,'item_name':name,'pdp_view_customers':len(by_product[pid]['view_item']),
               'cart_customers':len(by_product[pid]['add_to_cart']),
               'units_sold':sum(int(x['quantity']) for x in itemrows if x['product_id']==pid)}
              for pid,name in product_meta.items()]
    segments=[]
    for seg in sorted(known_segments):
        if segment!='ALL' and seg!=segment:continue
        subset={c for c,s in segment_by_customer.items() if s==seg}
        reached=len(subset & users_by_event['session_start'])
        seg_buyers=len(subset & purchased)
        segments.append({'segment':seg,'reached':reached,'buyers':seg_buyers,
                         'purchase_per_reached':round(seg_buyers/reached,6) if reached else None,
                         'validation':'scenario_assigned_unverified'})
    reached=len(users_by_event['session_start'])
    result={'semantic_version':SCHEMA_VERSION,'source_type':'synthetic_fixture_only','launch_id':launch_id,
            'launch_start':str(from_date),'launch_end':str(through_date),'segment_filter':segment,
            'metrics':{**{name:len(users_by_event[event]) for name,event in EVENT_MAP.items()},
                       'purchasing_customers':len(purchased),'completed_orders':len(orders),
                       'net_order_revenue_usd':order_revenue,'purchase_per_reached':round(len(purchased)/reached,6) if reached else None,
                       'checkout_types':dict(checkout)},
            'customer_segments':segments,'products':products,
            'evidence':{'sources':list(FILENAME.values()),'grain':'distinct synthetic customer_key x launch x event (except orders)',
                        'identity':'fixture-only pseudo-ID prefix; NOT a general identity resolution method',
                        'definitions':{'reached':'distinct linked customer_key with session_start',
                                       'purchase_per_reached':'distinct customers with completed orders / reached customers',
                                       'revenue':'sum completed order net_revenue_usd'},
                        'observation':'inclusive launch days 0-13','causal_claims_permitted':False},
            'quality':{'events_in_window':all_launch_events,'unmapped_pseudo_ids':quality['unmapped_pseudo_ids'],
                       'missing_segment_assignments':quality['missing_segment_assignments'],
                       'user_id_conflicts':quality['user_id_conflicts'],
                       'duplicate_order_ids':quality['duplicate_order_ids'],
                       'duplicate_transaction_ids':quality['duplicate_transaction_ids'],
                       'order_item_revenue_mismatch':bool(quality['order_item_revenue_mismatch']),
                       'purchase_events_without_matching_order':len(event_transactions-transactions) if segment=='ALL' else None,
                       'completed_orders_without_purchase_event':len(transactions-event_transactions) if segment=='ALL' else None}}
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--data-dir',required=True,help='Directory containing unzipped synthetic CSVs')
    ap.add_argument('--launch-id',default='ZELDA_2026')
    ap.add_argument('--segment',default='ALL')
    args=ap.parse_args()
    print(json.dumps(run(args.data_dir,args.launch_id,args.segment),indent=2))


if __name__=='__main__':main()