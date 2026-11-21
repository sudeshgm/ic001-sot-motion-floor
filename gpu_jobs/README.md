# IC001 GPU jobs — FINAL specs for GPU Bot (free Kaggle T4). Not sent by the CPU agent.

Pre-registration: frozen, see `PREREG.md` and `PREREG.githash` (commit e31629c99566bd989094d3a3922374863f0ac163).
Approvals (Sudesh's own words, relayed and verified by Idea Launcher, 21 Nov 2026): go with IC001; KITTI download; free Kaggle GPU; private Kaggle dataset. **No paid compute. No money spent.**

| Spec | What | Est. T4 time (estimate) |
|---|---|---|
| `m2track_first_test.md` | M2-Track (Open3DSOT checkpoints) KITTI Car + Pedestrian (+ nuScenes Car, phase 2), protocols ope + reinit | ≈ 0.5–1 T4-h |
| `mbptrack_first_test.md` | MBPTrack (official checkpoints) KITTI Car/Ped/Van/Cyc (+ nuScenes, phase 2), ope + reinit | ≈ 0.5–1 T4-h + env setup |
| `m2track_oxts_crop.md` | **SECONDARY** (#1): M2-Track KITTI Car with an oxts-compensated search crop; same commit/checkpoint as the first test | ≈ 0.3 T4-h |
| `bat_kitti_car.md` | **SECONDARY** (#2): BAT on KITTI Car, official Open3DSOT `bat_kitti_car.ckpt`; same env as M2-Track | ≈ 0.3 T4-h |
| `dump_open3dsot.py` | Harness: Open3DSOT model → per-frame CSV (untested on GPU) | — |
| `dump_open3dsot_oxts.py` | Harness: M2-Track with oxts-compensated previous box/crop (yaw-only); KITTI only (untested on GPU) | — |
| `dump_mbptrack.py` | Harness: MBPTrack → per-frame CSV, camera→velodyne conversion + self-check (untested on GPU) | — |

## Data: PRIVATE Kaggle dataset (never public; licence-restricted)
- **KITTI (CC BY-NC-SA 3.0, non-commercial):** create a **private** Kaggle dataset `ic001-kitti-0019-0020` from the box folder `/workspace/ic001/data/kitti/` (contents: `velodyne/0019/*.bin` (1,060 files), `velodyne/0020/*.bin` (836 files), `label_02/*.txt`, `calib/*.txt`, `oxts/*.txt`, ~3.67 GB) plus `data_manifest/kitti_sha256.txt` from this repo. Visibility must be Private; do not add collaborators.
  - On Kaggle, first verify: `cd /kaggle/input/ic001-kitti-0019-0020/kitti && sha256sum -c kitti_sha256.txt --quiet` (paths in the manifest are relative to `kitti/`). Any mismatch → stop.
  - The `m2track_oxts_crop` job needs `oxts/0019.txt` and `oxts/0020.txt`. They are already in this layout and in the manifest; if an already-uploaded dataset is missing them, add `oxts/` and re-verify the manifest before that job.
  - The same root works for both loaders: Open3DSOT `path:` and MBPTrack `data_root_dir:` (`velodyne/`, `label_02/`, `calib/` directly under it).
- **nuScenes (phase 2, CC BY-NC-SA 4.0 + nuScenes terms):** only after the CPU agent has the val keyframes on the box; a second private dataset `ic001-nuscenes-val-keyframes` (val `samples/LIDAR_TOP` + `v1.0-trainval/*.json`). Not available yet.

## What comes back to the box (small files only)
Per job, per (dataset, class): one CSV with both protocols, exactly:
```
dataset,category,tracklet_id,frame_idx,protocol,method,cx,cy,cz,w,l,h,yaw
```
- Boxes in the Open3DSOT scoring frame: KITTI velodyne frame of that frame; nuScenes global. `yaw` = rotation about +z of the box length axis. Frame 0 = the given GT box.
- `tracklet_id`: KITTI `"%04d_%d" % (scene, track_id)`; nuScenes `instance_token`. `frame_idx` 0-based in frame order. `protocol` ∈ {`ope`, `reinit`}. `method` ∈ {`m2track`, `mbptrack`, `m2track_oxts`, `bat`}.
- Also: the repo's own Success/Precision printout for protocol ope (V1), harness printouts, `pip freeze` / `conda list`, `nvidia-smi`, tracker repo commit, SHA-256 of each checkpoint, wall times, list of environment deviations.
- Never return point clouds, features or dataset files.

## Protocols (PREREG §5)
- `ope`: standard one-pass evaluation (frame-1 GT only).
- `reinit`: at every t ≥ 1 the tracker restarts from GT_{t−1} (box incl. size; M2-Track history = GT; MBPTrack memory reset from the GT box, i.e. a 2-frame tracklet [t−1, t]).

## V1 stop rule (PREREG §10, restated in `PREREG_ADDENDUM_2026-11-21.md`)
Applies only to the first-test jobs (`m2track_first_test.md`, `mbptrack_first_test.md`), protocol ope, KITTI Car. The repo's own number must be within 1.0 Success of **either** the paper value **or** the documented official-checkpoint value, when one exists: M2-Track paper 65.5 / Open3DSOT README checkpoint 67.43; MBPTrack paper 73.4 (no separate checkpoint value). Outside → stop and report; no tuning, no re-runs with other seeds/settings.

The SECONDARY jobs (`m2track_oxts_crop.md`, `bat_kitti_car.md`) are **not** part of V1 or of the frozen GO / KILL rule. Do not apply this stop rule to them.
