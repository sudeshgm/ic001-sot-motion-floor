# SOT-M2 Stage 1 — data preparation log (box CPU, $0). Times IST, 23 Nov 2026. No training or evaluation result exists yet.
- P1 `v1.0-trainval_meta.tgz`: 461,678,030 B, stream sha256 `db48746b…25b` (same as the 21 Nov IC001 stream); all 13 tables match
  `data_manifest/nuscenes_trainval_meta_json_sha256.txt`. `slim_meta.py` → train_track LIDAR_TOP tables: 350 scenes, 14,071 samples,
  136,700 LIDAR_TOP sample_data, 478,816 annotations, 26,647 instances.
- P2 `v1.0-trainval07_blobs.tgz`, streamed, never stored. Attempt 1 (curl | tar pipe) lost the connection at 19,347,340,724 B (curl 56);
  `prep_train_crops.py --url` (HTTP Range reconnect) added. Attempt 2 07:38–08:18: full object 29,534,216,608 B (= Content-Length),
  in-stream sha256 `70287e2d65386bce2d67001ef56f5c0abdd3dd95d1ec404c3e00a39208fa60b7`, 2 reconnects, 16,806 LIDAR_TOP files read.
  train_track scenes found 43, all complete (`data_manifest/sotm2_stage1_archive07_complete_scenes.txt`).
- P3 first 40 complete scenes in seed-0 rank order (`data_manifest/sotm2_stage1_train_scenes.txt`; re-checked against `select_scenes.pick`):
  1,050 Car tracklets, 23,300 keyframes, 221,943 sweeps; crops 3,073,795,380 B (5.3 GB float32 decompressed).
- P4 checkpoint rollout, 8 CPU shards (one tracklet in memory at a time; first launch with all shards loaded hit the 15.6 GB box limit and
  was restarted), finished ≈ 08:52: 1,050/1,050 tracklets, 221,943 rows = sweeps, all finite, unit quaternions, frame 0 = GT (|Δc| = 0).
- P5/P6 `kaggle_inputs/` assembled: 1,280 files, 4.64 GB; checksums `data_manifest/sotm2_stage1_kaggle_inputs_sha256.txt`.
  Eval files verified against the kill-test SOTM2_SHA256SUMS before copying.

## Chunk 1 (T4, 3662 s wall, cap 6900 s): PARTIAL, rc=5
- Inputs sha, env, checkpoint sha: OK. G1 probe: 82 rows, max|dIoU| = 1.0e-06 (pass).
- Training reached step 1000/2000 for C, I and D (500-step blocks of 483–827 s). Stopped because the time left was below the eval reserve.
- A_ft, the full 215-tracklet eval, the row-count check, decide.py and G2 were not run. No verdict is possible yet.
- All 20 output files match SHA256SUMS_outputs.txt (sha256sum -c rc=0).
- Next: a resume chunk with the remaining 1000 steps per arm, then A_ft, eval and decision.

## Chunk 2 (resume, T4, 4805 s wall): COMPLETE, rc=0
- C, I, D resumed from step 1000 and reached 2000/2000. A_ft was skipped for cap (reference only; never blocks the rule, PREREG item 10).
- Row counts: frames=23370, b_sweep_boxes=44693. G1 max|dIoU| = 1.0e-06. G2: A 53.954, B 39.413 (both within ±0.1).
- All 33 output files match SHA256SUMS_outputs.txt. Copies of decision.json, the logs and the training curves are in chunk2/.

## Stage 1 decision (PREREG_SOTM2_STAGE1 §6): INCONCLUSIVE
| cell | D | C | I | Δ = D − max(C,I) | 95% CI | SE | binding |
|---|---|---|---|---|---|---|---|
| pts<10 (2,482 fr) | 41.93 | 46.03 | 15.36 | −4.10 | [−6.11, −2.20] | 1.00 | C |
| moving (1,116 fr) | 29.19 | 23.45 | 31.57 | −2.38 | [−8.04, +2.33] | 2.62 | I |

- GO fails in both cells.
- KILL holds in pts<10 but not in moving, where the CI upper bound of +2.33 is not below +2.0. So the rule gives INCONCLUSIVE.
- The self-aligned buffer (D) is clearly worse than retrained ego-frame accumulation (C) on sparse targets. On moving targets it beats C (+5.7) but not interpolated-box training (I).
- Stage 2 is conditioned on GO and is not triggered.
