#!/usr/bin/env bash
# Stream nuScenes v1.0-trainval meta + keyframe archives through tar, keeping ONLY
# v1.0-trainval/*.json and val-split keyframe samples/LIDAR_TOP files. No .tgz is
# stored. md5 of each full stream via tee, checked against the official md5.checksum.
# Resumable per archive (done markers). Aborts if free disk would drop below 8 GB.
# Usage: scripts/stream_nuscenes.sh   (logs: /workspace/ic001/logs/nuscenes)
set -uo pipefail
BASE=https://d36yt3mvayqw5m.cloudfront.net/public/v1.0
ROOT=/workspace/ic001/data/nuscenes
LOG=/workspace/ic001/logs/nuscenes
MIN_FREE_KB=$((8*1024*1024))
PY=/workspace/ic001_venv/bin/python
mkdir -p "$ROOT" "$LOG"
cd "$LOG"
[ -s md5.checksum ] || curl -sS --retry 5 -o md5.checksum "$BASE/md5.checksum"

free_kb() { df -k --output=avail /workspace | tail -1 | tr -d ' '; }
watchdog() {  # kill the pipeline if free disk drops below the floor
  while sleep 5; do
    if [ "$(free_kb)" -lt "$MIN_FREE_KB" ]; then
      echo "ABORT: free disk below 8 GB" | tee -a "$LOG/ABORT"; pkill -P $$ curl; pkill -P $$ tar; exit 1
    fi
  done
}

stream() {  # $1 archive name, $2 tar member-list file (or "--meta")
  local name=$1 sel=$2
  [ -f "$LOG/$name.done" ] && { echo "skip $name (done)"; return 0; }
  [ "$(free_kb)" -lt $((MIN_FREE_KB + 1024*1024)) ] && { echo "ABORT before $name: disk"; exit 1; }
  echo "$(date -Is) start $name"
  local targs
  if [ "$sel" = "--meta" ]; then targs=(--wildcards 'v1.0-trainval/*.json'); else targs=(-T "$sel"); fi
  curl -sS -f --retry 5 --retry-delay 10 "$BASE/$name" \
    | tee >(md5sum | cut -d' ' -f1 > "$LOG/$name.md5") >(sha256sum | cut -d' ' -f1 > "$LOG/$name.sha256") \
          >(gzip -t 2> "$LOG/$name.gzip.err"; echo $? > "$LOG/$name.gzip.rc") \
    | { tar -xz -C "$ROOT" "${targs[@]}" 2> "$LOG/$name.tar.err"; t=$?; cat > /dev/null; exit $t; }
  local rc=("${PIPESTATUS[@]}")  # drain after tar so tee/md5 see the full stream
  sleep 5  # let the md5/sha256/gzip process substitutions finish
  local want got; want=$(grep " $name\$" md5.checksum | cut -d' ' -f1); got=$(cat "$LOG/$name.md5")
  echo "$(date -Is) $name curl=${rc[0]} tar=${rc[2]} md5 got=$got want=$want"
  # Integrity: full-stream gzip CRC must pass. The official md5.checksum (Jan 2024) does
  # not match the current CDN meta archive (gzip CRC OK, table counts = published stats),
  # so an md5 mismatch is recorded and reported, not fatal.
  if [ "${rc[0]}" != 0 ] || [ "$(cat "$LOG/$name.gzip.rc")" != 0 ]; then echo "FAIL $name (curl or gzip CRC)"; return 1; fi
  [ "$got" != "$want" ] && echo "$name got=$got want=$want" >> "$LOG/MD5_MISMATCH"
  # tar exit 2 with only 'Not found in archive' lines is expected for member lists
  if [ "${rc[2]}" != 0 ] && grep -v -e "Not found in archive" -e "Exiting with failure status" "$LOG/$name.tar.err" | grep -q .; then
    echo "FAIL $name tar"; return 1; fi
  touch "$LOG/$name.done"
}

watchdog & WD=$!
trap 'kill $WD 2>/dev/null' EXIT
stream v1.0-trainval_meta.tgz --meta || exit 1
# val keyframe LIDAR_TOP file list from the metadata
[ -s "$LOG/val_lidar_keyframes.txt" ] || $PY - "$ROOT" "$LOG/val_lidar_keyframes.txt" <<'PYEOF' || exit 1
import json, sys, os
sys.path.insert(0, "/workspace/ic001_launch")
from ic001.data.nuscenes import val_scenes
root, out = sys.argv[1:]
J = lambda n: json.load(open(os.path.join(root, "v1.0-trainval", n + ".json")))
scenes = {s["token"] for s in J("scene") if s["name"] in set(val_scenes())}
samples = {s["token"] for s in J("sample") if s["scene_token"] in scenes}
files = sorted(sd["filename"] for sd in J("sample_data")
               if sd["is_key_frame"] and sd["sample_token"] in samples and sd["filename"].startswith("samples/LIDAR_TOP/"))
open(out, "w").write("\n".join(files) + "\n")
print("val scenes", len(scenes), "val samples", len(samples), "val LIDAR_TOP keyframes", len(files))
PYEOF
for i in 01 02 03 04 05 06 07 08 09 10; do
  stream "v1.0-trainval${i}_keyframes.tgz" "$LOG/val_lidar_keyframes.txt" || exit 1
  echo "have $(find "$ROOT/samples/LIDAR_TOP" -type f 2>/dev/null | wc -l) LIDAR_TOP files, free $(( $(free_kb)/1024/1024 )) GB"
done
echo "$(date -Is) ALL DONE"
