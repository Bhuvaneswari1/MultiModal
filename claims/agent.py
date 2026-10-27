"""LangGraph routing with durable SQLite checkpoints and human interruption."""
from __future__ import annotations
import json, sqlite3
from pathlib import Path
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt
from langgraph.checkpoint.sqlite import SqliteSaver
from .core import RUNS, mode
from .vision import analyze
from .documents import invoice, rag
from .media import transcribe, ticket, video
from .safety import inspect_text, sanitize_image

class State(TypedDict, total=False):
    files:list[str]
    product:str
    amount:float
    delivery_days:int
    observations:list[dict]
    warranty:dict
    flags:list[str]
    decision:str
    route:str
    reviewer:str
    reply:str

def inspect_files(state):
    observations=[]; flags=[]
    for name in state['files']:
        p=Path(name); suffix=p.suffix.lower()
        if suffix in ('.png','.jpg','.jpeg'):
            # Originals are retained locally, never silently replaced or sent into traces.
            # For live image uploads, sanitize BEFORE sending to the vision service.
            if mode()=='live':
                target=RUNS/('safe_'+p.stem+'.png'); result=sanitize_image(p,target)
                if result['injection_suspected']: flags.append('suspected_injection')
                value=analyze(target).model_dump()
            else: value=analyze(p).model_dump()
            observations.append({'kind':'photo','result':value})
        elif suffix=='.pdf': observations.append({'kind':'invoice','result':invoice(p)})
        elif suffix in ('.wav','.mp3','.m4a'):
            text=transcribe(p); safe=inspect_text(text)
            if safe['injection_suspected']: flags.append('suspected_injection')
            observations.append({'kind':'voice','result':ticket(safe['masked_text']).model_dump()})
        elif suffix=='.mp4': observations.append({'kind':'video','result':video(p)})
        else: raise ValueError(f'Unsupported file type: {suffix}')
    if not observations: raise ValueError('Supply at least one media file')
    return {'observations':observations,'flags':flags}

def policy(state):
    # Policy is deterministic; retrieval supplies supporting citations, never executable rules.
    evidence=rag('Is a cracked case or broken screen on delivery covered within 7 days?',state['product'])
    return {'warranty':evidence}

def decide(state):
    obs=state['observations']
    photos=[o['result'] for o in obs if o['kind']=='photo']
    invoices=[o['result'] for o in obs if o['kind']=='invoice']
    flags=list(state.get('flags',[]))
    if any(not i['totals_valid'] for i in invoices): flags.append('invoice_total_mismatch')
    if invoices and abs(invoices[0]['invoice']['total']-state['amount'])>0.01: flags.append('amount_mismatch')
    if len(invoices)>1: flags.append('multiple_invoices')
    if any(not any(state['product'].lower() in item['description'].lower() for item in i['invoice']['items']) for i in invoices):
        flags.append('invoice_product_mismatch')
    if any(p['confidence']<0.7 or p['damage_type']=='unknown' for p in photos): flags.append('uncertain_photo')
    damaged=any(p['damage_type'] in ('cracked_case','broken_screen') for p in photos)
    if not photos or not invoices or not state['warranty']['citations']: flags.append('missing_evidence')
    if any(p['product']!=state['product'] for p in photos): flags.append('product_mismatch')
    if flags: decision='review'
    elif state['delivery_days']>7: decision='reject'
    elif damaged: decision='approve'
    else: decision='reject'
    # High value approval AND uncertain claims go through a real interrupt.
    route='human' if decision=='review' or (decision=='approve' and state['amount']>5000) else 'automatic'
    return {'decision':decision,'route':route,'flags':flags}

def review(state):
    response=interrupt({'decision':state['decision'],'amount':state['amount'],'flags':state['flags'],
                        'allowed':['approve','reject'],'message':'Authorized reviewer must decide.'})
    if not isinstance(response,dict) or response.get('decision') not in ('approve','reject') or not response.get('reviewer'):
        raise ValueError('Review requires decision approve/reject and reviewer identity')
    return {'decision':response['decision'],'reviewer':response['reviewer']}

def reply(state):
    status={'approve':'approved','reject':'rejected','review':'awaiting review'}[state['decision']]
    return {'reply':f"Your fictional training claim is {status}. "
            'This is a draft for support review; no refund has been issued. '
            + 'Sources: '+', '.join(c['id'] for c in state['warranty']['citations'])}

def build_graph(database=None):
    connection=sqlite3.connect(str(database or RUNS/'checkpoints.sqlite'),check_same_thread=False)
    graph=StateGraph(State)
    for name,fn in [('inspect',inspect_files),('policy',policy),('decide',decide),('review',review),('reply',reply)]: graph.add_node(name,fn)
    graph.add_edge(START,'inspect'); graph.add_edge('inspect','policy'); graph.add_edge('policy','decide')
    graph.add_conditional_edges('decide',lambda s:'review' if s['route']=='human' else 'reply')
    graph.add_edge('review','reply'); graph.add_edge('reply',END)
    return graph.compile(checkpointer=SqliteSaver(connection))
