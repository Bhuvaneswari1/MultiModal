from pathlib import Path
import json, re, tempfile
from .core import DATA, Invoice, extract, fixture_record, mode, rows

def pdf_pages(path, folder):
    import fitz
    result=[]
    with fitz.open(path) as doc:
        if len(doc)>10: raise ValueError('Workshop limit: 10 PDF pages')
        for i,page in enumerate(doc):
            p=Path(folder)/f'page_{i+1}.png'; page.get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(p)
            result.append(p)
    return result

def invoice(path):
    if mode()=='demo':
        r=fixture_record('invoice_labels.csv',path)
        value=Invoice.model_validate_json(r['expected_json'])
    else:
        with tempfile.TemporaryDirectory() as folder:
            value=extract(Invoice,'Read all invoice fields. GST is total tax amount, not tax rate.',pdf_pages(path,folder))
    return {'invoice':value.model_dump(),'totals_valid':value.totals_valid()}

def ocr(path):
    import pytesseract
    from PIL import Image
    with tempfile.TemporaryDirectory() as folder:
        return '\n'.join(pytesseract.image_to_string(Image.open(p)) for p in pdf_pages(path,folder))

def retrieve(question, k=5, product=None):
    # Small transparent lexical baseline; CLIP search is a separate actual embedding lab.
    tokens=set(re.findall(r'\w+',question.lower()))
    docs=json.loads((DATA/'manual_pages.json').read_text())
    if product: docs=[d for d in docs if d['product']==product]
    return sorted(docs,key=lambda d:len(tokens & set(re.findall(r'\w+',d['text'].lower()))),reverse=True)[:k]

def rag(question, product='router'):
    docs=retrieve(question,product=product)
    if not docs: return {'answer':'Insufficient evidence','citations':[]}
    if mode()=='demo': answer=docs[0]['text']; docs=docs[:1]
    else:
        from pydantic import BaseModel
        class Answer(BaseModel):
            answer: str
            citation_ids: list[str]
        value=extract(Answer,'Answer only from these pages; cite IDs; abstain if absent. Question: '+question+'\n'+json.dumps(docs))
        allowed={d['id'] for d in docs}
        if not set(value.citation_ids)<=allowed: raise ValueError('Invalid citation from model')
        docs=[d for d in docs if d['id'] in value.citation_ids]; answer=value.answer
    return {'answer':answer,'citations':[{'id':d['id'],'file':d['file'],'page':d['page'],'figure':d['figure']} for d in docs]}

def chart_qa():
    source=rows('returns_by_month.csv')
    expected=max(source,key=lambda r:int(r['returns']))
    if mode()=='demo': result={'month':expected['month'],'returns':int(expected['returns'])}
    else:
        from pydantic import BaseModel
        class ChartAnswer(BaseModel):
            month:str
            returns:int
        result=extract(ChartAnswer,'Which month has the most returns?', [DATA/'charts/returns.png']).model_dump()
    return {'prediction':result,'expected':expected,'correct':result['month']==expected['month'] and result['returns']==int(expected['returns'])}

def clip_search(query, image=False):
    from sentence_transformers import SentenceTransformer
    import chromadb
    from PIL import Image
    model=SentenceTransformer('clip-ViT-B-32')
    catalog=rows('product_catalog.csv')
    db=chromadb.PersistentClient(path=str(DATA.parent/'.chroma'))
    collection=db.get_or_create_collection('products',metadata={'hnsw:space':'cosine'})
    ids=[r['id'] for r in catalog]
    if collection.count()!=len(ids):
        embeddings=[]
        for r in catalog:
            with Image.open(DATA/r['path']) as im: embeddings.append(model.encode(im.convert('RGB')).tolist())
        collection.upsert(ids=ids,embeddings=embeddings,metadatas=catalog)
    if image:
        with Image.open(query) as im: vector=model.encode(im.convert('RGB')).tolist()
    else: vector=model.encode(query).tolist()
    return collection.query(query_embeddings=[vector],n_results=5)
