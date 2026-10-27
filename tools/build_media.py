"""Regenerate bundled speech and animated unboxing fixtures.
python tools/build_media.py --ffmpeg /path/to/ffmpeg
Default gTTS engine sends fictional text to Google Translate TTS (network required).
Use --engine say for installed macOS voices; empty output is rejected.
These are synthesized voices and animated illustrations, never real customer evidence.
"""
import argparse, csv, shutil, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'

def run():
    p=argparse.ArgumentParser();p.add_argument('--ffmpeg',default='ffmpeg');p.add_argument('--engine',choices=['gtts','say'],default='gtts');a=p.parse_args()
    with (DATA/'voice_labels.csv').open() as f: voices=list(csv.DictReader(f))
    if a.engine=='say' and not shutil.which('say'): raise SystemExit('macOS say required for this engine. Use gtts or bundled assets.')
    def speech(text,lang,target,folder):
        source=Path(folder)/('speech.mp3' if a.engine=='gtts' else 'speech.aiff')
        if a.engine=='gtts':
            from gtts import gTTS
            gTTS(text,lang=lang,timeout=30).save(str(source))
        else:
            if lang=='te': raise ValueError('Use --engine gtts for Telugu speech generation')
            subprocess.run(['say','-v',{'en':'Samantha','ta':'Vani','hi':'Lekha'}[lang],'-r','150','-o',str(source),text],check=True,timeout=60)
        subprocess.run([a.ffmpeg,'-y','-i',str(source),'-ar','16000','-ac','1',str(target)],check=True,capture_output=True,timeout=60)
        import wave
        with wave.open(str(target)) as wav:
            if wav.getnframes()/wav.getframerate()<1: raise ValueError('Speech engine produced empty/too-short audio')
    with tempfile.TemporaryDirectory() as folder:
        for i,r in enumerate(voices):
            speech(r['transcript'],r['language'],DATA/r['path'],folder)
            print('Built',r['path'],flush=True)
        speech('Please pack your router safely and include the invoice.','en',DATA/'voice_notes/reply.wav',folder)
        for i in range(1,4):
            frames=Path(folder)/f'frames{i}';frames.mkdir()
            for t in range(15):
                im=Image.open(DATA/f'claim_photos/claim_{i:02}.png').convert('RGB')
                d=ImageDraw.Draw(im)
                if t<5:
                    d.rectangle((110,90,530,410),fill='#b58a54',outline='#624625',width=6)
                    d.line((320,90,320,410),fill='#efe0c2',width=18)
                d.rectangle((0,440,640,480),fill='white')
                d.text((20,455),f'Synthetic unboxing animation | second {t} | '+('sealed box' if t<5 else 'opened device'),fill='black')
                im.save(frames/f'{t:02}.png')
            subprocess.run([a.ffmpeg,'-y','-framerate','1','-i',str(frames/'%02d.png'),'-stream_loop','-1',
                '-i',str(DATA/f'voice_notes/voice_{i:02}.wav'),'-t','15','-r','12','-c:v','libx264','-pix_fmt','yuv420p',
                '-c:a','aac','-b:a','48k','-movflags','+faststart',str(DATA/f'unboxing_videos/unboxing_{i:02}.mp4')],check=True,capture_output=True,timeout=60)
    print('Generated 6 voice notes, fixed reply, and 3 voiced 15-second synthetic videos.')

if __name__=='__main__':run()
