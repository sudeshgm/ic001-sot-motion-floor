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
- v1.0-trainval val keyframes (LIDAR_TOP) + metadata, under Sudesh's nuScenes account. Licence: CC BY-NC-SA 4.0 plus the nuScenes Terms of Use (non-commercial). Not redistributed; any Kaggle copy private only. Status recorded below when done.
