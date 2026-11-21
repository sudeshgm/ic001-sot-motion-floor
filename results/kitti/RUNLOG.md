# KITTI floor run (CPU) — RUNLOG

- PREREG frozen at e31629c99566bd989094d3a3922374863f0ac163 (`PREREG.githash`); code at branch `cpu-agent`, commit with this file.
- Data: `/workspace/ic001/data/kitti` (DATA.md, `data_manifest/kitti_sha256.txt`). Open3DSOT test split scenes 0019–0020.
- Tracklets/frames (match Open3DSOT counts cited in PREREG_DRAFT): Car 120 / 6,424; Pedestrian 62 / 6,088; Van 16 / 1,248; Cyclist 8 / 308.
- Commands (per class C): `python -m ic001.run floor --dataset kitti --root /workspace/ic001/data/kitti --category C --out runs/kitti_C_floor_{A,B}.csv`; `python -m ic001.run evaluate ... --floor runs/kitti_C_floor_A.csv`; `python -m ic001.run sanity` (Car, Pedestrian).
- Merge rule (decided from GT only, `scripts/gt_bin_census.py`, before any score was looked at): every point bin of Car and Pedestrian has ≥ 30 distinct tracklets → **no merge**; KITTI bins stay <50 / 50–199 / ≥200.
- Under-powered (< 30 tracklets): Car high-motion bin (17 tracklets, 24.6% of binned frames); Pedestrian high-motion (6 frames); all Van and Cyclist bins (Other).
- V3 determinism: two independent runs per class are byte-identical (`V3_determinism_sha256.txt`). PASS.
- V4 ground filter (20 random frames, seed 0, GT box + 0.5 m BEV): Car median 0.126 removed (0.00–0.52), Pedestrian median 0.107 (0.00–0.34). Reported, not tuned.
- Deviations: none. The CV control is reported under re-init only (identical to last box under OPE, PREREG (d)).
- Learned trackers not run yet (GPU jobs pending) → decision rule NOT applied.

## 2026-11-21 — POST-HOC, SECONDARY, NOT PRE-REGISTERED velocity-heading check
See `results/kitti_POSTHOC_velocity_heading/RUNLOG.md`. The frozen results above are unchanged and stay primary.

## 2026-11-21 17:18 IST — KITTI learned-tracker rescore, V1, and KITTI-side decision

- GPU Bot primary outputs (`/workspace/gpubot/ic001-sot-kitti/outputs/v1/`, KITTI 0019–0020) had every file in `SHA256SUMS_outputs.txt` verified (all OK). Pins recorded by GPU Bot: ic001 `666a9e0`, Open3DSOT `f08451d`, MBPTrack3D `e5670d1`. Scoring code used here (`ic001` metrics / bins / IoU) is unchanged from that pin except for later additive oxts helpers that are not on the scoring path.
- Per-frame CSVs were re-scored with `ic001` against the same GT as the frozen floor (`results/kitti/`). Aggregate outputs only were written to `results/kitti_decision/`. Raw per-frame CSVs were not copied into the repo (KITTI-derived, not for publication).
- MBPTrack primary scores use the GT-convention yaw (`mbptrack_yawalt`) from the side `*.rawcam.csv` files, as specified by GPU Bot after the harness yaw self-check failed (7.8e-3 rad vs 1e-4; centres match exactly). This is a recorded deviation; see `RESULTS.md` and `results/kitti_decision/mbptrack_yaw_deviation.json`. The yawalt rescore changes overall Success by at most 0.088; three tiny non-headline cells exceed the “at most 0.2” headline statement and are listed there.
- V1 (approved addendum, KITTI Car, protocol a): M2-Track **PASS** (67.42 vs paper 65.5 / checkpoint 67.43); MBPTrack **PASS** (73.66 vs paper 73.4). Informational: M2-Track Pedestrian PASS (60.60 vs 61.5 / 60.61); MBPTrack Pedestrian FAIL (65.99 vs paper 68.6; not a gate). Formal record: `RESULTS.md`.
- Our ic001 Success/Precision match GPU Bot's `eval_bins_kitti_*.json` exactly (max |Δ| = 0). Offsets vs GPU Bot's native Car headline numbers (M2 67.43/81.04, MBP 73.67/85.19) are ≤ 0.10 Success and are the already-noted IoU-implementation difference, not a rescore mismatch.
- Decision rule applied to KITTI only (Car, protocol a, single-axis bins, frame 0 excluded, no merge, 10,000 tracklet bootstrap, seed 0). Learned = best family by point estimate per bin (MBPTrack in every Car decision bin). Per-family gaps (M2-Track − floor and MBPTrack − floor) are also reported. **KITTI side of rule: KILL conditions hold on every eligible decision bin; formal KILL needs nuScenes, which has not been run.** Secondary R (Car, floor → MBPTrack) = 0.833, 95% CI [0.612, 0.987]; P5 not supported. Full tables in `results/kitti_decision/tables.md`.
- `PREREG.md` and `PREREG_ADDENDUM_2026-11-21.md` were not edited. Frozen floor outputs in `results/kitti/` were not changed.
