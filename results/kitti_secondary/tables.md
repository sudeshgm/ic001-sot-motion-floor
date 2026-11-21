# Secondary analyses (KITTI Car) — 21 November 2026

**Label: SECONDARY / post-primary.** Nothing in this file is part of the frozen GO / KILL decision rule, the frozen floor, or frozen V1. The primary KITTI-side decision in `results/kitti_decision/` is unchanged (KITTI-side KILL stands). Formal first-test GO/KILL still waits on nuScenes.

- Pre-registration: `PREREG.md`, frozen at `e31629c99566bd989094d3a3922374863f0ac163`. This file does not edit it.
- Spec: `SECONDARY_ANALYSES.md` #1 (ego-motion split + oxts-compensated M2-Track) and #2 (BAT progress anchor / R_progress).
- Protocol: standard one-pass evaluation (protocol a / `ope`) is the headline; re-init is reported as well.
- Floor: pre-registered `cv_snap` in `results/kitti/` (unchanged).
- Learned boxes: GPU Bot secondary outputs in `/workspace/gpubot/ic001-sot-kitti/outputs/sec_v1/` (M2-Track-oxts, BAT), SHA-256 verified. Primary M2-Track and MBPTrack CSVs from `outputs/v1/` are reused only for the oxts-minus-plain contrast and for R_progress (BAT → best learned). Re-scored with `ic001` metrics (same path as `results/kitti_decision/`). Best learned remains MBPTrack with the GT-convention yaw.
- Bins: the same single-axis point bins (`<50`, `50–199`, `≥200`) and 3D world-frame motion bins (`<0.5 m`, `≥0.5 m`) as the frozen decision; frame 0 excluded from every per-bin score; bootstrap 10,000 tracklet resamples, seed 0, percentile 95% CI.
- Ego axis (analysis #1 only): world-frame **BEV** displacement crossed with sensor-frame **BEV** displacement, threshold 0.5 m, matching the 21 Nov GT census in the spec (static/static 2,474 frames / 36 tracklets; ego-only 2,282 / 98; co-moving 1,065 / 11, under-powered; both-moving 483 / 14, under-powered). Claims need ≥30 tracklets; only the first two cells qualify.
- Aggregate tables and JSON only. Per-frame CSVs are KITTI-derived and are **not** committed.
- Computed at 2026-11-21 21:16:05 IST.

## Checksums

Every hash listed in the delivery brief, and every file in `SHA256SUMS_all.txt`, matched. Primary `m2track_kitti_car.csv` also matched `SHA256SUMS_outputs.txt`.

## Overall Success / Precision (ic001 rescore)

| Method | Protocol | Success | Precision | Native S/P | ΔS vs native |
|---|---|---:|---:|---|---:|
| floor (cv_snap) | ope | 23.86 | 30.18 | — | — |
| last_box | ope | 20.22 | 18.61 | — | — |
| cv_snap_noego | ope | 19.26 | 22.03 | — | — |
| M2-Track | ope | 67.42 | 81.01 | — | — |
| M2-Track-oxts | ope | 66.45 | 79.05 | 66.46/79.08 | -0.01 |
| BAT | ope | 63.17 | 76.07 | 63.18/76.09 | -0.01 |
| MBPTrack (GT-convention yaw) | ope | 73.66 | 85.16 | — | — |
| floor (cv_snap) | reinit | 89.09 | 94.88 | — | — |
| last_box | reinit | 81.51 | 81.58 | — | — |
| cv_snap_noego | reinit | 89.22 | 94.69 | — | — |
| M2-Track | reinit | 82.17 | 92.21 | — | — |
| M2-Track-oxts | reinit | 82.31 | 92.13 | 82.32/92.16 | -0.01 |
| BAT | reinit | 83.79 | 92.08 | 83.80/92.10 | -0.01 |
| MBPTrack (GT-convention yaw) | reinit | 80.48 | 91.10 | — | — |

ic001 Success / Precision on every reported group for M2-Track-oxts and BAT match GPU Bot's `eval_bins_kitti_Car_secondary.json` with max |Δ Success| = 0 and max |Δ Precision| = 0.

### BAT vs published numbers (informational only; not a V1 gate)

- Our ic001 Success / Precision (ope): **63.17 / 76.07** (native 63.18 / 76.09).
- BAT paper (ICCV 2021) KITTI Car: 60.5 / 77.7; |Δ Success| vs paper = **2.67**.
- Open3DSOT README checkpoint (`bat_kitti_car.ckpt`): 65.37 / 78.88; |Δ Success| vs README = **2.20**. The README asks for CUDA 10.x to reproduce that figure; this run was on a free Kaggle T4 (CUDA 11/12). BAT is used only as a relative anchor.

## Per-bin gaps vs the frozen floor (protocol a / ope)

Gap = method − floor (`cv_snap`). Same bins and bootstrap as the frozen KITTI decision. These gaps are diagnostic; they do not re-apply the GO/KILL rule.

| Method | Bin | Floor | Learned | Gap | 95% CI | n frames | n tracklets | Under-powered? |
|---|---|---:|---:|---:|---|---:|---:|---|
| M2-Track-oxts | pts0 (<50) | 26.60 | 53.10 | 26.49 | [19.62, 33.83] | 2344 | 99 | no |
| M2-Track-oxts | pts1 (50–199) | 17.59 | 72.33 | 54.74 | [42.16, 63.10] | 1691 | 107 | no |
| M2-Track-oxts | pts2 (≥200) | 21.80 | 74.19 | 52.40 | [40.87, 63.02] | 2269 | 91 | no |
| M2-Track-oxts | motLo (<0.5 m, 3D world) | 24.64 | 66.97 | 42.33 | [33.85, 49.98] | 4751 | 115 | no |
| M2-Track-oxts | motHi (≥0.5 m, 3D world) | 15.77 | 62.41 | 46.64 | [17.70, 64.54] | 1553 | 17 | yes (<30 tracklets) |
| BAT | pts0 (<50) | 26.60 | 54.65 | 28.05 | [22.03, 33.96] | 2344 | 99 | no |
| BAT | pts1 (50–199) | 17.59 | 70.99 | 53.40 | [41.33, 62.45] | 1691 | 107 | no |
| BAT | pts2 (≥200) | 21.80 | 64.29 | 42.49 | [31.17, 54.33] | 2269 | 91 | no |
| BAT | motLo (<0.5 m, 3D world) | 24.64 | 63.30 | 38.66 | [31.56, 45.78] | 4751 | 115 | no |
| BAT | motHi (≥0.5 m, 3D world) | 15.77 | 60.06 | 44.29 | [18.39, 61.70] | 1553 | 17 | yes (<30 tracklets) |
| M2-Track | pts0 (<50) | 26.60 | 54.59 | 27.99 | [21.87, 34.00] | 2344 | 99 | no |
| M2-Track | pts1 (50–199) | 17.59 | 72.49 | 54.90 | [44.00, 61.95] | 1691 | 107 | no |
| M2-Track | pts2 (≥200) | 21.80 | 75.26 | 53.46 | [42.06, 63.95] | 2269 | 91 | no |
| M2-Track | motLo (<0.5 m, 3D world) | 24.64 | 68.10 | 43.45 | [35.17, 50.88] | 4751 | 115 | no |
| M2-Track | motHi (≥0.5 m, 3D world) | 15.77 | 62.96 | 47.19 | [23.88, 62.76] | 1553 | 17 | yes (<30 tracklets) |

## M2-Track-oxts minus plain M2-Track (does ego-compensation change the score?)

Same bins and bootstrap. A positive gap means the oxts-compensated crop helps.

| Slice | Δ Success (oxts − plain) | 95% CI | n frames | n tracklets | Under-powered? |
|---|---:|---|---:|---:|---|
| overall (incl. frame 0) | -0.96 | [-4.18, 1.09] | 6424 | 120 | no |
| overall (binned, excl. frame 0) | -0.98 | [-4.21, 1.17] | 6304 | 119 | no |
| pts0 (<50) | -1.50 | [-5.09, 1.81] | 2344 | 99 | no |
| pts1 (50–199) | -0.16 | [-3.69, 2.14] | 1691 | 107 | no |
| pts2 (≥200) | -1.06 | [-4.39, 0.93] | 2269 | 91 | no |
| motLo (<0.5 m, 3D world) | -1.12 | [-4.37, 0.83] | 4751 | 115 | no |
| motHi (≥0.5 m, 3D world) | -0.55 | [-8.10, 2.96] | 1553 | 17 | yes (<30 tracklets) |
| ego: static_static | -1.84 | [-6.66, 0.54] | 2474 | 36 | no |
| ego: ego_only | -0.34 | [-2.65, 1.53] | 2282 | 98 | no |
| ego: co_moving | 0.23 | [-9.78, 3.17] | 1065 | 11 | yes (<30 tracklets) |
| ego: both_moving | -2.30 | [-8.47, 5.35] | 483 | 14 | yes (<30 tracklets) |

## #1 Ego-motion split (protocol a / ope)

Cells are GT-defined (BEV world × BEV sensor, 0.5 m). Co-moving and both-moving are under-powered and cannot drive a claim.

### Success by ego cell

| Cell | n frames | n tracklets | Floor | No-ego floor | M2-Track | M2-Track-oxts | BAT | MBPTrack |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| static_static | 2474 | 36 | 24.76 | 22.80 | 68.37 | 66.53 | 59.99 | 75.80 |
| ego_only | 2282 | 98 | 24.49 | 13.42 | 67.68 | 67.35 | 66.79 | 72.41 |
| co_moving | 1065 | 11 | 14.39 | 16.49 | 66.81 | 67.03 | 66.84 | 74.41 |
| both_moving | 483 | 14 | 18.83 | 15.08 | 54.97 | 52.68 | 45.57 | 60.84 |

### Gaps vs floor in ego cells

| Method | Cell | Gap | 95% CI | n tracklets | Under-powered? |
|---|---|---:|---|---:|---|
| M2-Track | static_static | 43.61 | [28.05, 55.59] | 36 | no |
| M2-Track | ego_only | 43.19 | [37.36, 48.73] | 98 | no |
| M2-Track | co_moving | 52.41 | [18.94, 67.14] | 11 | yes (<30 tracklets) |
| M2-Track | both_moving | 36.15 | [23.91, 50.23] | 14 | yes (<30 tracklets) |
| M2-Track-oxts | static_static | 41.77 | [25.77, 54.06] | 36 | no |
| M2-Track-oxts | ego_only | 42.86 | [37.11, 48.36] | 98 | no |
| M2-Track-oxts | co_moving | 52.64 | [12.71, 69.70] | 11 | yes (<30 tracklets) |
| M2-Track-oxts | both_moving | 33.85 | [18.98, 50.65] | 14 | yes (<30 tracklets) |
| BAT | static_static | 35.22 | [23.12, 46.82] | 36 | no |
| BAT | ego_only | 42.30 | [36.57, 47.78] | 98 | no |
| BAT | co_moving | 52.45 | [15.15, 69.00] | 11 | yes (<30 tracklets) |
| BAT | both_moving | 26.75 | [17.54, 37.43] | 14 | yes (<30 tracklets) |
| MBPTrack (GT-convention yaw) | static_static | 51.04 | [37.43, 60.91] | 36 | no |
| MBPTrack (GT-convention yaw) | ego_only | 47.92 | [41.88, 53.69] | 98 | no |
| MBPTrack (GT-convention yaw) | co_moving | 60.01 | [22.96, 73.53] | 11 | yes (<30 tracklets) |
| MBPTrack (GT-convention yaw) | both_moving | 42.02 | [27.67, 56.14] | 14 | yes (<30 tracklets) |

### Δgap = (learned − floor) in ego-only minus the same in static/static

Negative Δgap means the learned−floor gap is smaller in ego-only frames than in static/static frames (the H-ego direction). Also reported within point-bin strata.

| Method | Stratum | Δgap | 95% CI | CI excludes 0? | ego-only gap (n trk) | static/static gap (n trk) | Under-powered? |
|---|---|---:|---|---|---|---|---|
| M2-Track | overall | -0.41 | [-12.74, 14.71] | no | 43.19 (98) | 43.61 (36) | no |
| M2-Track | pts0 (<50) | -10.17 | [-24.08, 4.53] | no | 20.28 (80) | 30.45 (19) | yes |
| M2-Track | pts1 (50–199) | -16.84 | [-27.45, 1.43] | no | 43.79 (89) | 60.63 (25) | yes |
| M2-Track | pts2 (≥200) | 19.44 | [0.06, 39.20] | yes | 62.92 (73) | 43.49 (24) | yes |
| M2-Track-oxts | overall | 1.09 | [-11.47, 16.68] | no | 42.86 (98) | 41.77 (36) | no |
| M2-Track-oxts | pts0 (<50) | -10.18 | [-23.95, 4.32] | no | 19.70 (80) | 29.89 (19) | yes |
| M2-Track-oxts | pts1 (50–199) | -15.10 | [-26.66, 5.00] | no | 42.85 (89) | 57.95 (25) | yes |
| M2-Track-oxts | pts2 (≥200) | 22.03 | [2.59, 42.18] | yes | 63.26 (73) | 41.23 (24) | yes |
| BAT | overall | 7.07 | [-4.55, 18.98] | no | 42.30 (98) | 35.22 (36) | no |
| BAT | pts0 (<50) | -10.43 | [-22.95, 2.71] | no | 24.23 (80) | 34.65 (19) | yes |
| BAT | pts1 (50–199) | -11.12 | [-24.12, 6.94] | no | 42.08 (89) | 53.21 (25) | yes |
| BAT | pts2 (≥200) | 32.47 | [14.09, 46.67] | yes | 58.38 (73) | 25.91 (24) | yes |
| MBPTrack (GT-convention yaw) | overall | -3.12 | [-13.85, 10.54] | no | 47.92 (98) | 51.04 (36) | no |
| MBPTrack (GT-convention yaw) | pts0 (<50) | -13.91 | [-25.72, -0.86] | yes | 22.99 (80) | 36.90 (19) | yes |
| MBPTrack (GT-convention yaw) | pts1 (50–199) | -13.27 | [-24.96, 6.32] | no | 50.07 (89) | 63.34 (25) | yes |
| MBPTrack (GT-convention yaw) | pts2 (≥200) | 14.11 | [-3.24, 34.20] | no | 68.26 (73) | 54.15 (24) | yes |

### Validity check: ego-compensated floor minus no-ego floor

The no-ego floor (frozen control 3) should collapse versus the ego-compensated floor in ego-only frames.

| Cell | Floor − no-ego | 95% CI | Floor | No-ego |
|---|---:|---|---:|---:|
| static_static | 1.96 | [-1.69, 6.03] | 24.76 | 22.80 |
| ego_only | 11.07 | [7.27, 15.17] | 24.49 | 13.42 |
| co_moving | -2.10 | [-12.10, 2.10] | 14.39 | 16.49 |
| both_moving | 3.75 | [-0.06, 8.78] | 18.83 | 15.08 |

### Pre-specified #1 rule (applied to uncompensated M2-Track Δgap + oxts gain)

**Verdict: NO-GO.** SECONDARY #1 NO-GO: |Δgap| < 2 and the oxts-compensated gain is <1. Ego pose is not the source of the learned−floor gap (fairness objection defused).

oxts-compensated M2-Track gain: ego-only **-0.34** [-2.65, 1.53]; overall (incl. frame 0) **-0.96** [-4.18, 1.09].

## #2 BAT progress anchor (R_progress), protocol a / ope

R_progress = (share of the BAT → best-learned gain that sits in primary-hard frames) / (share of frames that are primary-hard), using the frozen P5 formula. Best learned is MBPTrack (GT-convention yaw), as in the primary analysis. Shown next to the already-reported floor → best R.

| Contrast | Total gain (binned) | R | 95% CI | CI excludes 1? |
|---|---:|---:|---|---|
| BAT → MBPTrack (R_progress) | 10.69 | 0.497 | [0.173, 0.882] | yes |
| Floor → MBPTrack (P5, restated) | — | 0.833 | [0.612, 0.987] | — |

KITTI-only. The pre-specified informative/uninformative call needs BAT and best-learned on both KITTI and nuScenes. Formal #2 is also labelled moot for the paper as planned if a formal KILL is later called; this is a diagnostic write-up.
On KITTI alone, the interval is entirely at or below 1, in the H-refine direction (recent gains are not concentrated in hard frames). This is not a formal two-dataset call.

## Published per-bin context (zero-compute, not measured here)

### TrackAny3D Table 3 (arXiv:2507.19908)

Waymo Vehicle, KITTI-trained, Easy / Medium / Hard tracklet thirds, Success. Caveat: thirds are by tracklets, not frames, and the table is cross-dataset.

| Method | Easy | Medium | Hard |
|---|---:|---:|---:|
| P2B | 57.1 | 52.0 | 47.9 |
| BAT | 61.0 | 53.3 | 48.9 |
| M2-Track | 68.1 | 58.6 | 55.4 |
| MBPTrack | 68.5 | 58.4 | 57.6 |
| TrackAny3D | 72.6 | 60.5 | 57.5 |

P2B→TrackAny3D gains +15.5 / +8.5 / +9.6, rough R ≈ 0.86. BAT→MBPTrack gains +7.5 / +5.1 / +8.7, rough R ≈ 1.23. The published pairs straddle R = 1.

### TFTrack Table IX (nuScenes Car, tracklet-level, Success / Precision)

| Method | Mean | Late 25% | Sp. init. (<10 first-frame pts) | Fast start (init >10 m/s) |
|---|---|---|---|---|
| M2-Track | 60.81 / 68.73 | 45.38 / 53.77 | 51.23 / 60.46 | 14.38 / 13.05 |
| MBPTrack | 65.72 / 73.06 | 51.56 / 60.14 | 57.98 / 66.09 | 12.59 / 11.50 |
| BEVTrack | 67.72 / 73.77 | 52.83 / 60.98 | 62.37 / 69.16 | 9.75 / 7.79 |
| TFTrack | 67.79 / 74.46 | 54.27 / 63.16 | 61.76 / 69.45 | 15.19 / 14.17 |

BEVTrack sparse-subset tables were listed as a further source in the spec; a complete extraction was not already in the existing notes and is not invented here.

## Files

- `results/kitti_secondary/kitti_secondary.json` — aggregate numbers only.
- `results/kitti_secondary/tables.md` — this file.
- `results/kitti_secondary/RUNLOG.md` — run log.
- Per-frame CSVs remain only under `/workspace/gpubot/ic001-sot-kitti/outputs/` and are not in the repo.

