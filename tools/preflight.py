import importlib, os, shutil, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from claims.core import DATA, mode
failures=[]
print('Python:',sys.version,'mode:',mode())
for name in ['openai','pydantic','PIL','pymupdf','cv2','langgraph','langgraph.checkpoint.sqlite','langsmith','fastapi','streamlit','jiwer']:
    try: importlib.import_module(name); print('OK',name)
    except ImportError: failures.append(name); print('MISSING',name)
for tool in ['ffmpeg','tesseract']: print(tool,shutil.which(tool) or 'MISSING (needed for video/OCR labs)')
for name in ['input_claims.csv','eval_set.csv','voice_notes/voice_01.wav','unboxing_videos/unboxing_01.mp4']:
    if not (DATA/name).exists(): failures.append(name)
if mode()=='live' and not os.getenv('OPENAI_API_KEY'): failures.append('OPENAI_API_KEY')
print('API key present:',bool(os.getenv('OPENAI_API_KEY')),'(value never printed)')
if failures: raise SystemExit('Fix: '+', '.join(failures))
print('Core preflight passed. Check optional system tools before corresponding labs.')
