import base64, json, os, time
from pathlib import Path
import requests
from .core import Damage, extract, fixture_record, mode, image_url, rows, DATA

def analyze(path, provider='cloud'):
    if mode() == 'demo':
        r = fixture_record('photo_labels.csv',path)
        return Damage.model_validate({k:r[k] or None for k in Damage.model_fields})
    prompt = ('Extract product, damage_type, severity, visible_serial and confidence. '
              'Use null for unreadable product/serial, unknown for unclear damage/severity. '
              'A dented package is not evidence that the product is damaged.')
    if provider == 'cloud': return extract(Damage,prompt,[path])
    if provider != 'ollama': raise ValueError('provider must be cloud or ollama')
    response = requests.post(os.getenv('OLLAMA_URL','http://localhost:11434')+'/api/chat',
        json={'model':os.getenv('OLLAMA_MODEL','gemma3:4b'),'stream':False,
              'format':Damage.model_json_schema(), 'messages':[{'role':'user','content':prompt,
                 'images':[image_url(path).split(',',1)[1]]}]}, timeout=180)
    response.raise_for_status()
    return Damage.model_validate_json(response.json()['message']['content'])

def compare():
    report=[]
    for r in rows('photo_labels.csv'):
        for provider in ['cloud','ollama']:
            start=time.perf_counter()
            try:
                value=analyze(DATA/r['path'],provider)
                report.append({'path':r['path'],'provider':provider,'mode':mode(),
                    'seconds':time.perf_counter()-start,'damage_correct':value.damage_type==r['damage_type'],
                    'result':value.model_dump(),'note':'fixture replay; no inference/cost comparison' if mode()=='demo' else 'See usage.jsonl for cloud tokens; local API has no token bill'})
            except Exception as e: report.append({'path':r['path'],'provider':provider,'error':str(e)})
    return report
