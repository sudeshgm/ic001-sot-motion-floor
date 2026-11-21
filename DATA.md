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
- Source: official nuScenes CDN `https://d36yt3mvayqw5m.cloudfront.net/public/v1.0/` (same files as the nuscenes.org download page), streamed through tar; no .tgz stored (`scripts/stream_nuscenes.sh`, logs in `/workspace/ic001/logs/nuscenes/`).
- **Done (21 Nov 2026):** `v1.0-trainval_meta.tgz` (461,678,030 B) → only `v1.0-trainval/*.json` kept (13 tables, 2.5 GB; maps not extracted). Tables: 850 scenes, 34,149 samples, 1,166,187 annotations, 64,386 instances (= published stats). SHA-256 of each table: `data_manifest/nuscenes_trainval_meta_json_sha256.txt`.
  - Integrity: full-stream gzip CRC OK; stream md5 `537d3954ec34e5bcb89a35d4f6fb0d4a` (reproduced on 3 independent streams), sha256 `db48746b10e3544d5ef619eaa3d687e3960626fe1b4422ed856711da5aa7325b`. **This does NOT match the official `md5.checksum` entry (`3eee698806fcf52330faa2e682b9f3a1`, file dated 30 Jan 2024)**; recorded as an open integrity note.
- Val keyframe LIDAR_TOP list (150 val scenes, 6,019 samples, 6,019 files): `data_manifest/nuscenes_val_lidar_keyframes.txt`.
- **Not done: keyframe archives (`v1.0-trainval{01..10}_keyframes.tgz`, 44,902,690,772 B total).** Stopped before extracting anything because free disk (11 GB) minus the ~4.2 GB of val LIDAR_TOP would fall below the 8 GB floor.
