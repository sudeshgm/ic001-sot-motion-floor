# GPU job: M2-Track inference for the IC001 first test (FINAL; free Kaggle T4)

**Why GPU:** Open3DSOT needs the `pointnet2_ops` CUDA kernels. Inference only. **No money spent** — free Kaggle T4 only; stop rather than use paid compute.
**Pre-registration:** frozen at `e31629c99566bd989094d3a3922374863f0ac163` (`PREREG.md`). Approvals: see `gpu_jobs/README.md`.

## Inputs
- Code: `https://github.com/Ghostish/Open3DSOT` (MIT), checked 21 Nov 2026 at commit `f08451ddf133d40c9bfadd6358040c569b5f71a9` — check out exactly this commit.
- Checkpoints (in the repo, verified 21 Nov via GitHub API + HTTP range): `pretrained_models/mmtrack_kitti_car.ckpt` (27,073,362 B), `mmtrack_kitti_pedestrian.ckpt` (27,073,489 B), `mmtrack_nuscenes_car.ckpt` (27,073,489 B). Record SHA-256.
- Data: private Kaggle dataset `ic001-kitti-0019-0020` (see README; verify the SHA-256 manifest first).
- IC001 repo (public): `https://github.com/sudeshgm/ic001-sot-motion-floor`, branch `cpu-agent` → `gpu_jobs/dump_open3dsot.py`.

## Kaggle notebook settings
GPU T4 x1, Internet ON (for git/pip), Persistence off. Add the private dataset as input.

## Setup (cells)
```bash
git clone https://github.com/Ghostish/Open3DSOT && cd Open3DSOT && git checkout f08451ddf133d40c9bfadd6358040c569b5f71a9
git clone -b cpu-agent https://github.com/sudeshgm/ic001-sot-motion-floor /kaggle/working/ic001
python -c "import torch;print(torch.__version__, torch.version.cuda)"   # keep Kaggle's torch
grep -v -iE "^torch|^torchvision" requirement.txt > req_notorch.txt && pip install -r req_notorch.txt
# if pytorch-lightning from requirement.txt fails to import with Kaggle torch, use the nearest 1.x that does; record it
TORCH_CUDA_ARCH_LIST="7.5" pip install "git+https://github.com/erikwijmans/Pointnet2_PyTorch.git#egg=pointnet2_ops&subdirectory=pointnet2_ops_lib"
sha256sum pretrained_models/mmtrack_*.ckpt
cd /kaggle/input/ic001-kitti-0019-0020/kitti && sha256sum -c kitti_sha256.txt --quiet && cd -
```

## Steps (KITTI, phase 1)
For CLASS in Car, Pedestrian (Car first):
1. In `cfgs/M2_track_kitti.yaml` set `path: /kaggle/input/ic001-kitti-0019-0020/kitti` and `category_name: CLASS` (leave everything else: `coordinate_mode: velodyne`, `up_axis [0,0,1]`, `IoU_space: 3`, `test_split: test`).
2. **V1 (repo's own script):** `python main.py --cfg cfgs/M2_track_kitti.yaml --checkpoint pretrained_models/mmtrack_kitti_<car|pedestrian>.ckpt --test --workers 2` → record Success/Precision. Car must be within 1.0 of **65.5** (paper). Pedestrian is informational (paper 61.5). If Car fails V1: stop, report, return logs only.
3. **Per-frame dump:** `python /kaggle/working/ic001/gpu_jobs/dump_open3dsot.py --cfg cfgs/M2_track_kitti.yaml --checkpoint pretrained_models/mmtrack_kitti_<car|pedestrian>.ckpt --category CLASS --method m2track --protocols ope reinit --path /kaggle/input/ic001-kitti-0019-0020/kitti --out /kaggle/working/m2track_kitti_<car|pedestrian>.csv`
   The printed `ope` Success must equal step 2 (±0.01); otherwise report the mismatch.

## Phase 2 (nuScenes Car) — only when the private nuScenes dataset exists
`cfgs/M2_Track_nuscene.yaml`: `path:` = nuScenes root, `version: v1.0-trainval`, `test_split: val`, `key_frame_only: True`; `pip install nuscenes-devkit`; V1-informational vs paper 55.85; dump to `m2track_nuscenes_car.csv`.

## Return
`m2track_kitti_car.csv`, `m2track_kitti_pedestrian.csv` (later `m2track_nuscenes_car.csv`), step-2 logs, harness printouts, `pip freeze`, `nvidia-smi`, checkpoint SHA-256s, wall times, deviations. Nothing else.

## Expected runtime (estimate)
KITTI Car 6,424 + Pedestrian 6,088 frames, × 2 protocols (+ V1 run): ~10–20 min of inference on a T4; setup ~15 min.
