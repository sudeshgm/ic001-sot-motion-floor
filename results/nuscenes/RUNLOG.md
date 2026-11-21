# nuScenes RUNLOG (frozen PREREG e31629c)

- 2026-11-21 14:42–15:01 IST: val-only slim metadata built and verified (ALL_IDENTICAL). Originals deleted (2.60 GB freed). See DATA.md.
- 2026-11-21 15:02 IST: `nohup scripts/stream_nuscenes.sh` resumed (logs: /workspace/ic001/logs/nuscenes). 10 keyframe archives, 44.9 GB in total.
  The measured CDN throughput is about 0.8 MB/s per connection, while the same box gets 6.2 MB/s from another host. At that rate the ETA is about 15 h.
