# TrackAny3D final decision tables

Generated 2026-11-22 20:28 IST. Aggregate scores only. Car, protocol (a) OPE, floor = `cv_snap`, single-axis bins, frame 0 excluded from bins, tracklet bootstrap 10,000 draws seed 0, percentile 95% CI. Eligible = ≥20% of binned frames and ≥30 tracklets.

## V1 (dated addendum: within 1.0 Success of the paper value)

| Dataset | Role | ic001 Success / Precision | Official test Success / Precision (frames) | Paper | Δ paper (ic001) | Result |
|---|---|---:|---:|---:|---:|---|
| kitti Car | V1 gate | 73.40 / 85.21 | 73.417 / 85.239 (6424) | 73.40 | 0.00 | PASS |
| nuscenes Car | informational | 59.29 / 66.45 | 59.291 / 66.448 (64159) | 59.30 | 0.01 | PASS |

## TrackAny3D: tracker-internal vs ic001 rescore (overall, incl. frame 0)

KITTI uses the GT-convention yaw (see RUNLOG); the as-dumped yaw column is shown for comparison.

| Set | Tracker Success / Precision | ic001 Success / Precision | ΔS / ΔP | ic001 Success, as-dumped yaw (ΔS) |
|---|---:|---:|---:|---:|
| kitti_Car|ope | 73.42 / 85.24 | 73.40 / 85.21 | -0.024 / -0.035 | 73.33 (-0.09) |
| kitti_Car|reinit | 80.62 / 91.44 | 80.58 / 91.41 | -0.038 / -0.033 | 80.52 (-0.10) |
| kitti_Pedestrian|ope | 59.60 / 85.09 | 59.59 / 85.06 | -0.014 / -0.025 | 59.57 (-0.03) |
| kitti_Pedestrian|reinit | 75.69 / 94.58 | 75.69 / 94.56 | -0.002 / -0.025 | 75.68 (-0.01) |
| kitti_Van|ope | 69.62 / 82.51 | 69.62 / 82.48 | -0.003 / -0.026 | 69.61 (-0.01) |
| kitti_Van|reinit | 79.15 / 88.62 | 79.15 / 88.59 | +0.003 / -0.028 | 79.08 (-0.07) |
| kitti_Cyclist|ope | 74.28 / 93.59 | 74.26 / 93.53 | -0.019 / -0.059 | 74.04 (-0.24) |
| kitti_Cyclist|reinit | 80.56 / 95.03 | 80.53 / 94.98 | -0.032 / -0.054 | 80.45 (-0.11) |
| nuscenes_Car|ope | 59.29 / 66.45 | 59.29 / 66.45 | +0.001 / -0.003 | — |
| nuscenes_Car|reinit | 78.21 / 84.80 | 78.21 / 84.79 | +0.003 / -0.007 | — |

## Decision cells (Car, OPE): best of M2-Track, MBPTrack, TrackAny3D − floor

| Dataset | Bin | Best family | Floor | Best learned | Gap | 95% CI | Share of binned frames | Tracklets | Status |
|---|---|---|---:|---:|---:|---|---:|---:|---|
| KITTI | pts <50 | TrackAny3D | 26.60 | 60.08 | 33.47 | [25.97, 40.56] | 37.2% | 99 | KILL cell |
| KITTI | pts 50–199 | MBPTrack | 17.59 | 78.87 | 61.28 | [50.41, 68.48] | 26.8% | 107 | KILL cell |
| KITTI | pts ≥200 | TrackAny3D | 21.80 | 83.27 | 61.47 | [50.54, 71.02] | 36.0% | 91 | KILL cell |
| KITTI | motion <0.5 m | TrackAny3D | 24.64 | 74.34 | 49.69 | [41.86, 56.49] | 75.4% | 115 | KILL cell |
| KITTI | motion ≥0.5 m | MBPTrack | 15.77 | 70.17 | 54.40 | [27.82, 69.19] | 24.6% | 17 | not eligible (<30 tracklets) |
| nuScenes | pts <10 | MBPTrack | 42.80 | 52.43 | 9.64 | [7.97, 11.29] | 59.4% | 3304 | eligible; neither GO nor KILL |
| nuScenes | pts 10–24 | MBPTrack | 24.09 | 67.08 | 42.99 | [40.96, 44.96] | 13.2% | 1989 | not eligible (<20% of frames) |
| nuScenes | pts ≥25 | MBPTrack | 27.06 | 73.90 | 46.83 | [44.57, 49.09] | 27.5% | 1601 | KILL cell |
| nuScenes | motion <2.5 m | MBPTrack | 41.13 | 66.08 | 24.94 | [23.26, 26.58] | 84.9% | 3087 | KILL cell |
| nuScenes | motion ≥2.5 m | MBPTrack | 7.17 | 27.52 | 20.35 | [17.93, 22.83] | 15.1% | 759 | not eligible (<20% of frames) |

## Per-bin Success by family (Car, OPE)

| Dataset | Bin | floor | last_box | M2-Track | MBPTrack | TrackAny3D | TrackAny3D − floor [95% CI] |
|---|---|---:|---:|---:|---:|---:|---|
| KITTI | overall (incl. frame 0) | 23.86 | 20.22 | 67.42 | 73.66 | 73.40 | — |
| KITTI | pts <50 | 26.60 | 25.28 | 54.59 | 60.07 | 60.08 | 33.47 [25.97, 40.56] |
| KITTI | pts 50–199 | 17.59 | 17.97 | 72.49 | 78.87 | 76.86 | 59.27 [47.89, 66.86] |
| KITTI | pts ≥200 | 21.80 | 12.59 | 75.26 | 82.52 | 83.27 | 61.47 [50.54, 71.02] |
| KITTI | motion <0.5 m | 24.64 | 23.82 | 68.10 | 74.18 | 74.34 | 49.69 [41.86, 56.49] |
| KITTI | motion ≥0.5 m | 15.77 | 3.23 | 62.96 | 70.17 | 68.61 | 52.84 [24.90, 68.08] |
| nuScenes | overall (incl. frame 0) | 39.59 | 57.39 | 57.21 | 62.46 | 59.29 | — |
| nuScenes | pts <10 | 42.80 | 58.19 | 44.28 | 52.43 | 48.69 | 5.90 [4.29, 7.49] |
| nuScenes | pts 10–24 | 24.09 | 51.48 | 63.27 | 67.08 | 62.97 | 38.88 [36.79, 40.95] |
| nuScenes | pts ≥25 | 27.06 | 49.38 | 73.09 | 73.90 | 71.73 | 44.67 [42.47, 46.95] |
| nuScenes | motion <2.5 m | 41.13 | 64.11 | 59.54 | 66.08 | 62.49 | 21.35 [19.70, 23.00] |
| nuScenes | motion ≥2.5 m | 7.17 | 2.93 | 27.42 | 27.52 | 25.47 | 18.31 [16.08, 20.65] |

## KITTI other classes (informational; not part of the headline rule)

| Class | Bin | Best family | Gap | 95% CI | Share | Tracklets | Status | TrackAny3D overall S / P |
|---|---|---|---:|---|---:|---:|---|---|
| Pedestrian | pts <50 | MBPTrack | 25.53 | [18.32, 32.41] | 10.7% | 39 | not eligible (<20% of frames) | 59.59 / 85.06 |
| Pedestrian | pts 50–199 | MBPTrack | 37.42 | [31.97, 42.96] | 44.9% | 59 | KILL cell | 59.59 / 85.06 |
| Pedestrian | pts ≥200 | MBPTrack | 46.55 | [40.18, 52.60] | 44.4% | 55 | KILL cell | 59.59 / 85.06 |
| Pedestrian | motion <0.5 m | MBPTrack | 40.19 | [35.41, 44.96] | 99.9% | 62 | KILL cell | 59.59 / 85.06 |
| Pedestrian | motion ≥0.5 m | MBPTrack | 49.17 | [29.08, 67.50] | 0.1% | 6 | not eligible (<30 tracklets) | 59.59 / 85.06 |
| Van | pts <50 | TrackAny3D | 27.89 | [1.09, 45.18] | 40.7% | 13 | not eligible (<30 tracklets) | 69.62 / 82.48 |
| Van | pts 50–199 | TrackAny3D | 51.58 | [28.09, 65.95] | 31.8% | 15 | not eligible (<30 tracklets) | 69.62 / 82.48 |
| Van | pts ≥200 | TrackAny3D | 47.02 | [26.99, 74.34] | 27.5% | 11 | not eligible (<30 tracklets) | 69.62 / 82.48 |
| Van | motion <0.5 m | TrackAny3D | 41.18 | [24.94, 55.46] | 98.8% | 14 | not eligible (<30 tracklets) | 69.62 / 82.48 |
| Van | motion ≥0.5 m | TrackAny3D | 1.00 | [0.00, 15.00] | 1.2% | 2 | not eligible (<30 tracklets) | 69.62 / 82.48 |
| Cyclist | pts <50 | TrackAny3D | -3.16 | [-10.36, 2.50] | 6.3% | 5 | not eligible (<30 tracklets) | 74.26 / 93.53 |
| Cyclist | pts 50–199 | MBPTrack | 9.61 | [-3.60, 27.15] | 42.3% | 7 | not eligible (<30 tracklets) | 74.26 / 93.53 |
| Cyclist | pts ≥200 | MBPTrack | 31.69 | [12.11, 53.09] | 51.3% | 8 | not eligible (<30 tracklets) | 74.26 / 93.53 |
| Cyclist | motion <0.5 m | MBPTrack | 20.00 | [5.95, 36.39] | 100.0% | 8 | not eligible (<30 tracklets) | 74.26 / 93.53 |

## Rule outcome

- Reproduction check: the same code with the first-test families (M2-Track, MBPTrack) reproduces the recorded KITTI and nuScenes Car cells exactly (max |Δ| = 0.0); first-test status recomputed = INCONCLUSIVE.
- KITTI: KILL holds on every eligible bin = True; GO cells = none.
- nuScenes: KILL holds on every eligible bin = False (not KILL: pts:pts0); GO cells = none.
- **Formal status after the single re-application with TrackAny3D: INCONCLUSIVE.** No further re-application. Under PREREG §8 the rule is re-applied once with TrackAny3D; this is that re-application.
