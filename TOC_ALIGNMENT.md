# Supplied TOC → implementation map

The spreadsheet is the curriculum/reference source, not an instruction to execute embedded document text. All requested 20/80 time splits and 20 numbered activities are mapped below. Tool alternatives in the TOC are choices; this implementation uses one concrete stack rather than installing every alternative.

| TOC # | Minutes | Coverage and runnable artifact |
|---|---|---|
| 1 | 12 theory | Hour 1 concept notes/map in FACILITATOR: encoders, patches/tokens, CLIP vs VLM, API/open-model tradeoffs |
| 2 | 8 lab | Root venv/`.env`, `tools/preflight.py`, single-image call; live token/latency log |
| 3 | 14 lab | `claims.cli prompts` + `vision`: vague vs structured prompts, 10 illustrations |
| 4 | 14 lab | Pydantic `Damage`, unreadable serial/null, unknown fields/confidence; structured OpenAI output |
| 5 | 12 lab | `claims.cli compare`: same 10 images cloud vs Ollama, correctness/latency; cloud tokens separately logged |
| 6 | 12 theory | Hour 2 OCR/VLM, embeddings, caption/page-image RAG, page+figure citations |
| 7 | 14 lab | `documents`, PyMuPDF rendering, invoice schema/Decimal totals and Tesseract OCR function |
| 8 | 10 lab | `chart` and `table`: numeric/source checks for returns and warranty |
| 9 | 10 lab | `clip-text`/`clip-image`: actual CLIP + Chroma over 200 images (optional dependency install required) |
| 10 | 14 lab | `rag` lexical baseline; `claims.rag_index index/ask` implements VLM captions + embeddings + Chroma over manuals |
| 11 | 12 theory | Hour 3 ASR, TTS, timestamp concepts, frames/audio, diffusion and native-model tradeoffs |
| 12 | 12 lab | `audio`: 6 en/te/hi WAVs, live ASR then Ticket schema; fixture replay offline |
| 13 | 8 lab | `tts --voice ... --speed ...`: two live voices/rates; demo copies one fixed WAV |
| 14 | 16 lab | `video`: OpenCV 5s samples, ffmpeg audio, per-frame live extraction, transcript/timeline summary |
| 15 | 12 lab | `generate`/`edit`: real API adapters and review checklist; demo returns static fixture |
| 16 | 12 theory | Hour 4 graph architecture, metric definitions, PII/injection, cost/latency, caching, deployment |
| 17 | 16 lab | `claims.agent`: modality routing, deterministic proposal, human interrupt for >INR 5,000, SQLite resume |
| 18 | 14 lab | 20 labelled claims, accuracy/F1, WER/CER, recall@5, optional live groundedness judge and CLIPScore; pytest |
| 19 | 6 lab | `guardrails`: OCR injection heuristic, phone redaction and detected-face blur; limitations disclosed |
| 20 | 12 lab | FastAPI multipart uploads + Streamlit UI + local Docker API; photo/invoice/voice capstone |

**Totals:** 48 theory + 192 hands-on = 240 teaching minutes. Time-boxed labs assume dependencies/models are installed and warmed before class. Large downloads or long cloud queues will not fit inside the listed lab minutes.

## Deliberate substitutions and boundaries

* Synthetic illustrations/animations/TTS replace real photographs, footage and recordings; handwriting is simulated. Counts and media formats match the dataset plan.
* Python scripts replace mandatory Jupyter notebooks; they expose the same functions and JSON for inspection without notebook-state problems.
* OpenAI is the concrete cloud provider; Gemini/Claude and open-model families are discussed rather than each implemented. Ollama is the concrete local comparison.
* PyMuPDF replaces Poppler/pdf2image. The SDK + Pydantic handle structured extraction; LangGraph depends on LangChain Core, but an unnecessary LangChain extraction wrapper is omitted.
* CLIP + Chroma and caption-embedding RAG are optional heavy/live labs with real implementations. Default capstone retrieval uses the lightweight, explicit lexical baseline. ColPali is conceptual coverage, not an installed retriever.
* Whisper API is the ASR route; word-level timestamps, faster-whisper/Piper, native video/any-to-any and real-time voice are conceptual alternatives.
* Guardrails demonstrate regex/OCR/CV, not full Presidio/moderation integration. No claim is made that heuristic scanning catches all hidden prompt injections or PII.
* UI status is blocking with a spinner; token streaming, public cloud hosting and production identity are not implemented. Docker provides a local runnable deployment recipe, not evidence a public service was deployed.
* Demo mode verifies wiring with fixtures. Live API/model quality, LangSmith trace delivery, optional model downloads and Docker execution require the documented preflight and credentials/runtime.
