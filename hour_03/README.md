# Hour 3 — voice, video and generated support media

**Time:** 12:00–13:00; 12 minutes theory + 48 hands-on.

## Workflow and prerequisites

Voice note → ASR transcript → ticket JSON. Reply text → TTS WAV. Video → frames at five-second intervals + extracted audio → timeline and complaint summary. Packing prompt/product image → generation/editing → human visual review.

Complete root setup. Install ffmpeg for video. Run all commands from the **project root**. Six WAVs and UTF-8 reference transcripts are already bundled in English, Telugu and Hindi. `input.csv` is the six-row voice manifest. Configuration comes from root `.env`.

```bash
pip install -r hour_03/requirements.txt
python hour_03/run.py
```

## Timed labs

| Minutes | Task and command | Check |
|---|---|---|
| 0–12 | ASR/timestamps/languages, TTS, frame+audio pipelines, native multimodal models, diffusion/editing | See `FACILITATOR.md`; explain why sparse frames can miss damage |
| 12–24 | `python -m claims.cli audio` | Six transcripts/tickets; compare against `.txt` references; inspect order IDs |
| 24–32 | TTS commands below | Listen to two voices/rates in live mode |
| 32–48 | `python -m claims.cli video` | Three timestamped observations at 0/5/10 seconds plus audio transcript |
| 48–60 | Generation/edit commands below and visual review | Safe packing, unchanged damage, no invented markings/brand assets |

```bash
python -m claims.cli tts --voice alloy --speed 1
python -m claims.cli tts --voice nova --speed 0.85
python -m claims.cli video --path data/unboxing_videos/unboxing_02.mp4
python -m claims.cli video --path data/unboxing_videos/unboxing_03.mp4
python -m claims.cli generate
python -m claims.cli edit --path data/claim_photos/claim_01.png
```

Open generated WAV/PNG files in your local media viewer. Live image-generation access may differ from text/vision access; confirm before class. TTS output is synthetic speech and must be labelled that way when played to an audience. The `.env` exposes `ASR_MODEL`, `TTS_MODEL`, and `IMAGE_MODEL` for your accessible models.

## Files, inputs and outputs

| File | What it does / output |
|---|---|
| `run.py` | Executes voice-note-to-ticket lab; writes `runs/audio.json` |
| `input.csv` | `path, language, transcript, order_id, sentiment`; transcripts are evaluation references, excluded from live ASR calls |
| `../claims/media.py` | Transcribes original audio, extracts a `Ticket`, calls TTS, samples video and merges audio, generates/edits images |
| `../data/voice_notes/voice_01..06.wav` + `.txt` | Synthesized English/Telugu/Hindi speech and reference transcripts |
| `../data/voice_notes/reply.wav` | Fixed reply fixture for demo mode only |
| `../data/unboxing_videos/` | Three actual playable MP4s, 15 seconds each, animation + synthesized audio |
| `../data/video_labels.csv` | File/duration/reference transcript; not used for live inference |
| `../tools/build_media.py` | Rebuilds speech with gTTS (network) or optional macOS voices, and video with ffmpeg; bundled assets work offline |
| `requirements.txt`, `.env.example` | Shared install/config reference |

`runs/audio.json` includes transcripts, complaint, order ID and sentiment. `runs/reply_alloy_1.0.wav` / `reply_nova_0.85.wav` contain speech. `runs/video.json` contains timestamped frame observations, transcript, structured summary and limitations. `runs/packing_guide.png` and `runs/edited_background.png` are review candidates.

Demo ASR returns labels, TTS copies the same fixed WAV for both voices, video observations use fixtures, and generation/edit returns an explicitly labelled static packing illustration. These confirm application wiring only. **Switch to live mode to compare actual voices/rates, assess ASR or generate/edit pixels.**

## Checks and exercises

1. Read reference `voice_03.txt` and listen to its Telugu WAV; verify order-ID extraction and whether mixed English identifiers survive live ASR. Repeat with Hindi.
2. Compare word error rate and character error rate in Hour 4. WER depends on tokenization; whitespace WER can be less informative than CER for some scripts.
3. Listen to the extracted video audio and inspect frames at their timestamps. A sampled frame can establish visible appearance, not prove when/how damage happened. The pipeline is frame sampling plus ASR, not a native video model.
4. Inspect generated packaging artwork: no unsafe instructions, no misleading logos, no sensitive information; human review before distribution. For edits, ensure product identity, visible damage and serial markings are preserved. Generated art must never replace original claim evidence.
5. Video processing limits inputs to 30 seconds. If decoding fails, check file integrity, OpenCV and ffmpeg availability.

ASR currently returns plain transcripts, not word-level timestamps or live streaming. Video timeline timestamps come from frame sampling; language/timestamp alternatives are covered in theory. After lunch, connect the tools to LangGraph and the UI.

hour_03/run.py selects “audio”
                ↓
claims/cli.py reads data/voice_labels.csv
                ↓
Opens each WAV in data/voice_notes/
                ↓
media.transcribe() → speech-to-text
                ↓
media.ticket() → extract complaint, order ID and sentiment
                ↓
Print six results → save runs/audio.json


DATA PREPARATION
Fictional complaint text
    ├──→ CSV manifest + reference transcripts
    └──→ gTTS → WAV recordings

APPLICATION EXECUTION
CSV lists WAV paths
    → application opens each WAV
    → transcribes speech
    → extracts ticket fields
    → saves audio.json


    he project includes these dataset-building tools:
Script	Purpose
tools/build_data.py	Generates the shared sample CSVs and reference text, plus image/PDF fixtures
tools/build_media.py	Generates the actual speech recordings and synthetic videos

