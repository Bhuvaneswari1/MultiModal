"""Evaluate predictions against separate answer-key CSVs; demo is wiring-only."""
import json, tempfile, uuid
from pathlib import Path
from jiwer import wer, cer
from .core import DATA, RUNS, mode, rows, save
from .vision import analyze
from .media import transcribe
from .documents import retrieve
from .agent import build_graph

def evaluate():
    from .metrics import macro_f1
    details=[]; field_hits=0; decision_hits=0; route_hits=0; retrieval_hits=0
    # No human resume: evaluate pre-review proposal, not a fictitious final decision.
    with tempfile.TemporaryDirectory() as folder:
        graph=build_graph(Path(folder)/'eval.sqlite')
        for r in rows('eval_set.csv'):
            photo=analyze(DATA/r['photo'])
            field_hits+=sum([photo.damage_type==r['expected_damage_type'],photo.severity==r['expected_severity']])
            cfg={'configurable':{'thread_id':str(uuid.uuid4())}}
            predicted=graph.invoke({'files':[str(DATA/r['photo']),str(DATA/r['invoice']),str(DATA/r['voice'])],
                'product':r['product'],'amount':float(r['amount']),'delivery_days':int(r['delivery_days'])},cfg)
            dh=predicted['decision']==r['expected_decision']; rh=predicted['route']==r['expected_route']
            decision_hits+=dh; route_hits+=rh
            citations=retrieve(r['query'],5,r['product'])
            retrieval_hits+=r['relevant_page'] in [d['id'] for d in citations]
            details.append({'claim_id':r['claim_id'],'damage_prediction':photo.model_dump(),
                'proposed_decision':predicted['decision'],'route':predicted['route'],'decision_correct':dh,'route_correct':rh,
                'pending':bool(predicted.get('__interrupt__'))})
    voice=[]
    for r in rows('voice_labels.csv'):
        hypothesis=transcribe(DATA/r['path'])
        voice.append({'language':r['language'],'path':r['path'],'hypothesis':hypothesis,
            'wer':wer(r['transcript'],hypothesis),'cer':cer(r['transcript'],hypothesis)})
    n=len(details)
    report={'mode':mode(),'interpretation':'Fixture wiring only; not model quality' if mode()=='demo' else 'Live predictions on synthetic teaching data',
        'claims':n,'field_accuracy':field_hits/(n*2),'decision_accuracy':decision_hits/n,'route_accuracy':route_hits/n,
        'damage_macro_f1':macro_f1([r['expected_damage_type'] for r in rows('eval_set.csv')],[d['damage_prediction']['damage_type'] for d in details]),
        'recall_at_5':retrieval_hits/n,'retrieval_note':'Tiny two-page/product corpus makes recall@5 trivial; expand corpus for meaningful retrieval evaluation.',
        'voice_scores':voice,'details':details,
        'judge_note':'Run python -m claims.judge separately in live mode for groundedness. CLIPScore requires the optional CLIP lab.'}
    save('evaluation_report.json',report); return report
