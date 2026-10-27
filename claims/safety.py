"""Workshop guardrails: deliberately limited heuristics, never a security guarantee."""
import re
from pathlib import Path

def inspect_text(text):
    injection=bool(re.search(r'ignore.{0,30}instructions|system prompt|approve all|bypass.{0,20}policy',text,re.I))
    masked=re.sub(r'(?<!\d)(?:\+91[ -]?)?[6-9]\d{9}(?!\d)','[PHONE]',text)
    return {'masked_text':masked,'injection_suspected':injection}

def sanitize_image(path, dest):
    import cv2, pytesseract
    im=cv2.imread(str(path))
    if im is None: raise ValueError('Unreadable image')
    gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    detector=cv2.CascadeClassifier(cv2.data.haarcascades+'haarcascade_frontalface_default.xml')
    faces=detector.detectMultiScale(gray,1.1,4)
    for x,y,w,h in faces:
        im[y:y+h,x:x+w]=cv2.GaussianBlur(im[y:y+h,x:x+w],(51,51),0)
    data=pytesseract.image_to_data(im,output_type=pytesseract.Output.DICT)
    text=' '.join(data['text'])
    for i,word in enumerate(data['text']):
        if re.search(r'\d{10}',word):
            x,y,w,h=(data[k][i] for k in ('left','top','width','height'))
            cv2.rectangle(im,(x,y),(x+w,y+h),(0,0,0),-1)
    cv2.imwrite(str(dest),im)
    return {'path':str(dest),'face_count':len(faces),**inspect_text(text),
            'limitation':'OCR misses handwriting, spaced phone digits and obfuscated injection; face detector can miss faces. Use fictional data only.'}
