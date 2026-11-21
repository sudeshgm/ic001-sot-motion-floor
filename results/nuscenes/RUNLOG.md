# nuScenes RUNLOG (frozen PREREG e31629c)

- 2026-11-21 14:42–15:01 IST: val-only slim metadata built and verified (ALL_IDENTICAL). Originals deleted (2.60 GB freed). See DATA.md.
- 2026-11-21 15:02 IST: `nohup scripts/stream_nuscenes.sh` resumed (logs: /workspace/ic001/logs/nuscenes). 10 keyframe archives, 44.9 GB in total.
  The measured CDN throughput is about 0.8 MB/s per connection, while the same box gets 6.2 MB/s from another host. At that rate the ETA is about 15 h.

- 2026-11-21 17:12–17:17 IST: archive 10 rerun with `MIN_FREE_GB=6` (Idea Launcher). 6,019 / 6,019 val LIDAR_TOP keyframes on disk. See DATA.md.

## 2026-11-21 17:23–17:30 IST — frozen motion floor + controls on nuScenes val

- PREREG frozen at e31629c99566bd989094d3a3922374863f0ac163 (`PREREG.githash`); real-data guard allowed the run. Code at branch `cpu-agent`, commit with this file.
- Data: `/workspace/ic001/data/nuscenes` (slim val-only `v1.0-trainval/` + 6,019 `samples/LIDAR_TOP` keyframes). Manifest `data_manifest/nuscenes_val_lidar_sha256.txt`. Licence note in DATA.md.
- Classes: all 7 official nuScenes tracking classes the indexer supports (Open3DSOT / MBPTrack family list). M2-Track has a nuScenes checkpoint for Car only; MBPTrack official checkpoints cover Car, Pedestrian, Truck, Trailer, Bus. Bicycle and Motorcycle have no first-test learned checkpoint; the floor still ran on them. `min_points=1` on the first box (PREREG §2). Point counts from `num_lidar_pts` (h). Primary hard = `<10` points ∪ high motion (e).
- Count check (matches `results/nuscenes/valonly_verification.json` and the known Car figure): Car 3,660 tracklets / 64,159 frames; Pedestrian 1,858 / 33,227; Truck 608 / 13,587; Trailer 152 / 3,352; Bus 120 / 2,953; Bicycle 153 / 2,292; Motorcycle 136 / 2,419. Missing LIDAR files: 0 for every class. Every class ran.
- Commands (per class C): `python -m ic001.run floor --dataset nuscenes --root /workspace/ic001/data/nuscenes --category C --out results/nuscenes/nuscenes_C_floor.csv`; `python -m ic001.run evaluate --dataset nuscenes --root ... --category C --floor ... --out results/nuscenes/nuscenes_C_floor_eval.json`; then gzip the per-frame CSV. V4: `python -m ic001.run sanity` for Car and Pedestrian.
- Merge rule (decided from GT only, `results/nuscenes/nuscenes_gt_census.json`, before any score was looked at): every point bin of Car and Pedestrian has ≥ 30 distinct tracklets (Car pts0/1/2: 3,304 / 1,989 / 1,601; Pedestrian: 1,772 / 953 / 560) → **no merge**; nuScenes bins stay <10 / 10–24 / ≥25.
- Under-powered (< 30 tracklets): Pedestrian high-motion (10 tracklets, 10 frames); Bicycle high-motion (12 tracklets, 130 frames); Trailer high-motion (21 tracklets, 207 frames). These cannot drive GO / KILL.
- V4 ground filter (20 random frames, seed 0, GT box + 0.5 m BEV): Car median 0.095 removed (0.00–1.00), Pedestrian median 0.041 (0.00–1.00). Reported, not tuned.
- V3: a second full nuScenes run was not repeated (single-run instruction). The same frozen code already passed V3 (byte-identical CSVs) on KITTI.
- Deviations: none. The CV control is reported under re-init only (identical to last box under OPE, PREREG (d)). No `cv_snap_noego` control (KITTI only).
- Learned trackers on nuScenes are not run yet (see `gpu_jobs/nuscenes_learned.md`) → decision rule NOT applied.

### Overall Success / Precision (incl. frame 0)

| Class | Tracklets / frames | OPE last_box | OPE floor (cv_snap) | Re-init last_box | Re-init CV | Re-init floor (cv_snap) |
|---|---|---|---|---|---|---|
| Car | 3,660 / 64,159 | 57.39 / 63.57 | 39.59 / 42.16 | 78.16 / 78.05 | 90.36 / 92.94 | 83.79 / 88.54 |
| Pedestrian | 1,858 / 33,227 | 21.42 / 33.32 | 16.97 / 29.70 | 38.04 / 78.56 | 78.41 / 94.21 | 70.30 / 92.38 |
| Truck | 608 / 13,587 | 62.67 / 63.20 | 34.14 / 30.40 | 84.67 / 80.27 | 92.51 / 92.90 | 82.96 / 82.96 |
| Trailer | 152 / 3,352 | 73.88 / 71.17 | 39.16 / 31.76 | 91.29 / 86.06 | 93.97 / 93.42 | 84.03 / 78.98 |
| Bus | 120 / 2,953 | 44.02 / 40.35 | 26.98 / 20.48 | 77.59 / 59.00 | 90.66 / 89.49 | 79.08 / 73.96 |
| Bicycle | 153 / 2,292 | 49.37 / 71.25 | 31.49 / 48.40 | 75.62 / 84.53 | 84.74 / 94.53 | 75.89 / 92.16 |
| Motorcycle | 136 / 2,419 | 42.39 / 56.61 | 28.35 / 37.58 | 66.73 / 72.88 | 82.09 / 91.58 | 75.98 / 89.98 |

### Per-bin floor (cv_snap) Success / Precision, with tracklet counts (frame 0 excluded)

Point bins: pts0 = <10, pts1 = 10–24, pts2 = ≥25. Motion: motLo = <2.5 m, motHi = ≥2.5 m. hard_primary = pts0 ∪ motHi.

**Car (headline)**

| Bin | Frames | Tracklets | OPE last_box | OPE cv_snap | Re-init last_box | Re-init CV | Re-init cv_snap |
|---|---|---|---|---|---|---|---|
| pts0 | 35,909 | 3,304 | 58.19 / 65.32 | 42.80 / 46.30 | 78.70 / 79.57 | 89.89 / 92.47 | 87.28 / 90.64 |
| pts1 | 7,961 | 1,989 | 51.48 / 58.51 | 24.09 / 26.13 | 75.07 / 74.70 | 88.60 / 91.96 | 71.71 / 80.34 |
| pts2 | 16,629 | 1,601 | 49.38 / 54.21 | 27.06 / 28.14 | 73.95 / 71.55 | 90.40 / 92.84 | 78.75 / 85.43 |
| motLo | 51,375 | 3,087 | 64.11 / 72.27 | 41.13 / 44.59 | 88.94 / 90.35 | 92.28 / 94.76 | 85.02 / 89.79 |
| motHi | 9,124 | 759 | 2.93 / 0.00 | 7.17 / 5.27 | 9.19 / 0.00 | 76.18 / 79.81 | 70.87 / 76.91 |
| hard_primary | 40,195 | 3,365 | 52.29 / 58.36 | 39.31 / 42.29 | 71.39 / 71.08 | 88.62 / 91.39 | 85.35 / 89.20 |
| easy_primary | 20,304 | 1,856 | 60.03 / 67.34 | 29.49 / 31.45 | 87.86 / 87.89 | 92.30 / 94.73 | 78.01 / 85.19 |

**Pedestrian**

| Bin | Frames | Tracklets | OPE last_box | OPE cv_snap | Re-init last_box | Re-init CV | Re-init cv_snap |
|---|---|---|---|---|---|---|---|
| pts0 | 24,271 | 1,772 | 16.08 / 28.73 | 11.40 / 24.00 | 32.71 / 76.74 | 76.74 / 93.61 | 70.09 / 91.98 |
| pts1 | 4,054 | 953 | 19.26 / 30.68 | 14.04 / 29.34 | 38.24 / 78.53 | 78.42 / 94.65 | 61.64 / 91.17 |
| pts2 | 3,044 | 560 | 19.69 / 32.76 | 15.37 / 32.71 | 43.18 / 80.02 | 79.31 / 94.85 | 66.15 / 92.52 |
| motLo | 31,359 | 1,798 | 16.84 / 29.38 | 12.13 / 25.54 | 34.45 / 77.32 | 77.22 / 93.88 | 68.63 / 91.94 |
| motHi (under-powered) | 10 | 10 | 2.50 / 0.00 | 2.50 / 0.00 | 2.50 / 0.00 | 16.00 / 38.75 | 17.50 / 40.25 |
| hard_primary | 24,271 | 1,772 | 16.08 / 28.73 | 11.40 / 24.00 | 32.71 / 76.74 | 76.74 / 93.61 | 70.09 / 91.98 |
| easy_primary | 7,098 | 967 | 19.45 / 31.57 | 14.61 / 30.78 | 40.36 / 79.17 | 78.80 / 94.73 | 63.58 / 91.75 |

**Truck**

| Bin | Frames | Tracklets | OPE last_box | OPE cv_snap | Re-init last_box | Re-init CV | Re-init cv_snap |
|---|---|---|---|---|---|---|---|
| pts0 | 5,944 | 540 | 62.30 / 64.01 | 34.90 / 33.27 | 83.86 / 80.58 | 91.88 / 92.13 | 86.28 / 86.62 |
| pts1 | 2,098 | 412 | 60.27 / 60.28 | 23.24 / 17.54 | 84.21 / 79.16 | 92.14 / 92.37 | 72.67 / 72.01 |
| pts2 | 4,937 | 353 | 59.69 / 58.94 | 29.90 / 23.85 | 84.11 / 77.94 | 92.66 / 93.18 | 81.39 / 81.11 |
| motLo | 11,388 | 547 | 68.92 / 70.07 | 34.21 / 30.39 | 91.86 / 90.43 | 93.84 / 94.47 | 83.57 / 83.80 |
| motHi | 1,591 | 120 | 4.10 / 0.00 | 8.97 / 3.89 | 27.86 / 0.00 | 80.60 / 78.99 | 72.58 / 70.47 |
| hard_primary | 6,834 | 552 | 54.70 / 55.67 | 31.67 / 29.55 | 76.94 / 70.09 | 90.69 / 90.84 | 84.39 / 84.42 |
| easy_primary | 6,145 | 405 | 67.96 / 67.93 | 30.50 / 24.47 | 91.89 / 89.64 | 93.92 / 94.49 | 79.81 / 79.65 |

**Trailer**

| Bin | Frames | Tracklets | OPE last_box | OPE cv_snap | Re-init last_box | Re-init CV | Re-init cv_snap |
|---|---|---|---|---|---|---|---|
| pts0 | 1,101 | 129 | 72.50 / 68.50 | 43.95 / 37.41 | 90.29 / 85.41 | 93.05 / 92.31 | 85.79 / 83.44 |
| pts1 | 625 | 114 | 70.61 / 68.11 | 32.48 / 23.16 | 89.37 / 82.70 | 92.72 / 91.38 | 75.75 / 67.47 |
| pts2 | 1,474 | 100 | 73.75 / 71.50 | 32.30 / 24.15 | 92.10 / 86.54 | 94.71 / 94.44 | 84.74 / 78.36 |
| motLo | 2,993 | 143 | 77.22 / 74.63 | 38.14 / 30.36 | 93.62 / 91.31 | 94.47 / 94.16 | 84.04 / 79.48 |
| motHi (under-powered) | 207 | 21 | 7.43 / 0.00 | 10.37 / 1.87 | 52.23 / 0.00 | 83.39 / 77.92 | 73.22 / 56.39 |
| hard_primary | 1,233 | 130 | 65.43 / 61.17 | 40.21 / 33.51 | 86.48 / 76.27 | 92.25 / 91.08 | 84.42 / 80.01 |
| easy_primary | 1,967 | 120 | 77.27 / 75.22 | 33.92 / 25.39 | 93.74 / 91.12 | 94.69 / 94.38 | 82.67 / 76.71 |

**Bus**

| Bin | Frames | Tracklets | OPE last_box | OPE cv_snap | Re-init last_box | Re-init CV | Re-init cv_snap |
|---|---|---|---|---|---|---|---|
| pts0 | 769 | 94 | 41.81 / 36.93 | 25.69 / 18.65 | 73.97 / 55.44 | 87.65 / 85.99 | 80.44 / 77.48 |
| pts1 | 502 | 86 | 45.61 / 42.31 | 18.53 / 11.90 | 76.83 / 59.88 | 90.39 / 89.20 | 70.35 / 63.78 |
| pts2 | 1,562 | 92 | 40.37 / 36.83 | 24.81 / 18.04 | 77.98 / 57.32 | 91.59 / 90.50 | 79.70 / 73.49 |
| motLo | 2,100 | 108 | 54.39 / 51.03 | 28.37 / 21.31 | 87.78 / 77.25 | 92.25 / 91.63 | 79.56 / 74.76 |
| motHi | 733 | 51 | 5.31 / 0.00 | 11.24 / 5.10 | 44.92 / 0.00 | 84.73 / 81.63 | 74.48 / 67.38 |
| hard_primary | 1,303 | 105 | 26.72 / 21.79 | 20.27 / 13.64 | 62.32 / 32.72 | 86.73 / 84.79 | 77.89 / 73.02 |
| easy_primary | 1,530 | 95 | 54.44 / 51.48 | 27.05 / 20.08 | 88.92 / 78.17 | 93.35 / 92.67 | 78.55 / 72.71 |

**Bicycle**

| Bin | Frames | Tracklets | OPE last_box | OPE cv_snap | Re-init last_box | Re-init CV | Re-init cv_snap |
|---|---|---|---|---|---|---|---|
| pts0 | 1,527 | 145 | 47.03 / 71.61 | 30.31 / 48.94 | 75.31 / 84.98 | 84.23 / 93.98 | 77.36 / 92.00 |
| pts1 | 382 | 94 | 46.73 / 66.31 | 17.60 / 35.43 | 70.21 / 78.37 | 82.08 / 94.21 | 63.97 / 89.38 |
| pts2 | 230 | 57 | 36.54 / 57.90 | 17.70 / 32.05 | 71.29 / 81.47 | 83.30 / 95.05 | 70.83 / 92.60 |
| motLo | 2,009 | 146 | 48.65 / 73.67 | 28.25 / 47.60 | 78.60 / 88.82 | 85.30 / 94.99 | 75.05 / 92.24 |
| motHi (under-powered) | 130 | 12 | 2.50 / 0.00 | 2.50 / 0.00 | 2.50 / 0.00 | 59.69 / 80.88 | 62.19 / 81.77 |
| hard_primary | 1,574 | 145 | 45.70 / 69.47 | 29.48 / 47.48 | 73.14 / 82.44 | 83.48 / 93.71 | 76.99 / 91.86 |
| easy_primary | 565 | 93 | 46.27 / 68.40 | 18.89 / 37.00 | 76.28 / 86.15 | 84.49 / 95.31 | 66.66 / 90.88 |

**Motorcycle**

| Bin | Frames | Tracklets | OPE last_box | OPE cv_snap | Re-init last_box | Re-init CV | Re-init cv_snap |
|---|---|---|---|---|---|---|---|
| pts0 | 1,590 | 133 | 39.69 / 54.42 | 27.35 / 37.31 | 64.97 / 71.72 | 80.50 / 90.70 | 76.14 / 89.22 |
| pts1 | 294 | 87 | 38.65 / 54.09 | 14.77 / 26.97 | 61.85 / 67.66 | 79.68 / 91.05 | 65.26 / 87.66 |
| pts2 | 399 | 64 | 36.70 / 52.37 | 18.38 / 25.18 | 66.47 / 72.12 | 84.60 / 92.61 | 75.55 / 91.30 |
| motLo | 1,897 | 117 | 46.47 / 65.01 | 28.57 / 40.75 | 77.51 / 85.77 | 85.67 / 93.75 | 77.74 / 91.51 |
| motHi | 386 | 36 | 2.50 / 0.00 | 2.50 / 0.00 | 2.50 / 0.00 | 58.70 / 77.96 | 59.37 / 78.94 |
| hard_primary | 1,702 | 133 | 37.24 / 50.84 | 25.71 / 34.85 | 60.86 / 67.00 | 79.14 / 89.99 | 75.19 / 88.78 |
| easy_primary | 581 | 73 | 44.28 / 63.33 | 19.61 / 30.94 | 76.46 / 83.77 | 86.88 / 94.26 | 73.02 / 91.17 |

Secondary (point × motion grid, secondary hard) is in the eval JSON files and was not used for any decision.
