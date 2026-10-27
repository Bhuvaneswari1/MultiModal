# Hour 2 — documents, charts, similarity search and cited RAG

**Time:** 11:00–12:00; 12 minutes theory + 48 hands-on.

## Workflow

Invoice PDF → page images → schema extraction → arithmetic validation. Separately: chart/table image → answer → source-number check; product images → CLIP vectors → Chroma → text/image search; manual text + diagram captions → retrieval → cited answer.

Root setup and Hour 1 are prerequisites. Run commands from the **project root**. `input.csv` is the eight-invoice manifest with answer keys. Keys remain in root `.env`; the local `.env.example` is a reference.

```bash
pip install -r hour_02/requirements.txt
python hour_02/run.py
```

## Timed labs

| Minutes | Task | Command/check |
|---|---|---|
| 0–12 | OCR vs VLM, charts, CLIP/shared embeddings, caption/page-image retrieval, citations | Use Hour 2 theory in `FACILITATOR.md`; ColPali is a conceptual alternative |
| 12–26 | Read 8 invoices, render PDF pages, validate totals and compare OCR | Run documents; invoice 8 must fail totals validation |
| 26–36 | Read returns chart and warranty table | Run chart/table commands; April has 30 returns, cracked-case window is 7 days |
| 36–46 | Embed/search 200 synthetic catalogue images | Run actual CLIP text/image search after optional dependency/model warm-up |
| 46–60 | Retrieve manual pages and ground a warranty answer | Baseline works offline; run caption/embedding index live if preflight is complete |

```bash
python -m claims.cli documents
python -m claims.cli chart
python -m claims.cli table
python -m claims.cli rag --query "Is a cracked case covered?"
```

OCR comparison (Tesseract must be on PATH):

```bash
python -c "from claims.documents import ocr; from claims.core import DATA; print(ocr(DATA/'invoices/invoice_06.pdf'))"
```

Compare OCR text, VLM JSON and the separate answer key. OCR does not automatically validate totals or understand product damage. Invoices 6–7 are raster scans. Invoice 8 is an italic-font handwritten-style simulation with a deliberate INR 100 arithmetic error, not natural handwriting.

## Actual similarity search

Preinstall and warm before class. This lab downloads a pretrained CLIP model on first use; demo mode does not turn it into fixture lookup.

```bash
pip install -r requirements-clip.txt
python -m claims.cli clip-text --query "cracked router case"
python -m claims.cli clip-image --path data/claim_photos/claim_01.png
```

Images → CLIP image vectors → persistent Chroma `products`; text query → CLIP text vector, example query → CLIP image vector. Inspect the top five paths/distances in `runs/clip-text.json` and `runs/clip-image.json`. Distance is a retrieval score, not damage confidence. These repeated synthetic shapes are a small lab, not a catalogue benchmark.

## Actual caption-then-embed RAG

```bash
python -m claims.rag_index index
python -m claims.rag_index ask --query "Is a cracked case covered?"
```

Set `APP_MODE=live`, valid OpenAI key, and optional `EMBEDDING_MODEL=text-embedding-3-small` in root `.env`; Chroma comes from `requirements-clip.txt`. Six manual pages are rendered, a VLM transcribes text/describes diagrams, text+captions are embedded and stored with page/figure metadata. Queries retrieve the top five pages and the model must cite only returned IDs. Output: `runs/embedding_rag.json`. Verify each claim against the actual PDF page; citation ID validation does not prevent every unsupported statement.

The default `claims.documents.rag()` used by the capstone is a small lexical baseline over `manual_pages.json`, which already includes the fictional policy and diagram-related text. It is intentionally distinguishable from CLIP search and the live caption/embedding pipeline. Page-image/ColPali retrieval is discussed, not implemented.

## Files and inputs

| Path | Purpose |
|---|---|
| `run.py`, `input.csv` | Run invoice extraction; inspect labels/kind and expected invoice JSON |
| `../claims/documents.py` | PyMuPDF rendering, Invoice extraction, Decimal totals check, OCR, chart QA, lexical retrieval, CLIP/Chroma search |
| `../claims/rag_index.py` | Real caption-then-embed manual retrieval and grounded generation |
| `../claims/labs.py` | Warranty-table QA with source check |
| `../data/invoices/`, `invoice_labels.csv` | Eight PDFs, extracted-field answer keys and valid/invalid totals |
| `../data/manuals/`, `manual_pages.json` | Three two-page fictional manuals with diagrams, text and citation IDs |
| `../data/charts/`, `returns_by_month.csv` | Returns chart, warranty table and authoritative numeric source |
| `../data/product_catalog.csv`, `product_catalog_images/` | 200 ID/path/category/damage-labelled synthetic product images |
| `requirements.txt`, `.env.example` | Shared dependencies/settings; no secrets |

## Output and checks

`runs/documents.json`: invoice fields and `totals_valid`. Claim 1 invoice is INR 2,000 + 360 GST = 2,360. Invoice 8 totals are inconsistent and must not pass. `runs/chart.json` must report April, 30 and `correct=true`; `runs/table.json` must report 7 days. `runs/rag.json` includes file/page/figure citations such as `router-p1`.

```bash
python -m pytest -q tests/test_workshop.py -k 'invoice_totals or rag_citations'
```

Ask a question absent from the policy to inspect live abstention; the offline baseline returns an extract rather than semantic reasoning. Do not treat retrieval relevance as proof of warranty eligibility. Next hour adds speech and video evidence.

hour_02/run.py
    ↓ selects “documents”
claims/cli.py
    ↓ reads data/invoice_labels.csv
    ↓ gets the eight PDF paths
claims/documents.py → invoice(pdf_path)
    ↓ extracts/replays invoice fields
    ↓ checks invoice arithmetic
Print results → save runs/documents.json