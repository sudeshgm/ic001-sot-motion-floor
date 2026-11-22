# nuScenes decision tables

Generated 2026-11-22 10:22 IST. Aggregate scores only; no per-frame CSVs.
Scope: nuScenes v1.0-trainval **val** split, keyframes, LIDAR_TOP. Combined with the already-recorded KITTI-side result for the formal first-test rule.
Floor = pre-registered `cv_snap` in `results/nuscenes/` (unchanged). Learned families = M2-Track (Car only) and MBPTrack (Car, Pedestrian, Truck, Trailer, Bus). No yaw-convention correction was applied: frame-0 predicted boxes match the index GT (centres exact; yaw error ≤ 4.4e-16 rad).
Bootstrap: tracklet resampling, 10,000 draws, seed 0, percentile 95% CI. Frame 0 is included in overall Success/Precision and excluded from every per-bin score (PREREG choice g). No point-bin merge (GT census already recorded).

## V1 reproduction (protocol a, nuScenes; informational)

V1 still gates on KITTI Car only (already recorded as PASS for both families). nuScenes Car uses the same dated-addendum tolerance and is informational.

| Tracker | Class | Role | Our Success / Precision | Paper | Δ paper | Checkpoint | Δ ckpt | Informational |
|---|---|---|---:|---:|---:|---:|---:|---|
| M2-Track | Car | informational | 57.21 / 65.73 | 55.85 | 1.36 | 57.22 | 0.01 | PASS |
| MBPTrack | Car | informational | 62.46 / 70.41 | 62.47 | 0.01 | — | — | PASS |

Rule: a tracker passes if its ic001-rescored Success is within 1.0 of either the paper value or a documented official-checkpoint value (MBPTrack: paper value only).

## Overall Success / Precision (protocol a, includes frame 0)

| Class | Method | Success | Precision | n frames | vs run-dir ic001 ΔS / ΔP | vs native ΔS / ΔP |
|---|---|---:|---:|---:|---:|---:|
| Car | floor (cv_snap) | 39.59 | 42.16 | 64159 | — | — |
| Car | last_box | 57.39 | 63.57 | 64159 | — | — |
| Car | M2-Track | 57.21 | 65.73 | 64159 | +0.00e+00 / +0.00e+00 | +0.00 / -0.00 |
| Car | MBPTrack | 62.46 | 70.41 | 64159 | +0.00e+00 / +0.00e+00 | -0.00 / +0.00 |
| Pedestrian | floor (cv_snap) | 16.97 | 29.70 | 33227 | — | — |
| Pedestrian | last_box | 21.42 | 33.32 | 33227 | — | — |
| Pedestrian | MBPTrack | 45.38 | 74.06 | 33227 | +0.00e+00 / +0.00e+00 | +0.00 / +0.00 |
| Truck | floor (cv_snap) | 34.14 | 30.40 | 13587 | — | — |
| Truck | last_box | 62.67 | 63.20 | 13587 | — | — |
| Truck | MBPTrack | 62.16 | 63.24 | 13587 | +0.00e+00 / +0.00e+00 | -0.00 / -0.00 |
| Trailer | floor (cv_snap) | 39.16 | 31.76 | 3352 | — | — |
| Trailer | last_box | 73.88 | 71.17 | 3352 | — | — |
| Trailer | MBPTrack | 65.07 | 61.30 | 3352 | +0.00e+00 / +0.00e+00 | +0.00 / +0.00 |
| Bus | floor (cv_snap) | 26.98 | 20.48 | 2953 | — | — |
| Bus | last_box | 44.02 | 40.35 | 2953 | — | — |
| Bus | MBPTrack | 55.08 | 51.34 | 2953 | +0.00e+00 / +0.00e+00 | +0.00 / +0.00 |

Native figures are the tracker-native overall scores from the run dump logs. ic001 rescoring can differ slightly because of IoU implementation differences. A mismatch against the run-dir `eval_bins_nuscenes_*.json` (same ic001 metric) would be unexpected.

## Decision-bin gaps (protocol a) — best learned − floor

Decision bins are single-axis (PREREG choice f). Learned = best family by point-estimate Success in that bin, before the bootstrap (choice m). Cells with fewer than 30 tracklets cannot drive GO/KILL. Shares are of binned frames (frame 0 excluded).

### Car — best learned (headline)

| Bin | Best family | Floor | Learned | Gap | 95% CI | n frames | Share of binned | n tracklets | Flags |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| pts0 (<10) | MBPTrack | 42.80 | 52.43 | 9.64 | [7.97, 11.29] | 35909 | 59.4% | 3304 | ≥40% frames; eligible, neither GO nor KILL cell |
| pts1 (10–24) | MBPTrack | 24.09 | 67.08 | 42.99 | [40.96, 44.96] | 7961 | 13.2% | 1989 | not eligible |
| pts2 (≥25) | MBPTrack | 27.06 | 73.90 | 46.83 | [44.57, 49.09] | 16629 | 27.5% | 1601 | ≥20% frames; meets KILL cell |
| motLo (<2.5 m) | MBPTrack | 41.13 | 66.08 | 24.94 | [23.26, 26.58] | 51375 | 84.9% | 3087 | ≥40% frames; meets KILL cell |
| motHi (≥2.5 m) | MBPTrack | 7.17 | 27.52 | 20.35 | [17.93, 22.83] | 9124 | 15.1% | 759 | not eligible |

### Car — per-family gaps

| Family | Bin | Floor | Learned | Gap | 95% CI | n frames | Share of binned | n tracklets | Flags |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| M2-Track | pts0 (<10) | 42.80 | 44.28 | 1.49 | [-0.29, 3.24] | 35909 | 59.4% | 3304 | ≥40% frames; meets GO cell |
| M2-Track | pts1 (10–24) | 24.09 | 63.27 | 39.18 | [37.14, 41.18] | 7961 | 13.2% | 1989 | not eligible |
| M2-Track | pts2 (≥25) | 27.06 | 73.09 | 46.03 | [43.85, 48.23] | 16629 | 27.5% | 1601 | ≥20% frames; meets KILL cell |
| M2-Track | motLo (<2.5 m) | 41.13 | 59.54 | 18.41 | [16.59, 20.18] | 51375 | 84.9% | 3087 | ≥40% frames; meets KILL cell |
| M2-Track | motHi (≥2.5 m) | 7.17 | 27.42 | 20.25 | [17.66, 22.89] | 9124 | 15.1% | 759 | not eligible |
| MBPTrack | pts0 (<10) | 42.80 | 52.43 | 9.64 | [7.97, 11.29] | 35909 | 59.4% | 3304 | ≥40% frames; eligible, neither GO nor KILL cell |
| MBPTrack | pts1 (10–24) | 24.09 | 67.08 | 42.99 | [40.96, 44.96] | 7961 | 13.2% | 1989 | not eligible |
| MBPTrack | pts2 (≥25) | 27.06 | 73.90 | 46.83 | [44.57, 49.09] | 16629 | 27.5% | 1601 | ≥20% frames; meets KILL cell |
| MBPTrack | motLo (<2.5 m) | 41.13 | 66.08 | 24.94 | [23.26, 26.58] | 51375 | 84.9% | 3087 | ≥40% frames; meets KILL cell |
| MBPTrack | motHi (≥2.5 m) | 7.17 | 27.52 | 20.35 | [17.93, 22.83] | 9124 | 15.1% | 759 | not eligible |

Per-family note, not used by the rule: M2-Track on the same pts0 bin has gap 1.49 with 95% CI [−0.29, 3.24], which would meet the GO cell condition. The frozen rule uses the best family by point-estimate Success in the bin (here MBPTrack, 52.43 vs M2-Track 44.28), so that M2-Track cell does not drive GO or KILL.

### Pedestrian — best learned (reported; headline is Car)

| Bin | Best family | Floor | Learned | Gap | 95% CI | n frames | Share of binned | n tracklets | Flags |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| pts0 (<10) | MBPTrack | 11.40 | 37.85 | 26.45 | [25.21, 27.70] | 24271 | 77.4% | 1772 | ≥40% frames; meets KILL cell |
| pts1 (10–24) | MBPTrack | 14.04 | 55.42 | 41.38 | [39.04, 43.69] | 4054 | 12.9% | 953 | not eligible |
| pts2 (≥25) | MBPTrack | 15.37 | 59.49 | 44.12 | [41.21, 47.05] | 3044 | 9.7% | 560 | not eligible |
| motLo (<2.5 m) | MBPTrack | 12.13 | 42.23 | 30.10 | [28.89, 31.33] | 31359 | 100.0% | 1798 | ≥40% frames; meets KILL cell |
| motHi (≥2.5 m) | MBPTrack | 2.50 | 2.50 | 0.00 | [0.00, 0.00] | 10 | 0.0% | 10 | under-powered (<30 tracklets); not eligible |

### Pedestrian — per-family gaps

| Family | Bin | Floor | Learned | Gap | 95% CI | n frames | Share of binned | n tracklets | Flags |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| MBPTrack | pts0 (<10) | 11.40 | 37.85 | 26.45 | [25.21, 27.70] | 24271 | 77.4% | 1772 | ≥40% frames; meets KILL cell |
| MBPTrack | pts1 (10–24) | 14.04 | 55.42 | 41.38 | [39.04, 43.69] | 4054 | 12.9% | 953 | not eligible |
| MBPTrack | pts2 (≥25) | 15.37 | 59.49 | 44.12 | [41.21, 47.05] | 3044 | 9.7% | 560 | not eligible |
| MBPTrack | motLo (<2.5 m) | 12.13 | 42.23 | 30.10 | [28.89, 31.33] | 31359 | 100.0% | 1798 | ≥40% frames; meets KILL cell |
| MBPTrack | motHi (≥2.5 m) | 2.50 | 2.50 | 0.00 | [0.00, 0.00] | 10 | 0.0% | 10 | under-powered (<30 tracklets); not eligible |

### Truck — best learned (reported; headline is Car)

| Bin | Best family | Floor | Learned | Gap | 95% CI | n frames | Share of binned | n tracklets | Flags |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| pts0 (<10) | MBPTrack | 34.90 | 48.37 | 13.46 | [9.25, 17.55] | 5944 | 45.8% | 540 | ≥40% frames; meets KILL cell |
| pts1 (10–24) | MBPTrack | 23.24 | 64.50 | 41.26 | [38.00, 44.46] | 2098 | 16.2% | 412 | not eligible |
| pts2 (≥25) | MBPTrack | 29.90 | 73.26 | 43.36 | [39.19, 47.56] | 4937 | 38.0% | 353 | ≥20% frames; meets KILL cell |
| motLo (<2.5 m) | MBPTrack | 34.21 | 64.33 | 30.12 | [26.73, 33.39] | 11388 | 87.7% | 547 | ≥40% frames; meets KILL cell |
| motHi (≥2.5 m) | MBPTrack | 8.97 | 32.65 | 23.68 | [17.38, 30.08] | 1591 | 12.3% | 120 | not eligible |

### Truck — per-family gaps

| Family | Bin | Floor | Learned | Gap | 95% CI | n frames | Share of binned | n tracklets | Flags |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| MBPTrack | pts0 (<10) | 34.90 | 48.37 | 13.46 | [9.25, 17.55] | 5944 | 45.8% | 540 | ≥40% frames; meets KILL cell |
| MBPTrack | pts1 (10–24) | 23.24 | 64.50 | 41.26 | [38.00, 44.46] | 2098 | 16.2% | 412 | not eligible |
| MBPTrack | pts2 (≥25) | 29.90 | 73.26 | 43.36 | [39.19, 47.56] | 4937 | 38.0% | 353 | ≥20% frames; meets KILL cell |
| MBPTrack | motLo (<2.5 m) | 34.21 | 64.33 | 30.12 | [26.73, 33.39] | 11388 | 87.7% | 547 | ≥40% frames; meets KILL cell |
| MBPTrack | motHi (≥2.5 m) | 8.97 | 32.65 | 23.68 | [17.38, 30.08] | 1591 | 12.3% | 120 | not eligible |

### Trailer — best learned (reported; headline is Car)

| Bin | Best family | Floor | Learned | Gap | 95% CI | n frames | Share of binned | n tracklets | Flags |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| pts0 (<10) | MBPTrack | 43.95 | 58.57 | 14.62 | [7.94, 21.45] | 1101 | 34.4% | 129 | ≥20% frames; meets KILL cell |
| pts1 (10–24) | MBPTrack | 32.48 | 58.96 | 26.47 | [18.82, 34.16] | 625 | 19.5% | 114 | not eligible |
| pts2 (≥25) | MBPTrack | 32.30 | 69.07 | 36.77 | [29.04, 44.47] | 1474 | 46.1% | 100 | ≥40% frames; meets KILL cell |
| motLo (<2.5 m) | MBPTrack | 38.14 | 66.85 | 28.71 | [22.93, 34.47] | 2993 | 93.5% | 143 | ≥40% frames; meets KILL cell |
| motHi (≥2.5 m) | MBPTrack | 10.37 | 14.82 | 4.44 | [-1.53, 14.96] | 207 | 6.5% | 21 | under-powered (<30 tracklets); not eligible |

### Trailer — per-family gaps

| Family | Bin | Floor | Learned | Gap | 95% CI | n frames | Share of binned | n tracklets | Flags |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| MBPTrack | pts0 (<10) | 43.95 | 58.57 | 14.62 | [7.94, 21.45] | 1101 | 34.4% | 129 | ≥20% frames; meets KILL cell |
| MBPTrack | pts1 (10–24) | 32.48 | 58.96 | 26.47 | [18.82, 34.16] | 625 | 19.5% | 114 | not eligible |
| MBPTrack | pts2 (≥25) | 32.30 | 69.07 | 36.77 | [29.04, 44.47] | 1474 | 46.1% | 100 | ≥40% frames; meets KILL cell |
| MBPTrack | motLo (<2.5 m) | 38.14 | 66.85 | 28.71 | [22.93, 34.47] | 2993 | 93.5% | 143 | ≥40% frames; meets KILL cell |
| MBPTrack | motHi (≥2.5 m) | 10.37 | 14.82 | 4.44 | [-1.53, 14.96] | 207 | 6.5% | 21 | under-powered (<30 tracklets); not eligible |

### Bus — best learned (reported; headline is Car)

| Bin | Best family | Floor | Learned | Gap | 95% CI | n frames | Share of binned | n tracklets | Flags |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| pts0 (<10) | MBPTrack | 25.69 | 37.60 | 11.91 | [4.65, 18.79] | 769 | 27.1% | 94 | ≥20% frames; eligible, neither GO nor KILL cell |
| pts1 (10–24) | MBPTrack | 18.53 | 45.95 | 27.42 | [18.68, 36.42] | 502 | 17.7% | 86 | not eligible |
| pts2 (≥25) | MBPTrack | 24.81 | 63.27 | 38.46 | [30.96, 46.01] | 1562 | 55.1% | 92 | ≥40% frames; meets KILL cell |
| motLo (<2.5 m) | MBPTrack | 28.37 | 59.46 | 31.10 | [24.09, 37.78] | 2100 | 74.1% | 108 | ≥40% frames; meets KILL cell |
| motHi (≥2.5 m) | MBPTrack | 11.24 | 35.36 | 24.13 | [16.32, 32.18] | 733 | 25.9% | 51 | ≥20% frames; meets KILL cell |

### Bus — per-family gaps

| Family | Bin | Floor | Learned | Gap | 95% CI | n frames | Share of binned | n tracklets | Flags |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| MBPTrack | pts0 (<10) | 25.69 | 37.60 | 11.91 | [4.65, 18.79] | 769 | 27.1% | 94 | ≥20% frames; eligible, neither GO nor KILL cell |
| MBPTrack | pts1 (10–24) | 18.53 | 45.95 | 27.42 | [18.68, 36.42] | 502 | 17.7% | 86 | not eligible |
| MBPTrack | pts2 (≥25) | 24.81 | 63.27 | 38.46 | [30.96, 46.01] | 1562 | 55.1% | 92 | ≥40% frames; meets KILL cell |
| MBPTrack | motLo (<2.5 m) | 28.37 | 59.46 | 31.10 | [24.09, 37.78] | 2100 | 74.1% | 108 | ≥40% frames; meets KILL cell |
| MBPTrack | motHi (≥2.5 m) | 11.24 | 35.36 | 24.13 | [16.32, 32.18] | 733 | 25.9% | 51 | ≥20% frames; meets KILL cell |

## Secondary ratio R (protocol a)

R = (share of gain from the floor to the best learned tracker in primary-hard frames) / (share of frames that are primary-hard). SECONDARY (PREREG P5). R is not reported if the total gain is ≤ 2 Success. SECONDARY analysis #2 (R_progress, BAT → best learned) is not computed: BAT was not run on nuScenes.

| Class | Best learned | R | 95% CI | n valid | P5 supported? |
|---|---|---:|---|---:|---|
| Car | MBPTrack | 0.490 | [0.445, 0.532] | 10000 | no |
| Pedestrian | MBPTrack | 0.879 | [0.861, 0.895] | 10000 | no |
| Truck | MBPTrack | 0.550 | [0.450, 0.640] | 10000 | no |
| Trailer | MBPTrack | 0.498 | [0.307, 0.676] | 10000 | no |
| Bus | MBPTrack | 0.639 | [0.464, 0.802] | 10000 | no |

## Predicted effects (Car, protocol a; not the decision rule)

- P3 (<25-point frames: learned − floor ≥ 15): 43870 frames (72.5% of binned, 3385 tracklets); floor 39.40, MBPTrack 55.09, gap **15.69**. P3 holds as a point estimate.
- P4 (frames where floor ≈ learned, per-frame gap ≤ 5, should be ≤ 30%): 27598 / 60499 binned frames (**45.6%**), best family MBPTrack. P4 does not hold.

## Primary easy / hard point estimates (Car, protocol a; not decision bins)

| Slice | n frames | Share of binned | n tracklets | Floor | Best family | Learned | Gap |
|---|---:|---:|---:|---:|---|---:|---:|
| easy_primary | 20304 | 33.6% | 1856 | 29.49 | MBPTrack | 78.22 | 48.74 |
| hard_primary | 40195 | 66.4% | 3365 | 39.31 | MBPTrack | 51.19 | 11.88 |

## Formal first-test decision (PREREG §8, Car, protocol a)

KITTI side of rule: KILL conditions hold on every eligible decision bin (each bin with ≥20% of binned frames and ≥30 tracklets has learned − floor Success > 10 and a 95% lower bound > 5). nuScenes side of rule: KILL conditions do not hold on every eligible decision bin. The pts0 (<10 points) bin is eligible (59.4% of binned frames, 3,304 tracklets) and has best-learned − floor Success 9.64 [7.97, 11.29], which is neither a KILL cell (gap not > 10) nor a GO cell. The other eligible bins (pts2, motLo) meet the KILL cell condition. No eligible bin meets the GO cell condition. The first-test rule returns INCONCLUSIVE. On KITTI Car, every eligible decision bin meets the KILL cell condition. On nuScenes Car, two eligible bins (pts2 / ≥25 points, and motLo / <2.5 m) also meet that condition, but the remaining eligible bin does not: pts0 (<10 points) holds 59.4% of binned frames (35,909 frames, 3,304 tracklets) and has best-learned (MBPTrack) − floor Success of 9.64 with 95% CI [7.97, 11.29]. That gap is not greater than 10, so the bin is not a KILL cell; it is also not a GO cell (gap is not ≤ 5, and the upper bound is not ≤ 10). The GO clause therefore does not fire (KITTI has no GO cell, including no ≥40% GO bin). Per the frozen pre-registration, TrackAny3D is to be added and the same rule re-applied once.

**Overall verdict: INCONCLUSIVE.**

KILL requires the cell conditions on every eligible bin of **both** datasets. GO requires a qualifying cell on each dataset, or one KITTI bin with ≥40% of frames. Anything else is INCONCLUSIVE.

### Verification (inputs)

- Run used: learned-tracker nuScenes outputs under the v3 run directory. `run_meta`: rc=0, wall_s=23082, paid=0, finished_at=2026-11-22T04:08:06Z (2026-11-22 09:38:06 IST).
- `SHA256SUMS_outputs.txt`: all OK (12 files).
- `SHA256SUMS_all.txt` (files present in the run directory): all OK.
- `SHA256SUMS_eval.txt`: all OK.
- `BUNDLE_SHA256SUMS.txt` is identical to `MANIFEST.txt` and lists the **input job bundle** (source tarballs and environment parts), not the learned-tracker dumps. Those input files are not stored in the output directory. The run-dir `logs/bundle_sha_check.txt` records every listed file as OK from the job itself. The two output-directory copies of the sum file match their `SHA256SUMS_all.txt` entries.
- Dump keys match the frozen nuScenes index exactly for every class and both protocols (missing=0, extra=0, no duplicate keys). Row counts: Car 128,318 (= 64,159 frames × 2 protocols) for both M2-Track and MBPTrack; Pedestrian 66,454; Truck 27,174; Trailer 6,704; Bus 5,906. Frame-0 predicted boxes match index GT (centres exact, yaw ≤ 4.4e-16 rad).
- A failed earlier run tree (v1) is present alongside v3. It has `run_meta` rc=3, no per-frame dumps, and an empty `summary.txt`. It was not used.

