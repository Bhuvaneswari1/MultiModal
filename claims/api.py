"""Local training API. Tokens are workshop controls, not enterprise identity."""
import os, secrets, uuid
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Form, Header, HTTPException, Depends
from pydantic import BaseModel
from langgraph.types import Command
from .core import RUNS
from .agent import build_graph

app=FastAPI(title='Smart Claims Desk - workshop')
graph=build_graph()

def auth(x_api_key:str=Header(default='')):
    if not secrets.compare_digest(x_api_key,os.getenv('APP_API_TOKEN','local-workshop-token')):
        raise HTTPException(401,'Invalid API token')

def reviewer(x_reviewer_token:str=Header(default='')):
    if not secrets.compare_digest(x_reviewer_token,os.getenv('REVIEWER_TOKEN','local-reviewer-token')):
        raise HTTPException(403,'Reviewer token required')

@app.get('/health')
def health(): return {'status':'ok'}

def public(value,thread_id):
    pending=bool(value.get('__interrupt__'))
    return {'thread_id':thread_id,'pending_review':pending,
            'decision':'pending_review' if pending else value.get('decision'),
            'route':value.get('route'),'flags':value.get('flags',[]),
            'reply':value.get('reply'), 'warranty':value.get('warranty'),
            'observations':value.get('observations',[])}

@app.post('/claims',dependencies=[Depends(auth)])
def submit(files:list[UploadFile]=File(...),product:str=Form('router'),
           amount:float=Form(2360,gt=0),delivery_days:int=Form(2,ge=0)):
    if product not in ('router','phone','monitor'): raise HTTPException(422,'Unknown product')
    if not 1<=len(files)<=4: raise HTTPException(422,'Upload 1-4 files')
    tid=str(uuid.uuid4()); folder=RUNS/'uploads'/tid; folder.mkdir(parents=True)
    paths=[]
    try:
        for i,f in enumerate(files):
            suffix=Path(f.filename or '').suffix.lower()
            if suffix not in ('.png','.jpg','.jpeg','.pdf','.wav','.mp3','.m4a','.mp4'):
                raise HTTPException(415,'Unsupported extension')
            data=f.file.read(20*1024*1024+1)
            if len(data)>20*1024*1024: raise HTTPException(413,'20 MB per file maximum')
            p=folder/f'{i}{suffix}'; p.write_bytes(data); paths.append(str(p))
        value=graph.invoke({'files':paths,'product':product,'amount':amount,'delivery_days':delivery_days},
                           {'configurable':{'thread_id':tid}})
        return public(value,tid)
    except HTTPException: raise
    except (ValueError,RuntimeError) as e: raise HTTPException(422,str(e)) from e

class Approval(BaseModel):
    decision:str
    reviewer:str

@app.post('/claims/{thread_id}/review',dependencies=[Depends(auth),Depends(reviewer)])
def review(thread_id:str,body:Approval):
    if body.decision not in ('approve','reject') or not body.reviewer.strip(): raise HTTPException(422,'Invalid review')
    cfg={'configurable':{'thread_id':thread_id}}
    state=graph.get_state(cfg)
    if not state.next or state.next!=('review',): raise HTTPException(409,'No pending review')
    return public(graph.invoke(Command(resume=body.model_dump()),cfg),thread_id)
