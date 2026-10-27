# Hour 1 — photo to structured damage JSON

**Time:** 10:00–11:00; 12 minutes theory + 48 hands-on. **Use case:** the same customer claim used throughout the workshop.

## Outcome and workflow

Photo + question → resize/encode → vision model → Pydantic `Damage` → JSON with confidence/nulls → compare cloud/local. Demo mode replays fixture labels rather than running inference.

## Before running

Complete the root README setup once. Run every command below from the **project root**, not this folder. `requirements.txt` here includes the shared root requirements. `.env.example` documents root configuration; put actual keys in root `.env`. Input is `input.csv`, a local copy of the 10-image manifest. All paths in that CSV are relative to `data/`.

```bash
pip install -r hour_01/requirements.txt
python hour_01/run.py
```

## Timed labs

| Minutes | Task and command | Check |
|---|---|---|
| 0–12 | Theory from `FACILITATOR.md`: modalities, patches/tokens, CLIP vs VLM, cloud vs local, image-token cost | Explain why image similarity and damage reasoning are different tasks |
| 12–20 | Inspect `.env`, run `python tools/preflight.py`; run first image call below | See parsed fields and, in live mode, usage tokens |
| 20–34 | `python -m claims.cli prompts`; `python -m claims.cli vision` | Compare vague and structured prompts on 10 images |
| 34–48 | Inspect the schema and low-quality image; rerun vision | Image 10 has unknown damage and low confidence in demo; unreadable serial is null |
| 48–60 | `python -m claims.cli compare` after enabling live mode and starting Ollama | Table/report contains actual correctness/latency or explicit provider errors |

First single-photo call:

```bash
python -c "from claims.vision import analyze; from claims.core import DATA; print(analyze(DATA/'claim_photos/claim_01.png').model_dump_json(indent=2))"
```

## Files explained

| File | Responsibility |
|---|---|
| `run.py` | Runs this hour's vision artifact and saves `runs/vision.json` |
| `input.csv` | `path, product, damage_type, severity, visible_serial, confidence`; reference labels, not live model inputs |
| `../claims/vision.py` | `analyze()` selects cloud/Ollama or strict fixture replay; `compare()` measures both providers |
| `../claims/core.py` | `Damage` schema, image resizing to at most 1280 px, data URLs, live structured parsing and token/latency log |
| `../data/claim_photos/` | Ten synthetic product illustrations, including deliberately unreadable image 10 |
| `requirements.txt`, `.env.example` | Dependency/configuration references; actual settings load from root `.env` |

## Expected output

`runs/vision.json` contains a mode label and 10 damage objects. Claim 1 in demo:

```json
{"product":"router","damage_type":"cracked_case","severity":"medium","visible_serial":"SN-0001","confidence":0.95}
```

`runs/prompts.json` compares prompts; in demo it lists the prompts without pretending a model ran. `runs/compare.json` reports both providers; demo timings measure fixture lookup and must not be used as inference benchmarks. Live structured calls append token usage and latency to `runs/usage.jsonl`.

## Live cloud/local exercise

Set `APP_MODE=live`, enter `OPENAI_API_KEY`, verify `VISION_MODEL` access. Pull the configured Ollama vision model before class: `ollama pull gemma3:4b`. Start Ollama, then run the comparison. It makes 10 calls to each provider; budget time and cloud costs. Score damage correctness against the CSV and manually inspect product/serial mistakes. Local models have resource/latency costs even without an API token bill.

## Run and check

```bash
python -m pytest -q tests/test_workshop.py -k 'modified_fixture or data_counts'
```

Change `claim_10.png` to a sharper image only in live mode; observe confidence and null handling. Do not interpret model-reported confidence as calibrated probability. A dented box alone is not proof of product damage. Labels and filenames are excluded from live vision prompts. Next hour adds invoice validation and warranty evidence.

hour_01/run.py
    ↓ selects the "vision" lab
claims/cli.py
    ↓ reads data/photo_labels.csv
    ↓ takes each row's image path
claims/vision.py → analyze(image_path)
    ↓
10 results printed and saved to runs/vision.json

