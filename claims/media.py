import base64, json, os, re, subprocess, tempfile
from pathlib import Path
from .core import DATA, RUNS, Ticket, Damage, client, extract, fixture_record, mode

def transcribe(path):
    if mode()=='demo': return fixture_record('voice_labels.csv',path)['transcript']
    with open(path,'rb') as f:
        return client().audio.transcriptions.create(model=os.getenv('ASR_MODEL','whisper-1'),file=f).text

def ticket(text):
    if mode()=='live': return extract(Ticket,'Extract complaint, order ID and sentiment from this evidence: '+text)
    match=re.search(r'ORD-\d+',text)
    return Ticket(complaint=text,order_id=match.group(0) if match else None,sentiment='negative')

def speak(text, target, voice='alloy', speed=1.0):
    if mode()=='demo':
        # A bundled fixture, explicitly not speech generated from the supplied text.
        import shutil
        shutil.copyfile(DATA/'voice_notes/reply.wav',target)
        return {'path':str(target),'note':'Bundled fixed demo reply; live mode speaks supplied text'}
    with client().audio.speech.with_streaming_response.create(model=os.getenv('TTS_MODEL','tts-1'),
            voice=voice,input=text,speed=speed,response_format='wav') as response:
        response.stream_to_file(target)
    return {'path':str(target),'voice':voice,'speed':speed}

def video(path):
    import cv2
    cap=cv2.VideoCapture(str(path)); fps=cap.get(cv2.CAP_PROP_FPS); count=cap.get(cv2.CAP_PROP_FRAME_COUNT)
    if not cap.isOpened() or fps<=0: raise ValueError('Unreadable video')
    if count/fps>30: cap.release(); raise ValueError('Workshop limit: 30 second video')
    timeline=[]
    try:
        if mode()=='demo': fixture=fixture_record('video_labels.csv',path)
        with tempfile.TemporaryDirectory() as folder:
            for second in range(0,max(1,int(count/fps)),5):
                cap.set(cv2.CAP_PROP_POS_MSEC,second*1000); ok,frame=cap.read()
                if not ok: continue
                p=Path(folder)/f'{second}.jpg'; cv2.imwrite(str(p),frame)
                if mode()=='demo':
                    observation='Sealed package' if second<5 else 'Product crack visible in synthetic animation'
                else: observation=extract(Damage,'Describe visible product damage in this frame.',[p]).model_dump()
                timeline.append({'second':second,'observation':observation})
            wav=Path(folder)/'sound.wav'
            subprocess.run(['ffmpeg','-y','-i',str(path),'-vn','-ar','16000','-ac','1',str(wav)],check=True,capture_output=True)
            transcript=fixture['transcript'] if mode()=='demo' else transcribe(wav)
    finally: cap.release()
    return {'timeline':timeline,'transcript':transcript,'summary':ticket(transcript).model_dump(),
            'limitation':'Sampled frames can miss brief events; no causal proof of shipping damage.'}

def visual(edit=None):
    if mode()=='demo':
        import shutil
        dest=RUNS/('edited_background.png' if edit else 'packing_guide.png')
        shutil.copyfile(DATA/'charts/packing_guide.png',dest)
        return {'path':str(dest),'note':'Static illustration fixture; no image generation or editing performed'}
    c=client(); model=os.getenv('IMAGE_MODEL','gpt-image-1')
    if edit:
        with open(edit,'rb') as f:
            result=c.images.edit(model=model,image=f,prompt='Replace only background with neutral white. Preserve damage and product markings.')
    else:
        result=c.images.generate(model=model,prompt='A clear three-step return packing illustration: protect device, cushion in box, seal. No logos, people or text.',size='1024x1024')
    dest=RUNS/('edited_background.png' if edit else 'packing_guide.png')
    dest.write_bytes(base64.b64decode(result.data[0].b64_json)); return {'path':str(dest),'review':'Check preservation of damage, safe packing, brand neutrality and legibility before use.'}
