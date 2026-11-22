# GPU job: TrackAny3D on KITTI test and nuScenes val (free T4 only)

**Why GPU:** CUDA `pointnet2_ops` plus pytorch3d, same family as the MBPTrack jobs. Inference only. **No money spent** — free T4 only; stop rather than use paid compute. **Private dataset only** for nuScenes (Terms of Use prohibit redistribution; CC BY-NC-SA 4.0) and for KITTI (CC BY-NC-SA 3.0).
**Pre-registration:** frozen at `e31629c99566bd989094d3a3922374863f0ac163` (`PREREG.md` §3, §8). If the first test is INCONCLUSIVE, TrackAny3D is added and the same §8 rule is re-applied once. V1 references follow `PREREG_ADDENDUM_2026-11-21.md` (within 1.0 Success of the paper value or a documented official-checkpoint value).
**Scope:** official TrackAny3D checkpoints, protocols `ope` + `reinit`, KITTI Open3DSOT test split (scenes 0019–0020) and nuScenes val keyframes. Headline class is **Car**. The official release is category-unified: one checkpoint per dataset covers every official class (no per-class fine-tune). Dump every official class the loaders accept. This is not a training job.

## Licence and citation

The official code repository `https://github.com/sallymmx/TrackAny3D` has **no licence file** at the pinned commit (GitHub licence field empty; no `LICENSE` / `COPYING` in the tree). Use is for evaluation in this study only; **do not redistribute** TrackAny3D code or weights in the returned bundle. The same stance as MBPTrack3D (`gpu_jobs/mbptrack_first_test.md`).

The paper is open-access (ICCV 2025 / arXiv:2507.19908, arXiv non-exclusive distribution licence). Cite:

```
@InProceedings{Wang_2025_ICCV,
  author    = {Wang, Mengmeng and Wang, Haonan and Li, Yulong and Kong, Xiangjie and Du, Jiaxin and Shen, Guojiang and Xia, Feng},
  title     = {TrackAny3D: Transferring Pretrained 3D Models for Category-unified 3D Point Cloud Tracking},
  booktitle = {Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV)},
  month     = {October},
  year      = {2025},
  pages     = {28249-28259}
}
```

The constructor also loads the third-party RECON pretrained file `pretrained/base.pth` (paper §3.2). Evaluation use only; do not redistribute that file from the job.

## Pinned commit

- TrackAny3D: `https://github.com/sallymmx/TrackAny3D` at `2f01dc84f7611706cf912473f4b0be08127b9463` (20 Oct 2025; tip of `master`, no tags). This is the commit that sets `missing_threshold: 0.2` in `configs/trackany_kitti_all_cfg.yaml`. The authors stated (issue #1, 20 Oct 2025) that this threshold is required for the official checkpoint to match the paper. Do not change it. Both official configs already have `missing_threshold: 0.2` at this commit.
- IC001 repo, branch `cpu-agent`: `gpu_jobs/dump_trackany3d.py` and `gpu_jobs/patch_nuscenes_maps.py`.
- Pre-registration hash: `e31629c99566bd989094d3a3922374863f0ac163`.

Check out exactly that TrackAny3D commit. Do not train, do not substitute weights, do not change model code except the one-line load patch below.

## Required one-line patch (single-GPU load)

`models/TrackAny/RECON.py`, in `load_model_from_ckpt`, hardcodes:

```
ckpt = torch.load(bert_ckpt_path, map_location=torch.device('cuda:1'))
```

A single T4 has only `cuda:0`, so this line raises. Change **only** the `map_location` to `'cpu'` (the model is moved to the T4 later). Record the patch in `run_meta.txt`. Do not change any other source, and do not change `missing_threshold`, crop sizes, or configs except `data_root_dir` and `category_name` as specified below.

## Checkpoints (liveness checked 22 Nov 2026, 1-byte HTTP range; SHA-256 of full files)

Official Google Drive links from the TrackAny3D README (commit `08b5140` / still present at the pin). Headless download (same pattern as the MBPTrack jobs):

```bash
curl -L -o pretrained/<file> "https://drive.usercontent.google.com/download?id=<id>&export=download&confirm=t"
```

Check the size, then `sha256sum`. Any mismatch or unreachable file → **stop and report**; never substitute weights. All three files are required: the model constructor always loads `pretrained/base.pth` (hardcoded path, relative to the TrackAny3D repo root); `kitti.ckpt` / `nuscenes.ckpt` are then loaded with `strict=False` and may omit frozen backbone tensors already filled from `base.pth`.

| File (place in `pretrained/`) | Drive id | Size (B) | SHA-256 (22 Nov 2026) | 1-byte range, 22 Nov 2026 |
|---|---|---|---|---|
| `base.pth` (filename on Drive: `base.pth`) | `1zEc9w5AdeiW55yWVUC4zuEQ2tu0xtJfA` | 613,675,406 | `a7f4bbc0c935638cd46cdd52c0e741dca075689848c5ff3f6df8419d0115df27` | HTTP 206, `bytes 0-0/613675406`, `filename="base.pth"` |
| `kitti.ckpt` | `1xTwugKP1Iq-wZdmDEdxs5siwHbsCfawI` | 146,564,437 | `547e97049b00b9a9132ec95f326b9011fc3179b7a049de545e6901e1a51008dd` | HTTP 206, `bytes 0-0/146564437`, `filename="kitti.ckpt"` |
| `nuscenes.ckpt` | `1LTJGjlZR-yOhHV_BHr7TaDIN5j1mgC0k` | 146,564,629 | `19e4c070b085f6902979247211c25c3a8dfa92073e01f878e5fd4017143cab1c` | HTTP 206, `bytes 0-0/146564629`, `filename="nuscenes.ckpt"` |

README documented Success / Precision (dataset **Mean**, frame-weighted), same numbers as paper Tables 1–2 Mean column: KITTI **67.1 / 85.4** (`kitti.ckpt`); nuScenes **54.57 / 66.25** (`nuscenes.ckpt`). There is **no** separate documented Car checkpoint value. Per-class paper values are in the V1 section below.

## Environment (T4, sm_75)

Reuse the MBPTrack Plan A pins (`mbptrack_first_test.md`): Python 3.8, torch 1.8.0+cu111, torchvision 0.9.0, pytorch-lightning 1.5.10, pytorch3d 0.6.2, shapely 1.8.1, plus the TrackAny3D README extras `open3d==0.15.2` and `timm` (`DropPath` / `trunc_normal_` in `RECON.py`). Also: addict, pyyaml, pandas, pyquaternion, tqdm, pynvml, nuscenes-devkit.

```bash
# Plan A outline (see mbptrack_first_test.md for micromamba / nvcc notes)
pip install torch==1.8.0+cu111 torchvision==0.9.0+cu111 -f https://download.pytorch.org/whl/torch_stable.html
pip install pytorch-lightning==1.5.10 addict pyyaml pandas pyquaternion shapely==1.8.1 tqdm pynvml nuscenes-devkit open3d==0.15.2 timm
pip install "git+https://github.com/facebookresearch/pytorch3d.git@v0.6.2"
# pointnet2_ops (TrackAny3D imports pointnet2_ops._ext)
TORCH_CUDA_ARCH_LIST="7.5" pip install "git+https://github.com/erikwijmans/Pointnet2_PyTorch.git#egg=pointnet2_ops&subdirectory=pointnet2_ops_lib"
```

**Plan B** only if Plan A fails after ≤ 2 h: the host torch + pytorch3d / `pointnet2_ops` built from source; list every deviation. V1 decides whether Plan B numbers are usable. Internet ON for git/pip/Drive. Persistence off. No paid compute.

## Data

### KITTI — private dataset `ic001-kitti-0019-0020`

Reuse the existing private dataset if its manifest still matches. Verify first:

```bash
cd /kaggle/input/ic001-kitti-0019-0020/kitti && sha256sum -c kitti_sha256.txt --quiet
```

Any mismatch → stop. The loader wants `velodyne/`, `label_02/`, `calib/` directly under `data_root_dir`. Official test split is scenes 19–20 (`KITTIMem` `test=list(range(19, 21))`), matching frozen PREREG.

### nuScenes — re-upload private `ic001-nuscenes-val-keyframes`, delete after a verified run

nuScenes terms say no redistribution. Create a **private** dataset (no collaborators, never public) from the box folder `/workspace/ic001/data/nuscenes/` plus the manifests in this repo, same slim val-keyframes bundle as `gpu_jobs/nuscenes_learned.md`:

| Path (relative to dataset root) | What | Size |
|---|---|---|
| `samples/LIDAR_TOP/*.pcd.bin` | 6,019 val LIDAR_TOP keyframes | 4,179,568,000 B |
| `v1.0-trainval/*.json` | slim **val-only** tables (150 val scenes; see `DATA.md`) | 155,517,152 B |
| `nuscenes_val_lidar_sha256.txt` | SHA-256 of every LIDAR file (copy from `data_manifest/`) | — |
| `nuscenes_valonly_json_sha256.txt` | SHA-256 of the slim JSON tables (copy from `data_manifest/`) | — |

**Payload size:** 4,335,085,152 B ≈ **4.04 GiB** of data, plus a few hundred KB of manifests. No sweeps, no cameras, no full trainval JSON, no `.tgz`.

On the kernel, first verify (paths in both manifests are relative to this root):

```bash
cd /kaggle/input/ic001-nuscenes-val-keyframes
sha256sum -c nuscenes_val_lidar_sha256.txt --quiet
sha256sum -c nuscenes_valonly_json_sha256.txt --quiet
find samples/LIDAR_TOP -name '*.pcd.bin' | wc -l   # expect 6019
```

Any mismatch → stop and report.

The official `NuScenes()` constructor expects a `maps/` tree. The slim bundle has none. Use the same writable dataroot as the previous nuScenes learned job: symlink `samples/` and every `v1.0-trainval/*.json` except `map.json`, which is replaced by `[]`. Point `data_root_dir` at this dataroot (e.g. `/kaggle/working/nuscenes_root`). Do not modify the input dataset. Apply `gpu_jobs/patch_nuscenes_maps.py` **in-process** before any `NuScenes()` construct (official test and dump), e.g. a `sitecustomize.py` on `PYTHONPATH` that calls `patch_nuscenes_maps.apply()`. Record that the patch ran.

**Delete after a verified run.** A run is verified when: process rc=0; checkpoint SHA-256s match this spec; KITTI Car V1 is recorded against the table below; headline Car dumps exist with the expected row counts; frame-count and frame-0 self-checks are reported (not silently "fixed"). Then **delete the private nuScenes Kaggle dataset**. Do not delete the box copy, the KITTI private dataset, or anything on the box. If the run is not verified, keep the dataset and report; do not delete it.

## Per-frame dump format (must match previous dumps)

```
dataset,category,tracklet_id,frame_idx,protocol,method,cx,cy,cz,w,l,h,yaw
```

- `dataset` ∈ {`kitti`, `nuscenes`}. `category` is the official loader name (`Car`, `Pedestrian`, `Van`, `Cyclist` on KITTI; `Car`, `Pedestrian`, `Truck`, `Trailer`, `Bus` on nuScenes).
- `tracklet_id`: KITTI `"%04d_%d" % (scene, track_id)`; nuScenes `instance_token`. `frame_idx` 0-based in the same order as `ic001` indexers (`index_kitti` test scenes 19–20; `index_nuscenes` val, keyframes only, `min_points=1` on the first box).
- Boxes in the Open3DSOT / IC001 scoring frame: **KITTI velodyne** of that frame; **nuScenes global**. `yaw` = rotation about +z of the box length axis. Frame 0 = the given GT box.
- `protocol` ∈ {`ope`, `reinit`}. `method` = `trackany3d`.
- `ope`: frame-1 GT only. `reinit`: at every t ≥ 1 the tracker restarts from GT_{t−1} (box incl. size; memory reset from the GT box, i.e. a 2-frame tracklet [t−1, t]; PREREG choice j).

`dump_trackany3d.py` writes this schema. Official configs use `category_name: All`; the harness overrides `dataset_cfg.category_name` and `data_root_dir` from the command line so each class is dumped separately with the same unified checkpoint. Self-checks: KITTI camera→velodyne frame-0 error < 1e-4 m / 1e-4 rad; nuScenes frame-0 centres/yaw vs `index_nuscenes` and per-tracklet frame counts. Do not "fix" a failing self-check silently.

## Steps

T4 x1, Internet ON, Persistence off. Add the private KITTI dataset; add the private nuScenes dataset only for the nuScenes kernel. Work from the TrackAny3D repo root after the pin checkout, the one-line `map_location` patch, and the three checksummed files in `pretrained/`.

Official configs (do not swap in deleted per-class yamls):

| Dataset | Config | Checkpoint | Classes (run Car first) |
|---|---|---|---|
| KITTI | `configs/trackany_kitti_all_cfg.yaml` | `pretrained/kitti.ckpt` | Car, Pedestrian, Van, Cyclist |
| nuScenes | `configs/trackany_nuscenes_kitti_all_cfg.yaml` | `pretrained/nuscenes.ckpt` | Car, Pedestrian, Truck, Trailer, Bus |

Keep `missing_threshold: 0.2`, `coordinate_mode` (KITTI `camera`, nuScenes as in the yaml), `up_axis`, `eval_cfg.iou_space: 3`, `test_version: v1.0-trainval`. Only edit `dataset_cfg.data_root_dir` and, for a single-class run, `dataset_cfg.category_name`.

### A. Official test (V1 / informational)

```bash
# KITTI Car (V1 gate). Set data_root_dir and category_name: Car, then:
python main.py configs/trackany_kitti_all_cfg.yaml --phase test --resume_from pretrained/kitti.ckpt --gpus 0
# nuScenes Car (informational V1). Set data_root_dir to the patched slim root and category_name: Car:
python main.py configs/trackany_nuscenes_kitti_all_cfg.yaml --phase test --resume_from pretrained/nuscenes.ckpt --gpus 0
```

`main.py` always uses split type `test`. For nuScenes the loader maps a non-train split to the official **val** scene list, `key_frame_only=True`, `min_points=1` on the first box — the frozen PREREG protocol. Record Success/Precision from the official log (`Avg Prec/Succ=...` on KITTI; `Key: Prec=... Succ=...` on nuScenes).

An optional `category_name: All` run would check the README Mean (KITTI 67.1, nuScenes 54.57). It is **not** required: official `main.py` prints only a running Mean on All, not per-class scores, and a full nuScenes All pass is expensive. Prefer the Car V1 command above. If an All pass is run, record it as a sanity check only.

### B. Per-frame dump

```bash
python /kaggle/working/ic001/gpu_jobs/dump_trackany3d.py configs/trackany_kitti_all_cfg.yaml \
    --ckpt pretrained/kitti.ckpt --data-root /kaggle/input/ic001-kitti-0019-0020/kitti \
    --category <Car|Pedestrian|Van|Cyclist> --protocols ope reinit \
    --out /kaggle/working/outputs/trackany3d_kitti_<cls>.csv

python /kaggle/working/ic001/gpu_jobs/dump_trackany3d.py configs/trackany_nuscenes_kitti_all_cfg.yaml \
    --ckpt pretrained/nuscenes.ckpt --data-root /kaggle/working/nuscenes_root \
    --category <Car|Pedestrian|Truck|Trailer|Bus> --protocols ope reinit \
    --out /kaggle/working/outputs/trackany3d_nuscenes_<cls>.csv
```

Checks: printed `ope` Success equals the official step-A number for that class (±0.01); self-checks as above. Either failing → report, do not "fix" silently. `PYTHONPATH` must include the IC001 repo root so nuScenes frame-count checks can import `ic001.data.nuscenes.index_nuscenes`.

## V1 references (`PREREG_ADDENDUM_2026-11-21.md`)

Protocol (a) / official `ope`. **Pass** if reproduced Success is within **1.0** of either the paper value or a documented official-checkpoint value, when one exists. **Fail** if it is more than 1.0 from both (or from the paper value alone, if no documented class-specific checkpoint value exists). Then stop and report; no tuning, no re-runs with other seeds or settings.

The official README documents only the dataset Mean, not a Car-specific checkpoint Success, so the Car check uses the paper Table value only.

| Split / class | Paper Success / Precision | Paper source | Documented checkpoint Success / Precision | Role |
|---|---|---|---|---|
| KITTI Car [6,424 frames] | **73.4** / 85.2 | Wang et al., ICCV 2025, arXiv:2507.19908v1, Table 1 (category-unified TrackAny3D row) | none as a class-specific number (README Mean 67.1 / 85.4 for `kitti.ckpt`) | **V1** (KITTI Car) |
| nuScenes Car [64,159 frames] | **59.30** / 66.46 | same paper, Table 2 | none as a class-specific number (README Mean 54.57 / 66.25 for `nuscenes.ckpt`) | Informational |
| KITTI Pedestrian / Van / Cyclist | 59.6 / 85.6 ; 70.0 / 82.8 ; 74.7 / 94.0 | Table 1 | — | Informational |
| nuScenes Pedestrian / Truck / Trailer / Bus | 40.37 / 68.70 ; 62.70 / 62.80 ; 66.12 / 59.20 ; 61.01 / 58.02 | Table 2 | — | Informational |

If KITTI Car fails V1: stop, report, return logs only. Do not start or continue nuScenes dumps until that is resolved.

## Expected row counts (both protocols)

Checked against paper Tables 1–2 frame counts and the frozen IC001 indexers (KITTI: binned frames + tracklets = total including frame 0).

| File | Tracklets / frames (ope) | Rows (ope+reinit) |
|---|---|---|
| `trackany3d_kitti_car.csv` | 120 / 6,424 | **12,848** |
| `trackany3d_kitti_pedestrian.csv` | 62 / 6,088 | 12,176 |
| `trackany3d_kitti_van.csv` | 16 / 1,248 | 2,496 |
| `trackany3d_kitti_cyclist.csv` | 8 / 308 | 616 |
| `trackany3d_nuscenes_car.csv` | 3,660 / 64,159 | **128,318** |
| `trackany3d_nuscenes_pedestrian.csv` | 1,858 / 33,227 | 66,454 |
| `trackany3d_nuscenes_truck.csv` | 608 / 13,587 | 27,174 |
| `trackany3d_nuscenes_trailer.csv` | 152 / 3,352 | 6,704 |
| `trackany3d_nuscenes_bus.csv` | 120 / 2,953 | 5,906 |

## Output layout (small files only)

Return a folder (e.g. `/kaggle/working/outputs/`) containing:

- `trackany3d_kitti_{car,pedestrian,van,cyclist}.csv` and `trackany3d_nuscenes_{car,pedestrian,truck,trailer,bus}.csv` as completed
- official test logs and harness printouts under `logs/`
- `run_meta.txt` (tracker commit, IC001 commit, rc, wall time, GPU name, paid=0, Plan A/B, the RECON `map_location` patch, map-table patch, env deviations)
- `checkpoint_sha256.txt`, `SHA256SUMS_outputs.txt`, `pip freeze` / `conda list`, `nvidia-smi`
- self-check lines (frame-0 errors, nuScenes frame-count missing/mismatch counts)

Never return point clouds, features, checkpoints, or dataset files.

## Expected runtime (estimate)

Paper: 28 FPS on a 3090, 5.30 M trainable parameters, frozen RECON PointTransformer (dim 384, depth 12). A T4 is roughly 3–4× slower in FP32, so about **7–10 FPS**. Inference frames: KITTI all classes, both dump protocols, 28,136; nuScenes all classes, both protocols, 234,556; plus official V1 ope on the two Car splits, 70,583. At 8 FPS that is about **11–12 h** of inference, plus 0.5–1.5 h Plan A setup — tight for one 12 h session.

Use **two free T4 sessions** (a third only if nuScenes non-Car classes remain):

1. Env + KITTI (V1 Car, then dumps of all four classes): **≈ 1.5–3 T4-h**.
2. nuScenes Car first (informational V1 + dump, **≈ 3–5 T4-h**), then the other four classes (**≈ 3–5 T4-h**). If time will run out, finish Car and return those CSVs; continue the remaining classes in another free kernel.

Combined **≈ 8–14 T4-h**. Fits a free week if the env is reused. **No paid compute.** If a 16 GB OOM occurs, only lower `eval_cfg.num_workers`; do not change the model or the crop.

## Risks

- The `cuda:1` load line will abort a single-T4 run unless the documented one-line patch is applied.
- Slim nuScenes needs the empty-`map.json` dataroot plus `patch_nuscenes_maps.py`; unpatched loads fail in `NuScenes()`.
- Google Drive must remain reachable; if a file cannot be downloaded with the size/hash above, stop (do not train, do not substitute).
- GitHub issue #1 reported Mean scores well below the paper until `missing_threshold` was set to 0.2; the pin already includes that config. Do not retune it.
- Plan B (host torch) may miss V1; prefer Plan A.
- nuScenes wall time may exceed one 12 h session; split as above and prioritise Car.
