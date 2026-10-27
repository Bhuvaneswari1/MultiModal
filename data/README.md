# Fictional workshop data

All content is synthetic and local. No real customer, transaction, product brand, voice recording or invoice is included. No external dataset is required. You may use and modify these generated fixtures for this workshop. Reference transcripts/labels are for evaluation; live inference reads the media, not their answer keys.

| Dataset | Count and format | Meaning / source of truth |
|---|---|---|
| `claim_photos/` | 10 PNG illustrations | Labelled router/phone/monitor, damage classes, severity, serial and confidence in `photo_labels.csv` |
| `product_catalog_images/` | 200 JPG illustrations | CLIP image corpus; `product_catalog.csv` joins ID to path/name/category/damage |
| `invoices/` | 8 one-page PDFs | 5 digital, 2 raster scans, 1 simulated handwritten-style note; `invoice_labels.csv` contains expected JSON and arithmetic status |
| `manuals/` | 3 PDFs × 2 pages | Fictional router/phone/monitor warranty + packing, with diagrams; `manual_pages.json` mirrors text/page/figure metadata |
| `charts/` | 3 PNGs | Returns chart, warranty table, fixed packing illustration; `returns_by_month.csv` holds numeric truth |
| `voice_notes/` | 6 WAV + 6 TXT, plus fixed reply WAV | Two English, two Telugu, two Hindi synthesized notes; `voice_labels.csv` holds reference transcripts and IDs |
| `unboxing_videos/` | 3 MP4, 15 s each | Animated illustrations with synthesized speech, closed box then damaged device; `video_labels.csv` holds reference transcript/duration |
| `guardrails/injection.png` | 1 PNG | Visible instruction attack and fictional 10-digit phone number for OCR/redaction exercise |
| `input_claims.csv` | 20 rows | Input-only batch manifest |
| `eval_set.csv` | 20 rows | Manifest + expected damage/severity/proposed decision/route and retrieval relevance |

These are **illustrations instead of natural product photos**, **animated videos instead of real unboxing footage**, and an **italic-font note instead of authentic handwriting**. The variation and corpus size are intentionally small. They satisfy the teaching workflows and counts, not production evaluation diversity. Replace them with suitably licensed/consented material before a realistic benchmark.

## Claim CSV schema

Paths are relative to `data/`, not the shell working directory. Money is INR; GST is the invoice tax amount. Date is ISO `YYYY-MM-DD`. Blank optional video means no video input.

| Column | Type | Example / validation |
|---|---|---|
| `claim_id` | string | `C001`, unique in supplied files |
| `product` | enum | router, phone, monitor |
| `photo`, `invoice`, `voice`, `video` | path | Local evidence files; video optional |
| `amount` | decimal | Positive, includes GST; should match invoice total |
| `delivery_days` | integer | Non-negative days since delivery |
| `expected_damage_type`, `expected_severity` | enum | Only in evaluation CSV; compare with prediction |
| `expected_decision` | enum | approve, reject, review; pre-human proposal |
| `expected_route` | enum | automatic or human |
| `query`, `relevant_page` | string | Retrieval question and labelled manual page ID |

Some claims deliberately pair a different product photo and invoice, use unreadable evidence, or contain a bad invoice total. These are expected review cases, not dataset corruption. Labels are derived from the explicit fictional policy and manually inspectable source values. The replay demo reads labels by content hash; live inference does not.

Run the CSV batch (requires ffmpeg because five rows include videos):

```bash
python tools/batch.py --csv data/input_claims.csv
```

Output: `runs/batch_results.json`. Human-routed rows remain paused; no batch auto-approval is performed. This is separate from the 20-claim evaluation runner, which uses photo+invoice+voice consistently and evaluates video in the Hour 3 lab.

## Rebuild and provenance

`python tools/build_data.py` regenerates CSV/image/PDF fixtures with Pillow and ReportLab. `pip install -r requirements-media.txt`, then `python tools/build_media.py`, regenerates speech with gTTS (Google Translate TTS, fictional text sent over the network) and videos with ffmpeg. The bundled files run offline on all platforms. Optional `--engine say` uses installed macOS voices, but rejects empty audio; regional voice availability varies. Do not redistribute system voice engines with this project. English order identifiers embedded in Telugu/Hindi references may be pronounced differently by TTS; inspect live ASR against what is actually audible, not just the source text.

To inspect CLIPScore after installing optional dependencies:

```bash
python -m claims.metrics data/claim_photos/claim_01.png "a router with a cracked case"
```

CLIPScore measures semantic image/text alignment; it does not validate damage truth or safe response content.
