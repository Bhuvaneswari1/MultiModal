import argparse, json, uuid
from .core import DATA, RUNS, mode, rows, save

def main():
    p=argparse.ArgumentParser(description='Run workshop labs from project root')
    p.add_argument('lab',choices=['vision','compare','documents','rag','chart','clip-text','clip-image','audio','tts','video','generate','edit','agent','evaluate','guardrails','prompts','table'])
    p.add_argument('--path'); p.add_argument('--query',default='Is a cracked case covered?')
    p.add_argument('--voice',default='alloy'); p.add_argument('--speed',type=float,default=1)
    a=p.parse_args()
    if a.lab in ('vision','compare'):
        from .vision import analyze, compare
        value=compare() if a.lab=='compare' else [analyze(DATA/r['path']).model_dump() for r in rows('photo_labels.csv')]
    elif a.lab in ('documents','rag','chart','clip-text','clip-image','table'):
        from .documents import invoice, rag, chart_qa, clip_search
        if a.lab=='documents': value=[invoice(DATA/r['path']) for r in rows('invoice_labels.csv')]
        elif a.lab=='rag': value=rag(a.query)
        elif a.lab=='chart': value=chart_qa()
        elif a.lab=='table':
            from .labs import table_qa
            value=table_qa()
        else: value=clip_search(a.path if a.lab=='clip-image' else a.query,image=a.lab=='clip-image')
    elif a.lab in ('audio','tts','video','generate','edit'):
        from .media import transcribe, ticket, speak, video, visual
        if a.lab=='audio':
            value=[{'path':r['path'],'transcript':(text:=transcribe(DATA/r['path'])),'ticket':ticket(text).model_dump()} for r in rows('voice_labels.csv')]
        elif a.lab=='tts': value=speak('Please pack your router safely and include the invoice.',RUNS/f'reply_{a.voice}_{a.speed}.wav',a.voice,a.speed)
        elif a.lab=='video': value=video(a.path or DATA/'unboxing_videos/unboxing_01.mp4')
        else: value=visual(a.path if a.lab=='edit' else None)
    elif a.lab=='agent':
        from .agent import build_graph
        value=build_graph().invoke({'files':[str(DATA/'claim_photos/claim_01.png'),str(DATA/'invoices/invoice_01.pdf'),str(DATA/'voice_notes/voice_01.wav')],
                'product':'router','amount':2360,'delivery_days':2},{'configurable':{'thread_id':str(uuid.uuid4())}})
    elif a.lab=='evaluate':
        from .evaluation import evaluate
        value=evaluate()
    elif a.lab=='prompts':
        from .labs import prompts
        value=prompts()
    else:
        from .safety import sanitize_image
        value=sanitize_image(a.path or DATA/'guardrails/injection.png',RUNS/'sanitized.png')
    print(json.dumps(value,ensure_ascii=False,indent=2,default=str))
    print('Saved:',save(a.lab+'.json',{'mode':mode(),'result':value}))

if __name__=='__main__': main()
