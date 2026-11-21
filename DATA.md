# Data used by IC001 (not in this repo)

Only checksum manifests live in the repo (`data_manifest/`). Data files are never committed.

## KITTI tracking (downloaded 21 Nov 2026 with Sudesh's approval)
- Source: official KITTI tracking zips on `https://s3.eu-central-1.amazonaws.com/avg-kitti/` (cvlibs.net download links).
  - `data_tracking_velodyne.zip` (36,829,852,418 B): only `training/velodyne/0019/` (1,059 scans) and `training/velodyne/0020/` (837 scans) fetched by HTTP byte range (`scripts/fetch_kitti_subset.py`); 1,896 files, 3,663,947,936 B; every file verified against the zip's CRC-32 and size (`data_manifest/kitti_velodyne_zip_entries_crc32.tsv`).
  - `data_tracking_label_2.zip` (2,259,128 B), `data_tracking_calib.zip` (89,829 B), `data_tracking_oxts.zip` (8,352,970 B): whole zips; `training/*` extracted.
- On the box: `/workspace/ic001/data/kitti/{velodyne,label_02,calib,oxts}` (+ zips in `/workspace/ic001/data/zips/`).
- SHA-256 of every file: `data_manifest/kitti_sha256.txt` (paths relative to `kitti/`), zips: `data_manifest/kitti_small_zips_sha256.txt`.
- **Licence:** KITTI is CC BY-NC-SA 3.0 (non-commercial, attribution, share-alike). Research use only. Any Kaggle copy must be a **private** dataset.

## nuScenes
- v1.0-trainval val keyframes (LIDAR_TOP) + metadata, under Sudesh's nuScenes account. Licence: CC BY-NC-SA 4.0 plus the nuScenes Terms of Use (non-commercial). Not redistributed; any Kaggle copy private only.
- Source: official nuScenes objects. After a slow CloudFront start, the completed stream used direct S3 `https://motional-nuscenes.s3.amazonaws.com/public/v1.0` (same public v1.0 files as the nuscenes.org download page), streamed through tar; no .tgz stored (`scripts/stream_nuscenes.sh`; `MIN_FREE_GB` is env-configurable, default 8; logs in `/workspace/ic001/logs/nuscenes/`).
- **Done (21 Nov 2026):** `v1.0-trainval_meta.tgz` (461,678,030 B) → only `v1.0-trainval/*.json` kept (13 tables, 2.5 GB; maps not extracted). Tables: 850 scenes, 34,149 samples, 1,166,187 annotations, 64,386 instances (= published stats). SHA-256 of each table: `data_manifest/nuscenes_trainval_meta_json_sha256.txt`.
  - Integrity: full-stream gzip CRC OK; stream md5 `537d3954ec34e5bcb89a35d4f6fb0d4a` (reproduced on 3 independent streams), sha256 `db48746b10e3544d5ef619eaa3d687e3960626fe1b4422ed856711da5aa7325b`. **This does NOT match the official `md5.checksum` entry (`3eee698806fcf52330faa2e682b9f3a1`, file dated 30 Jan 2024)**; recorded as an open integrity note.
- **Val-only slim metadata (21 Nov 2026, Sudesh option c):** `scripts/slim_nuscenes_meta.py` wrote val-only tables (val scene/sample/sample_annotation/instance, every keyframe sample_data of val samples, the referenced ego_pose rows, small tables unchanged; 149 MB). Checks against the originals:
  - Raw counts are identical (original == slim): 150 scenes, 6,019 samples, 6,019 LIDAR_TOP keyframes, 4,543 vehicle.car instances, 80,004 vehicle.car annotations (`results/nuscenes/valonly_raw_counts_*.json`).
  - Loader tracklets for all 7 classes are identical in count, frames, filenames and transforms. Car has 3,660 tracklets and 64,159 frames at min_points=1. Result: ALL_IDENTICAL true (`results/nuscenes/valonly_verification.json`).
  - SHA-256 of the slim tables: `data_manifest/nuscenes_valonly_json_sha256.txt`.
  - The original full JSONs were re-verified against their manifest and then deleted, freeing 2,601,893,888 B. Free space went from 10.8 GB to 13.4 GB. The slim tables now sit at `data/nuscenes/v1.0-trainval/`.
- Val keyframe LIDAR_TOP list (150 val scenes, 6,019 samples, 6,019 files): `data_manifest/nuscenes_val_lidar_keyframes.txt`.
- Keyframe archives: first attempt (21 Nov, before slimming) was stopped before extracting anything because free disk (11 GB) minus the ~4.2 GB of val LIDAR_TOP would have fallen below the 8 GB floor. Resumed 15:02 IST after slimming. **Completed 17:17 IST — see the note below.**

- **Val LIDAR_TOP keyframes complete (21 Nov 2026, 17:17 IST).** 6,019 `samples/LIDAR_TOP/*.pcd.bin` files on the box (every file's size is a multiple of 20 B; 4,179,568,000 B total). SHA-256 of every file: `data_manifest/nuscenes_val_lidar_sha256.txt` (paths relative to the nuScenes root, same order as `nuscenes_val_lidar_keyframes.txt`).
  - Archives 01–09 finished 15:13–15:40 IST (S3). Archive 10 was first blocked by the 8 GB free-disk floor (5,417/6,019 files on disk). It was rerun at 17:12 IST with the floor lowered to 6 GB per Idea Launcher (`MIN_FREE_GB=6`); finished 17:17 IST with 6,019 files and about 8 GB still free. Nothing was deleted.
  - Integrity: full-stream gzip CRC OK for all 10 keyframe archives and for the metadata archive. Every archive's stream md5 differs from the official `md5.checksum` (the same pattern already noted for the metadata archive). The Jan 2024 checksum file does not match the current S3 objects; gzip CRC is the integrity check used. Mismatches, from `/workspace/ic001/logs/nuscenes/MD5_MISMATCH`:

    | Archive | Stream md5 (got) | Official md5.checksum (want) |
    |---|---|---|
    | v1.0-trainval_meta.tgz | 537d3954ec34e5bcb89a35d4f6fb0d4a | 3eee698806fcf52330faa2e682b9f3a1 |
    | v1.0-trainval01_keyframes.tgz | 1441a2b3ada1ba2b7a67fa3d26f58a16 | 1912cc6604789a88f1efe964bb918db5 |
    | v1.0-trainval02_keyframes.tgz | 201fd9833e73c4d30451e98242fd2419 | 591bc531a6d7297cb126638f1325fc01 |
    | v1.0-trainval03_keyframes.tgz | 0d68ea18afbf4b4480863b8d58f7ea21 | 48a700b3639ce43b315af12f1a9a36fe |
    | v1.0-trainval04_keyframes.tgz | 055ab21b319816d4979ac039006f9b8f | a8eef0eceb4f0af77b7ba6ec39139825 |
    | v1.0-trainval05_keyframes.tgz | 6e08e65c3a39922d68f75f6c1af8ea39 | 53d3223a5f7b39ef1871e022b72b5bd0 |
    | v1.0-trainval06_keyframes.tgz | 89ac1ccac50b3befbe18b738c72c2b16 | fd8434734ed3ab57006d13ed80d571a1 |
    | v1.0-trainval07_keyframes.tgz | 1aa4ba3a79c00230f96861dac8431595 | 522cebe3bf4f44e4bb0e584dd059f36e |
    | v1.0-trainval08_keyframes.tgz | 6032f76a983fe1ac73c469c6b6410dfb | ed4390b45c211eba2e87447542cc8770 |
    | v1.0-trainval09_keyframes.tgz | efe35ac88df9630c77ced7c165728b9f | 7f024373109cdf41eb4ef127513a00f1 |
    | v1.0-trainval10_keyframes.tgz | b43ca3897c22537326f364369ced218d | 4731922b48f48939ce45ac621b3a8c8a |

  - `tar` exit 2 is expected and benign: the member list spans all 10 archives, so each archive reports 'Not found in archive' for files it does not hold.
