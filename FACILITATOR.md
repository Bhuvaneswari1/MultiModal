# Four-hour facilitator guide

## Day-before preparation (outside 240 minutes)

Use Python 3.11/3.12, install root/optional dependencies, ffmpeg/Tesseract, pull Ollama model, warm CLIP, verify each API model and quota, and test LangSmith with fictional data only. Run preflight and pytest. Open the three manuals, scanned invoice, Telugu/Hindi WAVs and three MP4s before class. Keep demo mode as an explicitly labelled wiring fallback if cloud latency/access prevents live work. Print or project each hourly README timeline.

## Hour 1 theory — 12 minutes

* 0–3: Define modalities: text, image, audio, video, documents. A PDF can hold both selectable text and scanned page images. Use claim 1 to connect visible evidence with a customer's textual complaint.
* 3–6: Diagram `image → patches/vision encoder → token-like representations → language decoder → answer`. Distinguish this conceptual model from provider-specific internals. Resolution affects evidence detail and often token usage. Resize deliberately; tiny serial text may become unreadable.
* 6–9: Contrast CLIP shared embedding-space retrieval with VLM instruction following/structured reasoning. Similarity is not a warranty decision. API vs local choices involve latency, hardware, privacy and billing.
* 9–12: Explain schema fields, null vs invented serial, unknown vs low confidence, and why confidence must be calibrated on labelled data. Inspect input and output before the first lab.

Concept map: `modalities → representation → (similarity retrieval | structured understanding) → evidence + uncertainty`.

Use Hour 1's 8/14/14/12-minute lab split. Ask learners to identify one damage misclassification and one unreadable-field risk. Checkpoint: ten valid JSON objects, explicit provider comparison caveats.

## Hour 2 theory — 12 minutes

* 0–3: OCR recovers characters; a VLM can combine layout/visual cues. Neither replaces arithmetic validation. A plausible invoice answer can still be financially inconsistent.
* 3–6: Read chart axes, units and labels. Join returned values to authoritative CSV numbers. Explain image/text vectors, cosine similarity and top-k retrieval.
* 6–9: Draw `manual page → text + diagram caption → embeddings → index → retrieval → grounded answer`. Compare with direct image embeddings and ColPali-style page-image retrieval. Captions may lose layout/details; page-image approaches increase model/storage needs.
* 9–12: A citation must identify file, page and figure, and support the specific sentence. Correct source IDs alone are insufficient. Use abstention for questions not answered in policy.

Concept map: `PDF/chart/image → extraction/embedding → validation/retrieval → cited answer`.

Use 14/10/10/14-minute lab split. Prewarm optional model/index to fit the live exercises. Checkpoint: invoice 8 fails totals; chart returns April/30; inspect top-5 CLIP images; verify policy citation against a manual.

## Hour 3 theory — 12 minutes

* 0–3: ASR maps audio to text; vocabulary, noise, accents and mixed-language identifiers matter. Word/segment timestamps help align a timeline. Our plain-text API path does not emit word timestamps.
* 3–6: TTS produces synthetic speech from text. Voice and rate change user experience; label synthetic speech. Real-time systems involve turn detection, streaming latency and interruption handling beyond this batch exercise.
* 6–9: Draw `video → sampled frames + extracted audio → VLM + ASR → timestamped observations`. Sampling can miss short events. Native video models are an alternative with different cost/context tradeoffs.
* 9–12: Diffusion/modern image generators iteratively synthesize visual content; precise architecture varies. Editing can alter evidence accidentally. Use generated graphics for support instructions, never original claim proof. Compare specialized pipelines with native any-to-any models.

Concept map: `voice/video → transcript + frames → timeline/ticket → written reply → spoken reply/support illustration`.

Use 12/8/16/12-minute lab split. Checkpoint: multilingual transcripts, live voice/rate comparison, three timestamped frames plus audio, reviewed generated artwork. Keep a clear distinction between source speech text and what the synthetic voice actually pronounces.

## Hour 4 theory — 12 minutes

* 0–3: Draw the graph from Hour 4 README. Modality tools extract evidence; policy decides; a human reviews uncertainty/high values. Interruptions must checkpoint state and resume the same thread; a boolean confirmation in a local variable is insufficient.
* 3–6: Field accuracy = matching fields/all fields; per-class F1 combines precision/recall. WER=(substitutions+deletions+insertions)/reference words; CER uses characters. Recall@k=labelled relevant items found/relevant items. CLIPScore compares image-text semantic alignment. Hallucination rate requires a clear unsupported-claim rubric and adequate evaluation sample; an LLM judge is a fallible assessor.
* 6–9: PII may exist in pixels/audio, not just text. Uploaded evidence can contain prompt injection. Show redaction/detection failures. Separate instructions from evidence and enforce refund policy in deterministic code. Raw inputs and tracing have retention/privacy implications.
* 9–12: Measure latency/token use by modality. Content-hash caches must include model/prompt/schema versions and tenant isolation, TTL, consent and invalidation; caching is discussed here, not a hidden live-response cache. Resizing and frame limits bound cost. Explain API/UI/container boundaries, rate limits and deployment hardening. This UI is batch, not token streaming.

Concept map: `evidence → tools → policy → human checkpoint → draft response`, observed with `traces + metrics` and constrained by `validation + guardrails`.

Use 16/14/6/12-minute lab split. Checkpoint: high-value claim stays pending; reviewer can reject; restart/resume succeeds; evaluation labels remain distinct from predictions; API/UI sample completes.

## Completion rubric

Learner can run each hourly artifact, name its inputs/outputs, explain one uncertainty/failure case, cite a manual page, distinguish demo replay from live inference, and demonstrate that a high-value claim cannot finish without a reviewer. Submit the JSON artifacts, evaluation report and one reviewed support graphic. Never submit real keys or personal data.
