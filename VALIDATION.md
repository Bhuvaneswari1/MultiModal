# Validation record

Checked on 21 October 2026, macOS arm64, Python 3.14.6, in an isolated virtual environment. `requirements-tested.txt` records exact direct dependency versions; standard `requirements.txt` supports the documented installation ranges. Optional ML dependencies are best installed with Python 3.11/3.12.

| Check | Result |
|---|---|
| Core dependency installation and module preflight | Passed; provider key absent and never printed |
| Python source parsing | Passed |
| `python -m pytest -q` | **13 passed** |
| Four hourly `run.py` entry points | Passed in demo mode |
| 20-claim evaluation | Ran; per-claim damage/severity, proposed decisions/routes matched fixtures |
| Six multilingual voice notes | Playable PCM WAV, 7.01–8.59 s, nonzero audio signal; fixture ASR score is not model accuracy |
| Fixed reply speech | Playable WAV, 4.06 s |
| Three unboxing videos | Decode successfully; 15 s each; sampled video+audio pipeline ran |
| CSV batch runner including optional videos | Ran all 20 rows; review rows remain paused |
| Chart/warranty table checks | April/30 and seven days matched source fixtures |
| Invoice arithmetic | Valid invoice passes; intentional INR 100 mismatch fails |
| OCR | Tesseract recovered text from digital, scanned and simulated handwritten-style invoice samples |
| Privacy/injection exercise | Phone rectangle redacted, injection text flagged; redacted image visually inspected |
| All invoice/manual pages | Rendered 14 pages and visually reviewed; readable, no clipping/overlap |
| FastAPI + Streamlit integration | Local Uvicorn server started; Streamlit AppTest submitted photo+invoice+voice and displayed cited JSON |
| High-value approval | SQLite interrupt, graph reconstruction/restart and resume tested; reviewer token required; repeated review rejected |
| Invoice/product conflict | Regression test confirms valid totals alone cannot authorize wrong-product evidence |

Video checks used an isolated `imageio-ffmpeg` binary exposed on test PATH; participants must install ffmpeg as documented. Core tests check video decoding without requiring a shell ffmpeg. PDF rendering used PyMuPDF; fixture generation used ReportLab. Speech assets were generated with gTTS because the installed macOS speech tool produced empty audio; the builder now rejects empty WAVs.

## Not verified in this environment

No user provider credentials were supplied. Live cloud vision, ASR, TTS, generation/editing, judge/embedding calls and LangSmith trace delivery were **not executed**. Ollama, CLIP/Chroma model downloads/indexing, CLIPScore and Docker execution were also **not executed**. Their implementations, commands, configuration and prerequisites are supplied, but account access, hardware and first-run downloads must be checked before the live session. No public cloud service was deployed.

Demo metrics of 1.0 accuracy/F1/recall and 0 WER/CER reflect replayed fixture labels, not measured AI quality. The tiny two-page-per-product corpus makes recall@5 trivial. The illustrations, animated videos and simulated handwriting are teaching data, not a representative test set. Guardrails are limited heuristics; only fictional training data should be used.

`examples/` contains portable snapshots of the exercised demo outputs. Generated uploads, SQLite databases, Python bytecode and local virtual environments are excluded from the deliverable archive.

## Telugu update — 27 October 2026

Replaced the two Tamil voice notes with synthesized Telugu speech and updated both Hour 3 CSV manifests, UTF-8 references, third video audio and its reference transcript, generators and teaching guides. English and Hindi samples are retained. Hour 3 and the 20-claim evaluation reran in demo mode; live Telugu ASR quality is not verified.
