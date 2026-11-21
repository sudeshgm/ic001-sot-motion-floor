# GPU job: M2-Track + MBPTrack on nuScenes val (FINAL; free Kaggle T4 only)

**Why GPU:** same as the KITTI first-test jobs (`pointnet2_ops` / pytorch3d). Inference only. **No money spent** — free Kaggle T4 only; stop rather than use paid compute. **Private Kaggle dataset only** (nuScenes Terms of Use prohibit redistribution; CC BY-NC-SA 4.0).
**Pre-registration:** frozen at `e31629c99566bd989094d3a3922374863f0ac163` (`PREREG.md`). V1 references follow `PREREG_ADDENDUM_2026-11-21.md`. Approvals: `gpu_jobs/README.md`.
**Scope:** official first-test families on nuScenes val keyframes, protocols `ope` + `reinit`. This job is required for the frozen GO / KILL rule (both datasets). It is **not** a V1 gate (V1 still gates on KITTI Car, already run). The nuScenes Car ±1.0 comparison is informational: record it, do not tune.

Headline class is **Car**. MBPTrack official checkpoints also cover Pedestrian, Truck, Trailer and Bus. Bicycle and Motorcycle have no official first-test checkpoint; do not invent weights.

## Private Kaggle dataset `ic001-nuscenes-val-keyframes`

**Never public. Do not add collaborators.** nuScenes terms say no redistribution.

Create the dataset from the box folder `/workspace/ic001/data/nuscenes/` plus the manifests in this repo:

| Path (relative to dataset root) | What | Size |
|---|---|---|
| `samples/LIDAR_TOP/*.pcd.bin` | 6,019 val LIDAR_TOP keyframes | 4,179,568,000 B |
| `v1.0-trainval/*.json` | slim **val-only** tables (150 val scenes; see `DATA.md`) | 155,517,152 B |
| `nuscenes_val_lidar_sha256.txt` | SHA-256 of every LIDAR file (copy from `data_manifest/`) | — |
| `nuscenes_valonly_json_sha256.txt` | SHA-256 of the slim JSON tables (copy from `data_manifest/`) | — |

**Payload size:** 4,335,085,152 B ≈ **4.04 GiB** of data, plus a few hundred KB of manifests. No sweeps, no cameras, no full trainval JSON, no `.tgz`.

On Kaggle, first verify (paths in both manifests are relative to this root):

```bash
cd /kaggle/input/ic001-nuscenes-val-keyframes
sha256sum -c nuscenes_val_lidar_sha256.txt --quiet
sha256sum -c nuscenes_valonly_json_sha256.txt --quiet
# expect 6019 LIDAR files
find samples/LIDAR_TOP -name '*.pcd.bin' | wc -l
```

Any mismatch → stop and report. The same root is `path:` for Open3DSOT and `dataset_cfg.data_root_dir` for MBPTrack (`v1.0-trainval/` and `samples/LIDAR_TOP/` directly under it).

## Pinned commits (same as the KITTI first test)

- Open3DSOT (MIT): `https://github.com/Ghostish/Open3DSOT` at `f08451ddf133d40c9bfadd6358040c569b5f71a9`
- MBPTrack3D (**no licence file:** evaluation use only; do not redistribute code or weights): `https://github.com/slothfulxtx/MBPTrack3D` at `e5670d122a8fc129189ef826ec470bbeb51eb5ef`
- IC001 repo, branch `cpu-agent`: `gpu_jobs/dump_open3dsot.py` (already has a nuScenes `tracklet_id` = `instance_token` branch) and `gpu_jobs/dump_mbptrack.py` (**nuScenes branch still to be added in this job**; see below)
- Pre-registration hash: `e31629c99566bd989094d3a3922374863f0ac163`

Env setup: reuse the KITTI kernels' environments (`m2track_first_test.md`, `mbptrack_first_test.md` Plan A, then Plan B only if Plan A fails). Internet ON for git/pip/checkpoint download. Persistence off.

## Checkpoints (liveness checked 21 Nov 2026, 1-byte HTTP range only; do not substitute)

### M2-Track (Open3DSOT README checkpoint; documented Success 57.22 / 65.72)

| File | URL | Size (B) | 1-byte range, 21 Nov 2026 |
|---|---|---|---|
| `pretrained_models/mmtrack_nuscenes_car.ckpt` | `https://raw.githubusercontent.com/Ghostish/Open3DSOT/f08451ddf133d40c9bfadd6358040c569b5f71a9/pretrained_models/mmtrack_nuscenes_car.ckpt` | 27,073,489 | HTTP 206, `Content-Range: bytes 0-0/27073489` |

This file is a regular GitHub blob at the pinned commit (not LFS). After checkout, `sha256sum` it and record the hash. Size must be 27,073,489 B.

### MBPTrack (official Drive folder `1bYa_oLTbQcnm-wQO89Dv5km8HH_GIqSv`)

Download: `curl -L -o pretrained/<file> "https://drive.usercontent.google.com/download?id=<id>&export=download&confirm=t"`. Check the size, record SHA-256. If a file is unreachable: stop and report; never substitute weights.

| File | Drive id | Size (B) | 1-byte range, 21 Nov 2026 |
|---|---|---|---|
| `mbptrack_nuscenes_kitti_car.ckpt` | `1Exiyq0YP5q4Qd--ZUKWiVq7HInkAG4cn` | 23,509,583 | HTTP 206, `bytes 0-0/23509583`, `filename="mbptrack_nuscenes_kitti_car.ckpt"` |
| `mbptrack_nuscenes_kitti_ped.ckpt` | `1oicqgIqqyfEMYk2YCYE7xUXpKOFgsOmi` | 23,509,647 | HTTP 206, `bytes 0-0/23509647` |
| `mbptrack_nuscenes_kitti_truck.ckpt` | `1gx_CHAsEk0PZdY3Q5y7vxqfRM_3ZbSVw` | 23,509,647 | HTTP 206, `bytes 0-0/23509647` |
| `mbptrack_nuscenes_kitti_trailer.ckpt` | `1zgdR7IX6oHtPVmxqyGMRC3LSIMG0IorK` | 23,509,263 | HTTP 206, `bytes 0-0/23509263` |
| `mbptrack_nuscenes_kitti_bus.ckpt` | `1FE2dJVUPKbkYrxyVmB3S0opqgLztfMrl` | 23,509,199 | HTTP 206, `bytes 0-0/23509199` |

## Per-frame dump format (must match the KITTI dumps)

```
dataset,category,tracklet_id,frame_idx,protocol,method,cx,cy,cz,w,l,h,yaw
```

- `dataset=nuscenes`. `category` is the official config name (`Car`, `Pedestrian`, `Truck`, `Trailer`, `Bus`).
- `tracklet_id` = nuScenes `instance_token`. `frame_idx` 0-based in the same order as `ic001.data.nuscenes.index_nuscenes` (val, keyframes only, `min_points=1` on the first box). Check per-tracklet frame counts against that indexer before scoring is trusted.
- Boxes in the Open3DSOT / IC001 scoring frame: **nuScenes global**. `yaw` = rotation about +z of the box length axis. Frame 0 = the given GT box.
- `protocol` ∈ {`ope`, `reinit`}. `method` ∈ {`m2track`, `mbptrack`}.
- `ope`: frame-1 GT only. `reinit`: at every t ≥ 1 the tracker restarts from GT_{t−1} (box incl. size; M2-Track history = GT; MBPTrack memory reset from the GT box, i.e. a 2-frame tracklet [t−1, t]; PREREG choice j).

`dump_open3dsot.py` already writes this schema and already uses `instance_token` when `cfg.dataset != "kitti"`. `dump_mbptrack.py` still asserts a KITTI dataset: extend it with a `NuscenesKITTIMem` branch, write `instance_token` as `tracklet_id`, and emit boxes in the global frame (**no** KITTI camera→velodyne conversion). Self-check: converted/emitted frame-0 boxes must match `index_nuscenes` GT (centres and yaw); report the max error. Do not "fix" a failing self-check silently.

## Steps

Kaggle notebook: GPU T4 x1, Internet ON, Persistence off. Add **only** the private dataset `ic001-nuscenes-val-keyframes`.

### A. M2-Track, nuScenes Car

1. In `cfgs/M2_Track_nuscene.yaml` set `path: /kaggle/input/ic001-nuscenes-val-keyframes` (keep `version: v1.0-trainval`, `category_name: Car`, `test_split: val`, `key_frame_only: True`, `coordinate_mode: velodyne`, `up_axis [0,0,1]`, `IoU_space: 3`). `pip install nuscenes-devkit` if the Open3DSOT loader requires it.
2. **Repo's own script (informational V1):** `python main.py --cfg cfgs/M2_Track_nuscene.yaml --checkpoint pretrained_models/mmtrack_nuscenes_car.ckpt --test --workers 2` → record Success/Precision.
3. **Per-frame dump:** `python /kaggle/working/ic001/gpu_jobs/dump_open3dsot.py --cfg cfgs/M2_Track_nuscene.yaml --checkpoint pretrained_models/mmtrack_nuscenes_car.ckpt --category Car --method m2track --protocols ope reinit --path /kaggle/input/ic001-nuscenes-val-keyframes --out /kaggle/working/m2track_nuscenes_car.csv`
   The printed `ope` Success must equal step 2 (±0.01); otherwise report the mismatch.

### B. MBPTrack, official classes (Car first)

For each pair (config, checkpoint, category):

| Config | Checkpoint | Category |
|---|---|---|
| `configs/mbptrack_nuscenes_kitti_car_cfg.yaml` | `pretrained/mbptrack_nuscenes_kitti_car.ckpt` | Car |
| `configs/mbptrack_nuscenes_kitti_ped_cfg.yaml` | `pretrained/mbptrack_nuscenes_kitti_ped.ckpt` | Pedestrian |
| `configs/mbptrack_nuscenes_kitti_truck_cfg.yaml` | `pretrained/mbptrack_nuscenes_kitti_truck.ckpt` | Truck |
| `configs/mbptrack_nuscenes_kitti_trailer_cfg.yaml` | `pretrained/mbptrack_nuscenes_kitti_trailer.ckpt` | Trailer |
| `configs/mbptrack_nuscenes_kitti_bus_cfg.yaml` | `pretrained/mbptrack_nuscenes_kitti_bus.ckpt` | Bus |

1. Set `dataset_cfg.data_root_dir: /kaggle/input/ic001-nuscenes-val-keyframes/` (keep `dataset_type: NuscenesKITTIMem`, `test_version: v1.0-trainval`, official `category_name`).
2. **Repo's own script (Car is the informational V1):** `python main.py configs/mbptrack_nuscenes_kitti_car_cfg.yaml --phase test --resume_from pretrained/mbptrack_nuscenes_kitti_car.ckpt --gpus 0` → record Success/Precision. Then the other classes (informational).
3. **Per-frame dump** (after the nuScenes harness branch exists): `python /kaggle/working/ic001/gpu_jobs/dump_mbptrack.py configs/mbptrack_nuscenes_kitti_<cls>_cfg.yaml --ckpt pretrained/mbptrack_nuscenes_kitti_<cls>.ckpt --data-root /kaggle/input/ic001-nuscenes-val-keyframes --category <Category> --out /kaggle/working/mbptrack_nuscenes_<cls>.csv`
   Checks: printed `ope` Success equals step 2 (±0.01); frame-0 self-check vs `index_nuscenes` is exact enough to report (centres / yaw). Either failing → report, do not "fix" silently.

## Informational V1 references (`PREREG_ADDENDUM_2026-11-21.md`)

Protocol (a) / `ope`, nuScenes Car only. Same ±1.0 Success tolerance as the restated rule. **Not a study stop** (the gate is KITTI Car). Still: no tuning, no re-runs with other seeds or settings if the number is off — just report it.

| Tracker | Paper Success / Precision | Documented checkpoint Success / Precision | Pass if within 1.0 of |
|---|---|---|---|
| M2-Track | **55.85** / 65.09 (arXiv:2203.01730v1, Table 2) | **57.22** / 65.72 (Open3DSOT README, `mmtrack_nuscenes_car.ckpt`, verified 21 Nov 2026) | either 55.85 or 57.22 |
| MBPTrack | **62.47** / 70.41 (arXiv:2303.05071v1, Table 3) | none found as a separate number | 62.47 only |

## Return (small files only)

`m2track_nuscenes_car.csv`, `mbptrack_nuscenes_{car,ped,truck,trailer,bus}.csv`, step-2 logs, harness printouts, `pip freeze` / `conda list`, `nvidia-smi`, tracker repo commits, SHA-256 of each checkpoint, wall times, self-check errors, list of environment deviations. Never return point clouds, features or dataset files.

## Expected runtime (estimate)

Val frame counts at `min_points=1` (checked on the box against the frozen indexer): Car 3,660 tracklets / 64,159 frames; Pedestrian 1,858 / 33,227; Truck 608 / 13,587; Trailer 152 / 3,352; Bus 120 / 2,953. Total for MBPTrack's five classes: 117,278 frames; M2-Track runs Car only.

The KITTI first-test kernel (M2-Track Car+Ped + MBPTrack four KITTI classes, both protocols, plus setup) took 3,622 s on a free T4. nuScenes is roughly 5× (M2) to 8× (MBP) those frame counts, times two protocols, plus one V1 `ope` pass. Estimate:

- M2-Track nuScenes Car (V1 + dump of ope and reinit): **≈ 1–2 T4-h** plus any leftover Open3DSOT setup
- MBPTrack five classes (V1 on Car + dumps): **≈ 2–4 T4-h** plus Plan A env if it is not already built (0.5–1.5 T4-h)
- **Combined: ≈ 3–6 T4-h**, which fits in one free 12-hour T4 session if the env is reused; otherwise two kernels (A then B). No paid compute.

If a session will run out of time, finish Car (both trackers) first and return those CSVs; then continue the remaining MBPTrack classes in a second free kernel.
