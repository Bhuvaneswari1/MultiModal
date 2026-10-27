"""Actual caption-then-embed multimodal RAG, separate from lexical classroom baseline.
Install requirements-clip.txt (Chroma); requires API key and APP_MODE=live.
"""
import argparse, json, os, tempfile
from pathlib import Path
from pydantic import BaseModel
from .core import DATA, ROOT, client, extract, mode, save
from .documents import pdf_pages

class Caption(BaseModel):
    text:str
    diagram_description:str

def collection():
    import chromadb
    return chromadb.PersistentClient(path=str(ROOT/'.chroma')).get_or_create_collection('manual_pages')

def index():
    if mode()!='live': raise ValueError('Caption-embedding lab requires live mode')
    import fitz
    records=[]
    for file in sorted((DATA/'manuals').glob('*.pdf')):
        with tempfile.TemporaryDirectory() as folder, fitz.open(file) as pdf:
            for i,image in enumerate(pdf_pages(file,folder)):
                cap=extract(Caption,'Transcribe policy text and describe the diagram; include figure label. Evidence only.',[image])
                records.append({'id':f'{file.stem}-p{i+1}','text':pdf[i].get_text()+'\n'+cap.text+'\n'+cap.diagram_description,
                    'file':str(file.relative_to(DATA)),'page':i+1,'figure':f'Figure {i+1}'})
    vectors=client().embeddings.create(model=os.getenv('EMBEDDING_MODEL','text-embedding-3-small'),input=[r['text'] for r in records]).data
    collection().upsert(ids=[r['id'] for r in records],documents=[r['text'] for r in records],
        embeddings=[v.embedding for v in vectors],metadatas=[{k:r[k] for k in ('file','page','figure')} for r in records])
    return {'indexed_pages':len(records),'pattern':'page text + VLM diagram caption → text embeddings → Chroma'}

def answer(question):
    if mode()!='live': raise ValueError('Embedding RAG requires live mode')
    col=collection()
    if col.count()==0: raise ValueError('Run index first')
    vector=client().embeddings.create(model=os.getenv('EMBEDDING_MODEL','text-embedding-3-small'),input=question).data[0].embedding
    result=col.query(query_embeddings=[vector],n_results=min(5,col.count()))
    docs=[{'id':i,'text':t,**m} for i,t,m in zip(result['ids'][0],result['documents'][0],result['metadatas'][0])]
    class Answer(BaseModel):
        answer:str
        citation_ids:list[str]
    response=extract(Answer,'Answer only from evidence. Abstain if absent. '+json.dumps({'question':question,'pages':docs}))
    if not set(response.citation_ids)<={d['id'] for d in docs}: raise ValueError('Fabricated citation ID')
    return {'answer':response.answer,'citations':[d for d in docs if d['id'] in response.citation_ids]}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['index','ask']);p.add_argument('--query',default='Is a cracked case covered?')
    a=p.parse_args();print(save('embedding_rag.json',index() if a.action=='index' else answer(a.query)))
