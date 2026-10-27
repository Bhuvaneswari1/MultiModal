"""Consume the actual input-only CSV and run each claim through the graph."""
import argparse,csv,json,sys,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from claims.core import DATA, save, mode
from claims.agent import build_graph

p=argparse.ArgumentParser();p.add_argument('--csv',default=str(DATA/'input_claims.csv'));a=p.parse_args()
graph=build_graph();results=[]
with open(a.csv,encoding='utf-8',newline='') as f:
    for r in csv.DictReader(f):
        cfg={'configurable':{'thread_id':str(uuid.uuid4())}}
        files=[str(DATA/r[k]) for k in ('photo','invoice','voice','video') if r.get(k)]
        state=graph.invoke({'files':files,'product':r['product'],'amount':float(r['amount']),'delivery_days':int(r['delivery_days'])},cfg)
        results.append({'claim_id':r['claim_id'],'thread_id':cfg['configurable']['thread_id'],
            'pending_review':bool(state.get('__interrupt__')),'proposed_decision':state['decision'],'route':state['route'],'flags':state['flags']})
print(save('batch_results.json',{'mode':mode(),'results':results}))
