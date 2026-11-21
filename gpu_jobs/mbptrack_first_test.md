# GPU job: MBPTrack inference for the IC001 first test (FINAL; free Kaggle T4)

**Why GPU:** CUDA point ops + pytorch3d. Inference only. **No money spent** — free Kaggle T4 only.
**Pre-registration:** frozen at `e31629c99566bd989094d3a3922374863f0ac163`. Approvals: `gpu_jobs/README.md`.

## Inputs
- Code: `https://github.com/slothfulxtx/MBPTrack3D`, checked 21 Nov 2026 at commit `e5670d122a8fc129189ef826ec470bbeb51eb5ef` — check out exactly this commit. **No licence file:** evaluation use only; do not redistribute code or weights.
- Checkpoints: Google Drive folder `1bYa_oLTbQcnm-wQO89Dv5km8HH_GIqSv` (README link). **Liveness checked 21 Nov 2026 by 1-byte HTTP range requests: all 9 files reachable (HTTP 206)**:

  | File | Drive id | Size (B) |
  |---|---|---|
  | mbptrack_kitti_car.ckpt | 1dUu5AuNXP7Yrc2Yp1EVSHvy4zo0pt-Kk | 23,509,135 |
  | mbptrack_kitti_ped.ckpt | 1eASHsUOSVALsz7jL8DDHx0stxAlWalCd | 23,509,135 |
  | mbptrack_kitti_van.ckpt | 19z4ymUzn1ccUcuErBIgkrDa3sovAHhz7 | 23,509,135 |
  | mbptrack_kitti_cyc.ckpt | 1WqwUguRqTg_qGK9JxvAFgTv4xYrPTt0U | 23,509,135 |
  | mbptrack_nuscenes_kitti_car.ckpt | 1Exiyq0YP5q4Qd--ZUKWiVq7HInkAG4cn | 23,509,583 |
  | mbptrack_nuscenes_kitti_ped.ckpt | 1oicqgIqqyfEMYk2YCYE7xUXpKOFgsOmi | 23,509,647 |
  | mbptrack_nuscenes_kitti_truck.ckpt | 1gx_CHAsEk0PZdY3Q5y7vxqfRM_3ZbSVw | 23,509,647 |
  | mbptrack_nuscenes_kitti_trailer.ckpt | 1zgdR7IX6oHtPVmxqyGMRC3LSIMG0IorK | 23,509,263 |
  | mbptrack_nuscenes_kitti_bus.ckpt | 1FE2dJVUPKbkYrxyVmB3S0opqgLztfMrl | 23,509,199 |

  Download: `curl -L -o pretrained/<file> "https://drive.usercontent.google.com/download?id=<id>&export=download&confirm=t"`; check the size matches the table, record SHA-256. If a file is unreachable: stop and report; never substitute weights.
- Data: private Kaggle dataset `ic001-kitti-0019-0020` (verify manifest first).
- IC001 repo branch `cpu-agent` → `gpu_jobs/dump_mbptrack.py`.

## Environment (Kaggle T4, sm_75)
**Plan A (faithful pins, from the README / `freeze.yml`):** Python 3.8, torch 1.8.0 + CUDA 11.1, torchvision 0.9.0, pytorch-lightning 1.5.10, pytorch3d 0.6.2.
```bash
curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj bin/micromamba
./bin/micromamba create -y -p /kaggle/working/mbp python=3.8 -c conda-forge
/kaggle/working/mbp/bin/pip install torch==1.8.0+cu111 torchvision==0.9.0+cu111 -f https://download.pytorch.org/whl/torch_stable.html
/kaggle/working/mbp/bin/pip install pytorch-lightning==1.5.10 addict pyyaml pandas pyquaternion shapely tqdm pynvml nuscenes-devkit
/kaggle/working/mbp/bin/pip install "git+https://github.com/facebookresearch/pytorch3d.git@v0.6.2"   # needs nvcc 11.x; see Plan B if it fails
cd MBPTrack3D/pointnet2_ops && TORCH_CUDA_ARCH_LIST="7.5" /kaggle/working/mbp/bin/pip install . && cd -
```
(Kaggle's system CUDA toolkit may not be 11.1; install `cudatoolkit-dev=11.1` / `cuda-nvcc=11.1` from conda-forge/nvidia into the env if compilation needs it.)
**Plan B** (only if Plan A fails after ≤ 2 h): Kaggle's own torch + pytorch3d built from source + rebuilt `pointnet2_ops`; list every deviation. V1 decides whether Plan B numbers are usable.

## Steps (KITTI, phase 1) — Car first, then Ped, Van, Cyc
1. In `configs/mbptrack_kitti_<car|ped|van|cyc>_cfg.yaml` set `dataset_cfg.data_root_dir: /kaggle/input/ic001-kitti-0019-0020/kitti/` (keep `coordinate_mode: camera`, `up_axis [0,-1,0]`).
2. **V1 (repo's own script):** `python main.py configs/mbptrack_kitti_car_cfg.yaml --phase test --resume_from pretrained/mbptrack_kitti_car.ckpt --gpus 0` → Success/Precision. Car must be within 1.0 of **73.4** (arXiv:2303.05071v1 Tab. 1). Others informational (Ped 68.6, Van 61.3, Cyc 76.7). Car fails → stop, report.
3. **Per-frame dump:** `python /kaggle/working/ic001/gpu_jobs/dump_mbptrack.py configs/mbptrack_kitti_<cls>_cfg.yaml --ckpt pretrained/mbptrack_kitti_<cls>.ckpt --data-root /kaggle/input/ic001-kitti-0019-0020/kitti --category <Car|Pedestrian|Van|Cyclist> --out /kaggle/working/mbptrack_kitti_<cls>.csv`
   Checks: printed `ope` Success equals step 2 (±0.01); the camera→velodyne self-check error < 1e-4. Either failing → report, do not "fix" silently.
   `reinit` = 2-frame tracklets [t−1, t] → memory reset from GT_{t−1} (PREREG choice j).

## Phase 2 (nuScenes) — only when the private nuScenes dataset exists
Configs `mbptrack_nuscenes_kitti_<car|ped|truck|trailer|bus>_cfg.yaml`, `data_root_dir` = nuScenes root, `test_version: v1.0-trainval`. The harness's nuScenes branch is not written yet: extend `dump_mbptrack.py` with `NuscenesKITTIMem`, write `instance_token` as `tracklet_id`, boxes in global frame (no conversion), and check per-tracklet frame counts against `ic001.data.nuscenes.index_nuscenes`. V1-informational vs paper nuScenes Car 62.47.

## Return
`mbptrack_kitti_{car,ped,van,cyc}.csv`, step-2 logs, harness printouts, `conda list`/`pip freeze`, `nvidia-smi`, checkpoint SHA-256s, wall times, deviations. Nothing else.

## Expected runtime (estimate)
MBPTrack runs ~50 FPS on a 3090; KITTI test ≈ 14k frames over 4 classes; reinit adds one extra init per frame (~2–3×). ≈ 20–40 min on a T4 plus setup (Plan A env 30–90 min).
