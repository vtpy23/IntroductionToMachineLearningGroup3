# Published experiment evidence

These are byte-identical, lightweight copies of existing completed runs. No experiment was rerun to create this folder. `manifest.json` records each original local path, published path, SHA-256 and size.

Each run includes its real config, summary and JSONL history; phase tables and official-output comparisons are included where present. `tracking.json` is the original local synchronization verification metadata. A summary may retain `tracking_mode=offline`, a null URL or `submission_ready=false`: it is intentionally not rewritten after synchronization. Live verified URLs/states are recorded separately in the slide evidence and mapping.

- [Mapping: config, result, real W&B URL and slide](../../reports/milestone2_final/EXPERIMENT_TRACEABILITY.md)
- [Verified snapshot and source-code hashes](../../reports/milestone2_final/assets/verified_evidence.json)
- [Benchmark table](../reproduction/RESULTS.md)
- [Synthetic mechanisms](../empirics/)

The CIFAR-100 benchmark is **seed 0 only**. Three-seed synthetic tests are separate evidence and do not establish benchmark mean/std. Raw images, feature arrays, model weights/checkpoints, credentials and W&B binary logs remain local and ignored by Git. Dataset revision, class order and checkpoint checksum are retained in configs; use the documented pipeline to reproduce weights/features.

The final slide builder and read-only audit can fall back to these snapshots when the original `outputs/` directory is absent in a fresh clone.
