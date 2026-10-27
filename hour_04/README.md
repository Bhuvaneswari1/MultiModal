# Hour 4 — LangGraph, evaluation, guardrails and application

**Time:** 14:00–15:00; 12 minutes theory + 48 hands-on.

## End-to-end workflow

```mermaid
flowchart LR
  A[Photo/PDF/voice/video] --> B[Detect extension and run tool]
  B --> C[Retrieve warranty with citations]
  C --> D[Validate evidence and propose decision]
  D --> E{Review required?}
  E -->|yes| F[SQLite checkpoint + interrupt]
  F --> G[Authorized reviewer approve/reject]
  G --> H[Resume same thread]
  E -->|no| I[Draft written reply]
  H --> I
```

Run commands from the **project root**, after root setup. `input.csv` contains the 20 labelled evaluation claims; `data/input_claims.csv` is the input-only version. Root `.env` holds all real settings/secrets.

```bash
pip install -r hour_04/requirements.txt
python hour_04/run.py
```

## Timed labs

| Minutes | Task | Commands/check |
|---|---|---|
| 0–12 | Tool routing, evaluation metrics, PII/injection, token cost, resizing/caching, deployment | Hour 4 theory in `FACILITATOR.md` |
| 12–28 | Inspect/build LangGraph, run photo+invoice+voice, test >5,000 approval pause | `python -m claims.cli agent`; graph tests below |
| 28–42 | Score 20 claims and six voice notes; inspect retrieval and live judge | Evaluation command below; do not present demo metrics as model quality |
| 42–48 | Mask phone, blur detected faces, flag injection | `python -m claims.cli guardrails` (requires Tesseract) |
| 48–60 | Start FastAPI + Streamlit and run capstone demo | Two terminals as shown below |

## Files explained

| Path | Responsibility |
|---|---|
| `run.py`, `input.csv` | Runs graph artifact; carries evaluation rows with media paths, expected fields/decision/route |
| `../claims/agent.py` | Explicit photo/PDF/audio/video tool routing; policy checks; conditional review branch; durable SQLite checkpoint |
| `../claims/api.py` | `/health`, multipart `POST /claims`, authorized `POST /claims/{thread_id}/review`; extension/count/size limits |
| `../streamlit_app.py` | Upload/sample selector, pending review form and downloadable JSON |
| `../claims/evaluation.py`, `judge.py`, `metrics.py` | Field accuracy/F1, proposed-decision/route accuracy, WER/CER, recall@5, optional supportedness judge/CLIPScore |
| `../claims/safety.py` | Heuristic injection scanning, Indian mobile masking, OCR rectangle redaction, face blurring |
| `../tests/test_workshop.py` | Data integrity, invoice mismatch, altered fixture rejection, citations, threshold, missing evidence, restart/resume, auth |
| `../Dockerfile`, `.dockerignore` | API container; runtime env injection; excludes secrets/generated state |
| `requirements.txt`, `.env.example` | Dependency/config references |

## Decision policy (fictional, explicit)

* Approve a cracked case/broken screen within seven days only with a matching product photo and arithmetically valid invoice whose total matches the submitted amount.
* Dented package alone or no visible product damage: reject when evidence is otherwise complete. After seven days: reject under this fictional delivery-damage policy.
* Missing photo/invoice, confidence below 0.7, unknown damage, conflicting product, total mismatch or suspected injection: human review.
* An otherwise approved claim **above INR 5,000** pauses for review. INR 5,000 exactly does not trigger the high-value rule. A high-value claim that should be rejected does not become approved just because it was expensive.
* The graph's `decision` before an interrupt is a **proposal**; the API exposes `pending_review`, not final approval. No reply is drafted until resumed. Human approve/reject replaces the proposal and records reviewer identity.

## Run and verify the application

Terminal A:

```bash
uvicorn claims.api:app --host 127.0.0.1 --port 8000
```

Terminal B:

```bash
streamlit run streamlit_app.py
```

Open `http://localhost:8501`; use bundled router sample at INR 2,360. Expect route `automatic`, decision `approve`, citations and a draft reply. For review, uncheck sample; upload photo 2/invoice 2/voice 2, select phone, INR 7,080, two days. Expect `pending_review`. Enter a reviewer name and the root `.env` reviewer token; choose approve or reject. The same thread resumes. Restart the API while pending to test SQLite persistence.

Multipart API example (macOS/Linux):

```bash
curl -X POST http://127.0.0.1:8000/claims \
  -H 'X-API-Key: local-workshop-token' \
  -F 'product=router' -F 'amount=2360' -F 'delivery_days=2' \
  -F 'files=@data/claim_photos/claim_01.png' \
  -F 'files=@data/invoices/invoice_01.pdf' \
  -F 'files=@data/voice_notes/voice_01.wav'
```

Replace example app tokens if changed in `.env`. In Swagger `/docs`, supply both relevant header fields. Only the reviewer endpoint accepts reviewer decisions; ordinary claim uploads cannot submit one.

## Evaluation and LangSmith

```bash
python -m claims.cli evaluate
python -m pytest -q
python -m claims.judge
```

The judge command intentionally requires live mode. `runs/evaluation_report.json` contains per-claim predictions plus field accuracy/F1, decision and route accuracy, retrieval recall@5, and WER/CER by voice note. `runs/judge.json` gives unsupported claims and a supportedness flag for one cited warranty answer. An LLM judge can be wrong; verify with a human and do not treat one example as a population hallucination-rate estimate. `claims.metrics` adds an optional CLIPScore lab. Macro field F1 is over damage classes; accuracy uses damage + severity fields. Review the metric definitions in the report.

For LangSmith set tracing true/key/project in root `.env`, restart, run a live extraction, and find the `structured-extraction` spans and graph nodes in the configured project. With no live key/tracing, the local checks still work. Tracing is opt-in; prompts/transcripts and graph state can be logged. Do not use real personal data. Delete local `runs/` and clear test traces according to your account policy after the workshop.

The retrieval corpus has only two pages per product, so recall@5 is deliberately trivial. Expand the corpus/distractors and hold out new claims before assessing model quality. Demo scores reflect fixture replay and deterministic policy tests, not model performance.

## Guardrails and deployment scope

Inspect `runs/sanitized.png`: the fictional phone number should be blacked out and injection flagged. Face detection blurs detected frontal faces; synthetic samples contain no real faces. Test the detector yourself with consented fictional/stock material if needed. Heuristics miss spaced digits, handwriting, hidden instructions and some faces. The live photo route sanitizes before vision calls; PDF pages, video frames and ASR uploads are not a complete PII-redaction pipeline. Use fictional training assets only. No universal injection-prevention claim is made.

The API enforces 1–4 files, allowed suffixes and 20 MB/file. Parsers validate content further but no malware scanner or content moderation API is integrated. `SYSTEM` separates evidence from instructions. The agent uses deterministic policy rules rather than following uploaded instructions. Example app/reviewer tokens are local workshop controls, not enterprise authentication. Docker instructions are in the root README. Stop services after the session; deployment to public hosting is outside this local capstone.
