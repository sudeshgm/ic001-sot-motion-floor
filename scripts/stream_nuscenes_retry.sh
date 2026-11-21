#!/usr/bin/env bash
# Re-run the resumable per-archive stream until all archives are done or 20 attempts fail.
# Stops for good on a disk-floor ABORT. Single-writer lock prevents duplicate streams.
LOG=/workspace/ic001/logs/nuscenes
exec 9>"$LOG/stream.lock"
flock -n 9 || { echo "another stream is running"; exit 1; }
for i in $(seq 1 20); do
  echo "=== attempt $i $(date -Is) free $(df -h --output=avail /workspace | tail -1)" >> "$LOG/stream.log"
  bash /workspace/ic001_launch/scripts/stream_nuscenes.sh >> "$LOG/stream.log" 2>&1 && { echo "ALL DONE $(date -Is)" >> "$LOG/stream.log"; touch "$LOG/ALL_DONE"; exit 0; }
  [ -f "$LOG/ABORT" ] && { echo "disk abort, stopping" >> "$LOG/stream.log"; exit 1; }
  sleep 60
done
echo "GAVE UP after 20 attempts $(date -Is)" >> "$LOG/stream.log"; touch "$LOG/GAVE_UP"; exit 1
