# Smart Claims Desk — four-hour multimodal AI workshop

One use case across all four hours: read damaged-product evidence, validate an invoice, consult a fictional warranty policy, and draft a support response. Claims above INR 5,000 require human approval when otherwise approvable; incomplete or conflicting evidence also requires review. This workshop never issues a refund.

Based on the supplied `Multimodal_AI_4hr_TOC.xlsx`. Each hour retains **12 minutes theory + 48 minutes hands-on**. Hours are 10–11, 11–12, 12–13 and 14–15; the lunch break is outside the four teaching hours.

## Start here

Extract the ZIP and open a terminal **inside `smart_claims_desk`**. Use Python 3.11 or 3.12 for the broadest optional ML dependency support. Core code was also exercised on Python 3.14; see `VALIDATION.md` for actual checks.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python tools/preflight.py
python hour_01/run.py
python hour_02/run.py
python hour_03/run.py
python hour_04/run.py
python -m pytest -q
```

Windows PowerShell: use `python -m venv .venv`, then `.venv\Scripts\Activate.ps1`. All remaining Python commands are the same. Run one command at a time; do not paste shell comments into Python.

A **`.env` with empty key placeholders is included**. It defaults to `APP_MODE=demo`. If missing, copy `.env.example` to `.env`. Add your own keys only to `.env`:

```dotenv
APP_MODE=live
OPENAI_API_KEY=your-own-key
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your-own-langsmith-key
LANGSMITH_PROJECT=smart-claims-workshop
```

No real API key is distributed. Keep `.env` private. Model names in the file are configurable examples; confirm access in your account before class. Live mode calls paid services and sends fictional evidence to those services. Keep LangSmith tracing disabled until you explicitly want fictional prompts and results logged to your project. Restart API/UI processes after changing `.env`.

## The four hours

| Hour | Build and workflow | Guide |
|---|---|---|
| 1 | Image → structured damage JSON; compare cloud/local | [Hour 1](hour_01/README.md) |
| 2 | Invoice → validated fields; charts; CLIP search; cited manual RAG | [Hour 2](hour_02/README.md) |
| 3 | Speech → ticket; reply → speech; video → timeline; image generation/edit | [Hour 3](hour_03/README.md) |
| 4 | Tools → LangGraph → policy → review → reply; evaluation; FastAPI + Streamlit | [Hour 4](hour_04/README.md) |

Each hour folder contains `README.md`, `run.py`, a local `input.csv`, `.env.example` and `requirements.txt`. The local CSV is a teaching manifest of that hour's inputs; shared media stays under `data/`. All four stages import `claims/` to avoid incompatible copies of earlier code. Use the project-root `.env`; hourly examples are references, not separately loaded configuration.

## Modes and the meaning of outputs

**Demo:** deterministic replay of labels for unchanged bundled media. The SHA-256 of the input must match a fixture. Modified files and arbitrary uploads are rejected. No vision inference, ASR inference, generative images, cloud/local speed comparison, or model-quality claim is made. TTS returns one fixed sample reply. Video still decodes/samples the real MP4; its observations/transcript are fixture labels. CLIP is always a real local model and requires a first-run download.

**Live:** OpenAI vision/structured extraction, ASR, TTS, image generation/edit, optional Ollama vision, and optional embedding RAG. There is no silent fallback to demo when an API fails. Review the `runs/usage.jsonl` token counts and measured latency. Convert tokens to cost using your account's current model rates; no hardcoded prices are presented as current.

The default RAG in the agent is a transparent **lexical baseline over manual text and curated diagram descriptions**. Hour 2 also includes an actual **VLM caption → embeddings → Chroma** implementation in `claims/rag_index.py`. CLIP performs text-to-image and image-to-image retrieval separately. ColPali, native any-to-any models and real-time streaming are explained in theory, not falsely represented as implemented.

## Run the final application

Terminal A, with the environment activated:

```bash
uvicorn claims.api:app --host 127.0.0.1 --port 8000
```

Terminal B, same folder/environment:

```bash
streamlit run streamlit_app.py
```

Open `http://localhost:8501`. Leave “Use bundled router photo + invoice + English voice note” checked, total INR 2,360, product router, two days since delivery. Submit to see an automatic proposed approval with citations. API docs: `http://127.0.0.1:8000/docs`.

For a high-value review, uncheck the sample option and upload `claim_02.png` + `invoice_02.pdf` + `voice_02.wav`; select phone, INR 7,080, two days. The result must say `pending_review` with no reply until a reviewer submits a decision. Reviewer token comes from `.env`. Both approve and reject are supported. SQLite saves the interrupted state across API restarts.

## Files and data

| Path | Purpose |
|---|---|
| `claims/core.py` | Shared Pydantic schemas, `.env`, paths, fixture matching, live structured adapter and usage logging |
| `claims/vision.py` | Damage extraction and cloud/Ollama comparison |
| `claims/documents.py`, `rag_index.py` | PDF rendering, totals validation, OCR, chart QA, lexical/caption-embedding RAG, CLIP search |
| `claims/media.py`, `labs.py` | ASR/tickets, TTS, frame sampling/audio merge, generation/editing, prompt/table exercises |
| `claims/agent.py` | Graph state, modality routing, deterministic policy, SQLite checkpoints, human interrupt/resume |
| `claims/api.py`, `streamlit_app.py` | Multipart upload endpoint, token checks, reviewer endpoint and UI |
| `claims/evaluation.py`, `judge.py`, `metrics.py` | Label-based evaluation, optional live groundedness judge and CLIPScore |
| `claims/safety.py` | Heuristic injection detection, phone masking and face blurring |
| `data/input_claims.csv` | 20 input claim records; paths relative to `data/` |
| `data/eval_set.csv` | Separate expected fields, proposed decisions/routes and relevant pages |
| `data/README.md` | All datasets, provenance, schema and limitations |
| `tests/` | Regression tests including arithmetic, incomplete evidence, approval threshold, durable resume and API auth |
| `tools/` | Preflight, reproducible fixture builders and batch CSV runner |
| `runs/` | Generated JSON, audio, usage, uploads and SQLite state; created on first run |
| `TOC_ALIGNMENT.md`, `FACILITATOR.md` | Row-level coverage and timed teaching notes |

## Prerequisites and optional labs

Install **ffmpeg** for video and **Tesseract** for OCR/privacy labs before the session. macOS: `brew install ffmpeg tesseract`; Ubuntu: `sudo apt-get install ffmpeg tesseract-ocr`. Windows: install official builds and add executables to PATH. PyMuPDF renders PDFs, so Poppler is not required by this implementation.

For local vision, install Ollama and run `ollama pull gemma3:4b`, then ensure Ollama is running. Allow time for model downloads; 16 GB RAM is recommended. For CLIP and Chroma run `pip install -r requirements-clip.txt` **before class** and warm the model. A local GPU is optional. CLIP dependencies may lag the newest Python release; use 3.11/3.12.

## Troubleshooting and checks

* Import error: activate `.venv`, install requirements using that interpreter, run from the project root.
* Demo input rejected: use an unchanged bundled file, or switch to live mode with your own API key.
* API 401/403: match `APP_API_TOKEN` and `REVIEWER_TOKEN` to your server environment. Do not use provider API keys as app tokens.
* Model/API failure: check account model access, quota and configured model name. Errors are surfaced, not converted to sample answers.
* `ffmpeg`/Tesseract missing: add system executables to PATH and restart terminals.
* Human review pending: submit to the same thread ID; do not create a new claim to resume it.
* RAG citations show IDs but not support: inspect the original page and figure. Valid citation IDs alone do not prove factual grounding; use the judge lab and manual review.
* Delete `runs/` to clear training uploads/state after stopping services. Deleting it also removes pending approvals. Delete `.chroma/` to rebuild optional indexes.

## Local container demo

```bash
docker build -t smart-claims-desk .
docker run --rm --env-file .env -p 127.0.0.1:8000:8000 -v claims-runs:/app/runs smart-claims-desk
```

Run Streamlit locally against that API. `.dockerignore` excludes `.env`; secrets are injected at runtime. Docker builds the API only. This is a local training deployment, not a production service: add identity/roles, malware scanning, quotas, encrypted storage, retention, durable multi-user infrastructure and monitoring before handling real customer data. The UI uses blocking request status, not token streaming.

## Sources

Implementation references: [OpenAI images and vision](https://developers.openai.com/api/docs/guides/images-vision), [audio transcription](https://developers.openai.com/api/reference/python/resources/audio/subresources/transcriptions/methods/create), [image generation/editing](https://developers.openai.com/api/docs/guides/image-generation), [LangGraph interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts), [LangSmith tracing](https://docs.langchain.com/langsmith/annotate-code). APIs and account access can change; verify in the pre-session check.


Multimodal AI means working with different types of information—images, documents, audio, video and text—within one application.
In Smart Claims Desk, each input provides a different piece of evidence about the same damaged-product claim.
One clarification: the current project is a damaged-product claim and warranty assistant. Its fictional rules demonstrate a claims workflow; it does not implement a complete insurance policy or settlement system.
Consider this example:
A customer says their router arrived damaged and requests a replacement.

Input modality	Customer provides	What the application does	Evidence obtained
Image	Photo of the router	A vision model identifies the product and visible damage	“Router has a cracked case”
Document	Invoice PDF	Renders pages as images, extracts fields and checks arithmetic	“Router invoice total is ₹2,360”
Audio	Spoken complaint in English, Telugu or Hindi	Transcribes speech, then extracts complaint, order ID and sentiment	“Customer reports damage on delivery”
Video	Unboxing recording	Samples frames and extracts audio for analysis	Timestamped observations of the package and product
Text/reference documents	Warranty manuals	Retrieves relevant policy passages with citations	“Delivery damage is covered within seven days”


How the information comes together
Photo ───────→ Damage details ─────────┐
Invoice PDF ─→ Purchase details ───────┤
Voice note ──→ Complaint and order ID ─┤
Video ───────→ Timeline observations ──┤
                                      ↓
                           Shared claim workflow
                                      ↓
                        Retrieve warranty evidence
                                      ↓
                      Check rules and inconsistencies
                                      ↓
                     Draft decision or human review
                                      ↓
                          Written support response
The application converts different inputs into structured information, such as:
{
  "product": "router",
  "damage_type": "cracked_case",
  "invoice_total": 2360,
  "totals_valid": true,
  "complaint": "Router arrived damaged"
}
This is how the modalities become useful together: the system can compare facts rather than dealing only with raw files.
How the four hours build this
Hour	Contribution
Hour 1	Understand the product photo and extract damage fields
Hour 2	Extract invoice details, validate totals and retrieve warranty evidence
Hour 3	Process speech/video and demonstrate spoken replies and support-image generation
Hour 4	Use LangGraph to connect the tools, apply rules and pause for human review


What makes the decision?
AI extracts and describes evidence. In the current project, Python rules determine the proposed decision and review route.
For example:
- Matching product photo, valid invoice and covered delivery damage can produce an approval proposal.
- Missing or conflicting evidence requires human review.
- An otherwise approvable claim above ₹5,000 pauses for an authorized reviewer.