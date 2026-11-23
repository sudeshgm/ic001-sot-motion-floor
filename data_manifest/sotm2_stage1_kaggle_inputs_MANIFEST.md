# sotm2-stage1-inputs (private; nuScenes-derived, CC BY-NC-SA 4.0 + nuScenes Terms of Use: do not redistribute)
| Folder | Files | Bytes | Content |
|---|---|---|---|
| eval/ | 218 | 1,534,882,802 | 215 mini kill-test crops (± 10 m), index.json, bins.csv, probe_ref_frames.csv |
| train/ | 1,052 | 3,073,795,380 | 1,050 train_track Car crops (± 5 m, 40 scenes), index.json, sotm2_stage1_train_scenes.txt |
| train/rollout/ | 8 | 7,915,533 | checkpoint sweep-rate rollout boxes, 1,050 tracklets / 221,943 sweeps |
| ckpt/ | 1 | 27,073,489 | mmtrack_nuscenes_car.ckpt (sha256 3b19f52c…) |
| code/ | 1 | 16,268 | ic001_sotm2_code.tgz = git archive d040ba4 gpu_jobs/sotm2 |
| **total** | **1,280 + SOTM2S1_SHA256SUMS.txt + MANIFEST.md** | **4,643,684,006 B (≈ 4.64 GB)** | |
Verify: `sha256sum -c SOTM2S1_SHA256SUMS.txt --quiet` (1,280 entries).
