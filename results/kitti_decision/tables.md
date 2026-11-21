# KITTI decision tables (KITTI only)

Generated 2026-11-21 17:18 IST. Aggregate scores only; no per-frame CSVs.
Scope: **KITTI only** (Open3DSOT test scenes 0019–0020). nuScenes floor and learned scores are not in this file.
Floor = pre-registered `cv_snap`. Learned families = M2-Track and MBPTrack with GT-convention yaw (`mbptrack_yawalt`).
Bootstrap: tracklet resampling, 10,000 draws, seed 0, percentile 95% CI. Frame 0 is included in overall Success/Precision and excluded from every per-bin score (PREREG choice g).

## V1 reproduction (protocol a, KITTI)

| Tracker | Class | Role | Our Success / Precision | Paper | Δ paper | Checkpoint | Δ ckpt | V1 |
|---|---|---|---:|---:|---:|---:|---:|---|
| M2-Track | Car | V1 gate | 67.42 / 81.01 | 65.50 | 1.92 | 67.43 | 0.01 | PASS |
| MBPTrack (GT-convention yaw) | Car | V1 gate | 73.66 / 85.16 | 73.40 | 0.26 | — | — | PASS |
| M2-Track | Pedestrian | informational | 60.60 / 89.37 | 61.50 | 0.90 | 60.61 | 0.01 | PASS |
| MBPTrack (GT-convention yaw) | Pedestrian | informational | 65.99 / 90.91 | 68.60 | 2.61 | — | — | FAIL |

V1 gates on KITTI Car only, under the approved addendum: a tracker passes if its ic001-rescored Success is within 1.0 of either the paper value or a documented checkpoint value (MBPTrack: paper value only). Pedestrian rows are informational (same tolerance, not a gate).

## Recorded deviation: MBPTrack yaw convention

MBPTrack harness camera→velodyne yaw-convention self-check failed: frame-0 yaw max error 7.75e-3–7.97e-3 rad (reported as 7.8e-3 rad) vs the harness tolerance of 1e-4 rad. Centres match exactly. The harness CSV was left unchanged. Primary MBPTrack scores use the GT-convention yaw rescore (mbptrack_yawalt: yaw = -(rotation_y + π/2) from the raw camera box). GPU Bot reported that the yawalt rescore changes results by at most 0.2. That holds for every overall score (largest |Δ Success| = 0.088 on Car ope) and for every Car group (largest |Δ Success| = 0.172). Precision is unchanged (centres match). Three tiny non-headline cells exceed 0.2: Pedestrian `mot:motHi` (6 frames, ΔS = −0.83), Pedestrian `grid:p2|mHi` (4 frames, ΔS = −1.25), and Cyclist `pts:pts0` / `hard_primary` (19 frames, ΔS = +0.26).

## Overall Success / Precision (protocol a, includes frame 0)

| Class | Method | Success | Precision | n frames | vs GPU Bot ic001 ΔS / ΔP | vs native ΔS / ΔP |
|---|---|---:|---:|---:|---:|---:|
| Car | floor (cv_snap) | 23.86 | 30.18 | 6424 | — | — |
| Car | M2-Track | 67.42 | 81.01 | 6424 | +0.00e+00 / +0.00e+00 | -0.01 / -0.03 |
| Car | MBPTrack (GT-convention yaw) | 73.66 | 85.16 | 6424 | +0.00e+00 / +0.00e+00 | -0.01 / -0.03 |
| Car | MBPTrack (harness yaw) | 73.57 | 85.16 | 6424 | +0.00e+00 / +0.00e+00 | -0.10 / -0.03 |
| Pedestrian | floor (cv_snap) | 26.19 | 48.74 | 6088 | — | — |
| Pedestrian | M2-Track | 60.60 | 89.37 | 6088 | +0.00e+00 / +0.00e+00 | -0.01 / -0.02 |
| Pedestrian | MBPTrack (GT-convention yaw) | 65.99 | 90.91 | 6088 | +0.00e+00 / +0.00e+00 | -0.01 / -0.02 |
| Pedestrian | MBPTrack (harness yaw) | 66.02 | 90.91 | 6088 | +0.00e+00 / +0.00e+00 | +0.02 / -0.02 |
| Van | floor (cv_snap) | 29.44 | 30.71 | 1248 | — | — |
| Van | MBPTrack (GT-convention yaw) | 60.69 | 71.91 | 1248 | +0.00e+00 / +0.00e+00 | -0.04 / -0.02 |
| Van | MBPTrack (harness yaw) | 60.71 | 71.91 | 1248 | +0.00e+00 / +0.00e+00 | -0.02 / -0.02 |
| Cyclist | floor (cv_snap) | 57.21 | 81.12 | 308 | — | — |
| Cyclist | MBPTrack (GT-convention yaw) | 76.69 | 94.12 | 308 | +0.00e+00 / +0.00e+00 | -0.06 / -0.05 |
| Cyclist | MBPTrack (harness yaw) | 76.70 | 94.12 | 308 | +0.00e+00 / +0.00e+00 | -0.05 / -0.05 |

GPU Bot's headline Car standard-protocol native numbers were M2-Track 67.43/81.04 and MBPTrack 73.67/85.19. ic001 rescoring is expected to differ slightly from those native figures because of IoU implementation differences (GPU Bot reported offsets ≤ 0.1). A mismatch against GPU Bot's own ic001 `eval_bins_kitti_*.json` would be unexpected.

## Decision-bin gaps (protocol a) — best learned − floor

Decision bins are single-axis (PREREG choice f). Learned = best family by point-estimate Success in that bin, before the bootstrap (choice m). Cells with fewer than 30 tracklets cannot drive GO/KILL. Shares are of binned frames (frame 0 excluded).

### Car — best learned (headline for Car)

| Bin | Best family | Floor | Learned | Gap | 95% CI | n frames | Share of binned | n tracklets | Flags |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| pts:pts0 | MBPTrack (GT-convention yaw) | 26.60 | 60.07 | 33.46 | [25.90, 40.63] | 2344 | 37.2% | 99 | ≥20% frames; meets KILL cell |
| pts:pts1 | MBPTrack (GT-convention yaw) | 17.59 | 78.87 | 61.28 | [50.41, 68.48] | 1691 | 26.8% | 107 | ≥20% frames; meets KILL cell |
| pts:pts2 | MBPTrack (GT-convention yaw) | 21.80 | 82.52 | 60.72 | [50.32, 69.76] | 2269 | 36.0% | 91 | ≥20% frames; meets KILL cell |
| mot:motLo | MBPTrack (GT-convention yaw) | 24.64 | 74.18 | 49.54 | [41.90, 56.12] | 4751 | 75.4% | 115 | ≥40% frames; meets KILL cell |
| mot:motHi | MBPTrack (GT-convention yaw) | 15.77 | 70.17 | 54.40 | [27.82, 69.19] | 1553 | 24.6% | 17 | under-powered (<30 tracklets); ≥20% frames; not eligible |

### Car — per-family gaps (M2-Track − floor and MBPTrack − floor)

| Family | Bin | Floor | Learned | Gap | 95% CI | n frames | Share of binned | n tracklets | Flags |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| M2-Track | pts:pts0 | 26.60 | 54.59 | 27.99 | [21.87, 34.00] | 2344 | 37.2% | 99 | ≥20% frames; meets KILL cell |
| M2-Track | pts:pts1 | 17.59 | 72.49 | 54.90 | [44.00, 61.95] | 1691 | 26.8% | 107 | ≥20% frames; meets KILL cell |
| M2-Track | pts:pts2 | 21.80 | 75.26 | 53.46 | [42.06, 63.95] | 2269 | 36.0% | 91 | ≥20% frames; meets KILL cell |
| M2-Track | mot:motLo | 24.64 | 68.10 | 43.45 | [35.17, 50.88] | 4751 | 75.4% | 115 | ≥40% frames; meets KILL cell |
| M2-Track | mot:motHi | 15.77 | 62.96 | 47.19 | [23.88, 62.76] | 1553 | 24.6% | 17 | under-powered (<30 tracklets); ≥20% frames; not eligible |
| MBPTrack (GT-convention yaw) | pts:pts0 | 26.60 | 60.07 | 33.46 | [25.90, 40.63] | 2344 | 37.2% | 99 | ≥20% frames; meets KILL cell |
| MBPTrack (GT-convention yaw) | pts:pts1 | 17.59 | 78.87 | 61.28 | [50.41, 68.48] | 1691 | 26.8% | 107 | ≥20% frames; meets KILL cell |
| MBPTrack (GT-convention yaw) | pts:pts2 | 21.80 | 82.52 | 60.72 | [50.32, 69.76] | 2269 | 36.0% | 91 | ≥20% frames; meets KILL cell |
| MBPTrack (GT-convention yaw) | mot:motLo | 24.64 | 74.18 | 49.54 | [41.90, 56.12] | 4751 | 75.4% | 115 | ≥40% frames; meets KILL cell |
| MBPTrack (GT-convention yaw) | mot:motHi | 15.77 | 70.17 | 54.40 | [27.82, 69.19] | 1553 | 24.6% | 17 | under-powered (<30 tracklets); ≥20% frames; not eligible |

### Pedestrian — best learned (reported for completeness; headline is Car)

| Bin | Best family | Floor | Learned | Gap | 95% CI | n frames | Share of binned | n tracklets | Flags |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| pts:pts0 | MBPTrack (GT-convention yaw) | 34.29 | 59.82 | 25.53 | [18.32, 32.41] | 645 | 10.7% | 39 | not eligible |
| pts:pts1 | MBPTrack (GT-convention yaw) | 28.28 | 65.70 | 37.42 | [31.97, 42.96] | 2707 | 44.9% | 59 | ≥40% frames; meets KILL cell |
| pts:pts2 | MBPTrack (GT-convention yaw) | 20.48 | 67.03 | 46.55 | [40.18, 52.60] | 2674 | 44.4% | 55 | ≥40% frames; meets KILL cell |
| mot:motLo | MBPTrack (GT-convention yaw) | 25.46 | 65.65 | 40.19 | [35.41, 44.96] | 6020 | 99.9% | 62 | ≥40% frames; meets KILL cell |
| mot:motHi | MBPTrack (GT-convention yaw) | 24.17 | 73.33 | 49.17 | [29.08, 67.50] | 6 | 0.1% | 6 | under-powered (<30 tracklets); not eligible |

### Pedestrian — per-family gaps (M2-Track − floor and MBPTrack − floor)

| Family | Bin | Floor | Learned | Gap | 95% CI | n frames | Share of binned | n tracklets | Flags |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| M2-Track | pts:pts0 | 34.29 | 55.09 | 20.80 | [7.58, 33.84] | 645 | 10.7% | 39 | not eligible |
| M2-Track | pts:pts1 | 28.28 | 61.23 | 32.96 | [24.68, 40.40] | 2707 | 44.9% | 59 | ≥40% frames; meets KILL cell |
| M2-Track | pts:pts2 | 20.48 | 60.42 | 39.95 | [32.58, 47.08] | 2674 | 44.4% | 55 | ≥40% frames; meets KILL cell |
| M2-Track | mot:motLo | 25.46 | 60.22 | 34.76 | [27.45, 41.51] | 6020 | 99.9% | 62 | ≥40% frames; meets KILL cell |
| M2-Track | mot:motHi | 24.17 | 58.33 | 34.17 | [7.50, 60.00] | 6 | 0.1% | 6 | under-powered (<30 tracklets); not eligible |
| MBPTrack (GT-convention yaw) | pts:pts0 | 34.29 | 59.82 | 25.53 | [18.32, 32.41] | 645 | 10.7% | 39 | not eligible |
| MBPTrack (GT-convention yaw) | pts:pts1 | 28.28 | 65.70 | 37.42 | [31.97, 42.96] | 2707 | 44.9% | 59 | ≥40% frames; meets KILL cell |
| MBPTrack (GT-convention yaw) | pts:pts2 | 20.48 | 67.03 | 46.55 | [40.18, 52.60] | 2674 | 44.4% | 55 | ≥40% frames; meets KILL cell |
| MBPTrack (GT-convention yaw) | mot:motLo | 25.46 | 65.65 | 40.19 | [35.41, 44.96] | 6020 | 99.9% | 62 | ≥40% frames; meets KILL cell |
| MBPTrack (GT-convention yaw) | mot:motHi | 24.17 | 73.33 | 49.17 | [29.08, 67.50] | 6 | 0.1% | 6 | under-powered (<30 tracklets); not eligible |

### Van — best learned (Other; all bins under-powered; reported for completeness)

| Bin | Best family | Floor | Learned | Gap | 95% CI | n frames | Share of binned | n tracklets | Flags |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| pts:pts0 | MBPTrack (GT-convention yaw) | 30.05 | 44.68 | 14.62 | [-8.66, 37.71] | 501 | 40.7% | 13 | under-powered (<30 tracklets); ≥40% frames; not eligible |
| pts:pts1 | MBPTrack (GT-convention yaw) | 22.53 | 67.60 | 45.08 | [20.63, 61.17] | 392 | 31.8% | 15 | under-powered (<30 tracklets); ≥20% frames; not eligible |
| pts:pts2 | MBPTrack (GT-convention yaw) | 33.31 | 74.61 | 41.30 | [22.72, 65.75] | 339 | 27.5% | 11 | under-powered (<30 tracklets); ≥20% frames; not eligible |
| mot:motLo | MBPTrack (GT-convention yaw) | 28.81 | 60.85 | 32.03 | [15.47, 49.32] | 1217 | 98.8% | 14 | under-powered (<30 tracklets); ≥40% frames; not eligible |
| mot:motHi | MBPTrack (GT-convention yaw) | 7.50 | 8.17 | 0.67 | [0.00, 10.00] | 15 | 1.2% | 2 | under-powered (<30 tracklets); not eligible |

### Van — per-family gaps (M2-Track − floor and MBPTrack − floor)

| Family | Bin | Floor | Learned | Gap | 95% CI | n frames | Share of binned | n tracklets | Flags |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| MBPTrack (GT-convention yaw) | pts:pts0 | 30.05 | 44.68 | 14.62 | [-8.66, 37.71] | 501 | 40.7% | 13 | under-powered (<30 tracklets); ≥40% frames; not eligible |
| MBPTrack (GT-convention yaw) | pts:pts1 | 22.53 | 67.60 | 45.08 | [20.63, 61.17] | 392 | 31.8% | 15 | under-powered (<30 tracklets); ≥20% frames; not eligible |
| MBPTrack (GT-convention yaw) | pts:pts2 | 33.31 | 74.61 | 41.30 | [22.72, 65.75] | 339 | 27.5% | 11 | under-powered (<30 tracklets); ≥20% frames; not eligible |
| MBPTrack (GT-convention yaw) | mot:motLo | 28.81 | 60.85 | 32.03 | [15.47, 49.32] | 1217 | 98.8% | 14 | under-powered (<30 tracklets); ≥40% frames; not eligible |
| MBPTrack (GT-convention yaw) | mot:motHi | 7.50 | 8.17 | 0.67 | [0.00, 10.00] | 15 | 1.2% | 2 | under-powered (<30 tracklets); not eligible |

### Cyclist — best learned (Other; all bins under-powered; reported for completeness)

| Bin | Best family | Floor | Learned | Gap | 95% CI | n frames | Share of binned | n tracklets | Flags |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| pts:pts0 | MBPTrack (GT-convention yaw) | 69.61 | 64.34 | -5.26 | [-26.88, 11.25] | 19 | 6.3% | 5 | under-powered (<30 tracklets); not eligible |
| pts:pts1 | MBPTrack (GT-convention yaw) | 64.31 | 73.92 | 9.61 | [-3.60, 27.15] | 127 | 42.3% | 7 | under-powered (<30 tracklets); ≥40% frames; not eligible |
| pts:pts2 | MBPTrack (GT-convention yaw) | 47.73 | 79.42 | 31.69 | [12.11, 53.09] | 154 | 51.3% | 8 | under-powered (<30 tracklets); ≥40% frames; not eligible |
| mot:motLo | MBPTrack (GT-convention yaw) | 56.13 | 76.13 | 20.00 | [5.95, 36.39] | 300 | 100.0% | 8 | under-powered (<30 tracklets); ≥40% frames; not eligible |

### Cyclist — per-family gaps (M2-Track − floor and MBPTrack − floor)

| Family | Bin | Floor | Learned | Gap | 95% CI | n frames | Share of binned | n tracklets | Flags |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| MBPTrack (GT-convention yaw) | pts:pts0 | 69.61 | 64.34 | -5.26 | [-26.88, 11.25] | 19 | 6.3% | 5 | under-powered (<30 tracklets); not eligible |
| MBPTrack (GT-convention yaw) | pts:pts1 | 64.31 | 73.92 | 9.61 | [-3.60, 27.15] | 127 | 42.3% | 7 | under-powered (<30 tracklets); ≥40% frames; not eligible |
| MBPTrack (GT-convention yaw) | pts:pts2 | 47.73 | 79.42 | 31.69 | [12.11, 53.09] | 154 | 51.3% | 8 | under-powered (<30 tracklets); ≥40% frames; not eligible |
| MBPTrack (GT-convention yaw) | mot:motLo | 56.13 | 76.13 | 20.00 | [5.95, 36.39] | 300 | 100.0% | 8 | under-powered (<30 tracklets); ≥40% frames; not eligible |

## Secondary: point × motion grid gaps (not used for GO/KILL)

Grid cell labels are GT point bin × motion (p0 = <50, p1 = 50–199, p2 = ≥200; mLo / mHi). Frame 0 excluded. These cells are secondary and cannot drive GO/KILL.

### Car grid — best learned

| Cell | Best family | Floor | Learned | Gap | 95% CI | n frames | Share of binned | n tracklets | Flags |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| grid:p0|mLo | MBPTrack (GT-convention yaw) | 31.25 | 61.17 | 29.92 | [22.44, 36.71] | 1524 | 24.2% | 91 | secondary; not a decision bin; ≥20% frames |
| grid:p0|mHi | MBPTrack (GT-convention yaw) | 17.98 | 58.01 | 40.04 | [23.40, 55.98] | 820 | 13.0% | 13 | secondary; not a decision bin; under-powered (<30 tracklets) |
| grid:p1|mLo | MBPTrack (GT-convention yaw) | 21.40 | 77.79 | 56.39 | [47.11, 63.48] | 1252 | 19.9% | 105 | secondary; not a decision bin |
| grid:p1|mHi | MBPTrack (GT-convention yaw) | 6.74 | 81.96 | 75.23 | [55.29, 79.09] | 439 | 7.0% | 8 | secondary; not a decision bin; under-powered (<30 tracklets) |
| grid:p2|mLo | MBPTrack (GT-convention yaw) | 21.60 | 81.93 | 60.33 | [50.00, 69.71] | 1975 | 31.3% | 91 | secondary; not a decision bin; ≥20% frames |
| grid:p2|mHi | MBPTrack (GT-convention yaw) | 23.11 | 86.46 | 63.35 | [29.18, 78.16] | 294 | 4.7% | 5 | secondary; not a decision bin; under-powered (<30 tracklets) |

### Car grid — per family

| Family | Cell | Floor | Learned | Gap | 95% CI | n frames | Share of binned | n tracklets | Flags |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| M2-Track | grid:p0|mLo | 31.25 | 56.67 | 25.42 | [17.94, 32.45] | 1524 | 24.2% | 91 | secondary; not a decision bin; ≥20% frames |
| M2-Track | grid:p0|mHi | 17.98 | 50.73 | 32.75 | [22.10, 47.27] | 820 | 13.0% | 13 | secondary; not a decision bin; under-powered (<30 tracklets) |
| M2-Track | grid:p1|mLo | 21.40 | 73.32 | 51.92 | [42.80, 59.00] | 1252 | 19.9% | 105 | secondary; not a decision bin |
| M2-Track | grid:p1|mHi | 6.74 | 70.13 | 63.39 | [19.58, 70.45] | 439 | 7.0% | 8 | secondary; not a decision bin; under-powered (<30 tracklets) |
| M2-Track | grid:p2|mLo | 21.60 | 73.60 | 52.00 | [40.20, 63.09] | 1975 | 31.3% | 91 | secondary; not a decision bin; ≥20% frames |
| M2-Track | grid:p2|mHi | 23.11 | 86.38 | 63.27 | [32.24, 77.21] | 294 | 4.7% | 5 | secondary; not a decision bin; under-powered (<30 tracklets) |
| MBPTrack (GT-convention yaw) | grid:p0|mLo | 31.25 | 61.17 | 29.92 | [22.44, 36.71] | 1524 | 24.2% | 91 | secondary; not a decision bin; ≥20% frames |
| MBPTrack (GT-convention yaw) | grid:p0|mHi | 17.98 | 58.01 | 40.04 | [23.40, 55.98] | 820 | 13.0% | 13 | secondary; not a decision bin; under-powered (<30 tracklets) |
| MBPTrack (GT-convention yaw) | grid:p1|mLo | 21.40 | 77.79 | 56.39 | [47.11, 63.48] | 1252 | 19.9% | 105 | secondary; not a decision bin |
| MBPTrack (GT-convention yaw) | grid:p1|mHi | 6.74 | 81.96 | 75.23 | [55.29, 79.09] | 439 | 7.0% | 8 | secondary; not a decision bin; under-powered (<30 tracklets) |
| MBPTrack (GT-convention yaw) | grid:p2|mLo | 21.60 | 81.93 | 60.33 | [50.00, 69.71] | 1975 | 31.3% | 91 | secondary; not a decision bin; ≥20% frames |
| MBPTrack (GT-convention yaw) | grid:p2|mHi | 23.11 | 86.46 | 63.35 | [29.18, 78.16] | 294 | 4.7% | 5 | secondary; not a decision bin; under-powered (<30 tracklets) |

### Pedestrian grid — best learned

| Cell | Best family | Floor | Learned | Gap | 95% CI | n frames | Share of binned | n tracklets | Flags |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| grid:p0|mLo | MBPTrack (GT-convention yaw) | 34.36 | 59.81 | 25.45 | [18.27, 32.33] | 643 | 10.7% | 39 | secondary; not a decision bin |
| grid:p0|mHi | M2-Track | 12.50 | 62.50 | 50.00 | [40.00, 60.00] | 2 | 0.0% | 2 | secondary; not a decision bin; under-powered (<30 tracklets) |
| grid:p1|mLo | MBPTrack (GT-convention yaw) | 28.28 | 65.70 | 37.42 | [31.97, 42.96] | 2707 | 44.9% | 59 | secondary; not a decision bin; ≥40% frames |
| grid:p2|mLo | MBPTrack (GT-convention yaw) | 20.46 | 67.01 | 46.55 | [40.18, 52.59] | 2670 | 44.3% | 55 | secondary; not a decision bin; ≥40% frames |
| grid:p2|mHi | MBPTrack (GT-convention yaw) | 30.00 | 78.75 | 48.75 | [10.00, 80.00] | 4 | 0.1% | 4 | secondary; not a decision bin; under-powered (<30 tracklets) |

### Pedestrian grid — per family

| Family | Cell | Floor | Learned | Gap | 95% CI | n frames | Share of binned | n tracklets | Flags |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| M2-Track | grid:p0|mLo | 34.36 | 55.07 | 20.71 | [7.54, 33.77] | 643 | 10.7% | 39 | secondary; not a decision bin |
| M2-Track | grid:p0|mHi | 12.50 | 62.50 | 50.00 | [40.00, 60.00] | 2 | 0.0% | 2 | secondary; not a decision bin; under-powered (<30 tracklets) |
| M2-Track | grid:p1|mLo | 28.28 | 61.23 | 32.96 | [24.68, 40.40] | 2707 | 44.9% | 59 | secondary; not a decision bin; ≥40% frames |
| M2-Track | grid:p2|mLo | 20.46 | 60.43 | 39.97 | [32.62, 47.10] | 2670 | 44.3% | 55 | secondary; not a decision bin; ≥40% frames |
| M2-Track | grid:p2|mHi | 30.00 | 56.25 | 26.25 | [-15.00, 75.00] | 4 | 0.1% | 4 | secondary; not a decision bin; under-powered (<30 tracklets) |
| MBPTrack (GT-convention yaw) | grid:p0|mLo | 34.36 | 59.81 | 25.45 | [18.27, 32.33] | 643 | 10.7% | 39 | secondary; not a decision bin |
| MBPTrack (GT-convention yaw) | grid:p0|mHi | 12.50 | 62.50 | 50.00 | [40.00, 60.00] | 2 | 0.0% | 2 | secondary; not a decision bin; under-powered (<30 tracklets) |
| MBPTrack (GT-convention yaw) | grid:p1|mLo | 28.28 | 65.70 | 37.42 | [31.97, 42.96] | 2707 | 44.9% | 59 | secondary; not a decision bin; ≥40% frames |
| MBPTrack (GT-convention yaw) | grid:p2|mLo | 20.46 | 67.01 | 46.55 | [40.18, 52.59] | 2670 | 44.3% | 55 | secondary; not a decision bin; ≥40% frames |
| MBPTrack (GT-convention yaw) | grid:p2|mHi | 30.00 | 78.75 | 48.75 | [10.00, 80.00] | 4 | 0.1% | 4 | secondary; not a decision bin; under-powered (<30 tracklets) |

### Van grid — best learned

| Cell | Best family | Floor | Learned | Gap | 95% CI | n frames | Share of binned | n tracklets | Flags |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| grid:p0|mLo | MBPTrack (GT-convention yaw) | 30.69 | 45.71 | 15.02 | [-9.16, 39.22] | 487 | 39.5% | 12 | secondary; not a decision bin; under-powered (<30 tracklets); ≥20% frames |
| grid:p0|mHi | MBPTrack (GT-convention yaw) | 7.86 | 8.57 | 0.71 | [0.00, 10.00] | 14 | 1.1% | 2 | secondary; not a decision bin; under-powered (<30 tracklets) |
| grid:p1|mLo | MBPTrack (GT-convention yaw) | 22.58 | 67.77 | 45.19 | [20.71, 61.30] | 391 | 31.7% | 14 | secondary; not a decision bin; under-powered (<30 tracklets); ≥20% frames |
| grid:p1|mHi | MBPTrack (GT-convention yaw) | 2.50 | 2.50 | 0.00 | [0.00, 0.00] | 1 | 0.1% | 1 | secondary; not a decision bin; under-powered (<30 tracklets) |
| grid:p2|mLo | MBPTrack (GT-convention yaw) | 33.31 | 74.61 | 41.30 | [22.72, 65.75] | 339 | 27.5% | 11 | secondary; not a decision bin; under-powered (<30 tracklets); ≥20% frames |

### Van grid — per family

| Family | Cell | Floor | Learned | Gap | 95% CI | n frames | Share of binned | n tracklets | Flags |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| MBPTrack (GT-convention yaw) | grid:p0|mLo | 30.69 | 45.71 | 15.02 | [-9.16, 39.22] | 487 | 39.5% | 12 | secondary; not a decision bin; under-powered (<30 tracklets); ≥20% frames |
| MBPTrack (GT-convention yaw) | grid:p0|mHi | 7.86 | 8.57 | 0.71 | [0.00, 10.00] | 14 | 1.1% | 2 | secondary; not a decision bin; under-powered (<30 tracklets) |
| MBPTrack (GT-convention yaw) | grid:p1|mLo | 22.58 | 67.77 | 45.19 | [20.71, 61.30] | 391 | 31.7% | 14 | secondary; not a decision bin; under-powered (<30 tracklets); ≥20% frames |
| MBPTrack (GT-convention yaw) | grid:p1|mHi | 2.50 | 2.50 | 0.00 | [0.00, 0.00] | 1 | 0.1% | 1 | secondary; not a decision bin; under-powered (<30 tracklets) |
| MBPTrack (GT-convention yaw) | grid:p2|mLo | 33.31 | 74.61 | 41.30 | [22.72, 65.75] | 339 | 27.5% | 11 | secondary; not a decision bin; under-powered (<30 tracklets); ≥20% frames |

### Cyclist grid — best learned

| Cell | Best family | Floor | Learned | Gap | 95% CI | n frames | Share of binned | n tracklets | Flags |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| grid:p0|mLo | MBPTrack (GT-convention yaw) | 69.61 | 64.34 | -5.26 | [-26.88, 11.25] | 19 | 6.3% | 5 | secondary; not a decision bin; under-powered (<30 tracklets) |
| grid:p1|mLo | MBPTrack (GT-convention yaw) | 64.31 | 73.92 | 9.61 | [-3.60, 27.15] | 127 | 42.3% | 7 | secondary; not a decision bin; under-powered (<30 tracklets); ≥40% frames |
| grid:p2|mLo | MBPTrack (GT-convention yaw) | 47.73 | 79.42 | 31.69 | [12.11, 53.09] | 154 | 51.3% | 8 | secondary; not a decision bin; under-powered (<30 tracklets); ≥40% frames |

### Cyclist grid — per family

| Family | Cell | Floor | Learned | Gap | 95% CI | n frames | Share of binned | n tracklets | Flags |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| MBPTrack (GT-convention yaw) | grid:p0|mLo | 69.61 | 64.34 | -5.26 | [-26.88, 11.25] | 19 | 6.3% | 5 | secondary; not a decision bin; under-powered (<30 tracklets) |
| MBPTrack (GT-convention yaw) | grid:p1|mLo | 64.31 | 73.92 | 9.61 | [-3.60, 27.15] | 127 | 42.3% | 7 | secondary; not a decision bin; under-powered (<30 tracklets); ≥40% frames |
| MBPTrack (GT-convention yaw) | grid:p2|mLo | 47.73 | 79.42 | 31.69 | [12.11, 53.09] | 154 | 51.3% | 8 | secondary; not a decision bin; under-powered (<30 tracklets); ≥40% frames |

## Secondary ratio R (floor → best learned, protocol a)

R = (share of gain G in primary-hard frames) / (share of frames that are primary-hard).
Undefined / not reported if total gain ≤ 2 Success. P5 is secondary and is not a GO/KILL claim.

| Class | Best learned (overall, binned) | R | 95% CI | n valid boots | P5 supported (R>1.2 and CI lo>1)? |
|---|---|---:|---|---:|---|
| Car | MBPTrack (GT-convention yaw) | 0.833 | [0.612, 0.987] | 10000 | False |
| Pedestrian | MBPTrack (GT-convention yaw) | 0.639 | [0.487, 0.771] | 10000 | False |
| Van | MBPTrack (GT-convention yaw) | 0.461 | [-0.466, 0.864] | 10000 | False |
| Cyclist | MBPTrack (GT-convention yaw) | -0.263 | [-2.692, 0.720] | 9972 | False |

## KITTI-side verdict (headline: Car, protocol a)

KITTI side of rule: KILL conditions hold on every eligible decision bin (each bin with ≥20% of binned frames and ≥30 tracklets has learned − floor Success > 10 and a 95% lower bound > 5). Formal KILL needs the same on nuScenes, which has not been run.

Eligible Car decision bins (≥20% of binned frames and ≥30 tracklets):

- `pts:pts0`: best=MBPTrack (GT-convention yaw), gap=33.46 [25.90, 40.63], share=37.2%, tracklets=99, KILL-cell=True, GO-cell=False
- `pts:pts1`: best=MBPTrack (GT-convention yaw), gap=61.28 [50.41, 68.48], share=26.8%, tracklets=107, KILL-cell=True, GO-cell=False
- `pts:pts2`: best=MBPTrack (GT-convention yaw), gap=60.72 [50.32, 69.76], share=36.0%, tracklets=91, KILL-cell=True, GO-cell=False
- `mot:motLo`: best=MBPTrack (GT-convention yaw), gap=49.54 [41.90, 56.12], share=75.4%, tracklets=115, KILL-cell=True, GO-cell=False

Formal status: KITTI-side KILL only; formal decision pending nuScenes

