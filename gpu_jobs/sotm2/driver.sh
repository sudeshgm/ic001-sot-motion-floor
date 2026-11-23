#!/bin/bash
# SOT-M2 Stage 1 chunk driver (free Kaggle T4, private kernel + private datasets, paid=0).
# Order: verify inputs -> env -> G1 probe -> round-robin training blocks (C, I, D; then A_ft if time) -> eval -> decide.
# Hard self-stop: CAP seconds of wall time (default 6900 s = 1.92 h < 2 T4-h). Checkpoints after every block;
# a later chunk resumes from STATE (directory holding *_last.pt from the previous chunk's outputs/models).
# rc in run_meta.txt: 0 complete | 5 partial (budget not reached; resume) | 20 inputs sha | 21 bundle sha | 22 env
#                     | 23 G1 probe mismatch | 24 G2 reference mismatch | 25 training failure | 26 eval/rows failure
CAP=${CAP:-6900}; EVAL_RESERVE=${EVAL_RESERVE:-2400}; STEPS=${STEPS:-2000}; BLOCK=${BLOCK:-500}; BATCH=${BATCH:-100}
WORKERS=${WORKERS:-4}; STATE=${STATE:-}
W=/kaggle/working/out; S=/tmp/sotm2s1; mkdir -p "$W/logs" "$W/models" "$S"
T0=$(date +%s); META_RC=partial
el() { echo $(( $(date +%s) - T0 )); }
exec > >(tee -a "$W/driver_log.txt") 2>&1
write_meta() {
  local gpu; gpu=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1); [ -n "$gpu" ] || gpu=na
  { echo "rc=$META_RC"; echo "wall_s=$(el)"; echo "paid=0"; echo "gpu=$gpu"; echo "cap_s=$CAP steps=$STEPS block=$BLOCK batch=$BATCH"
    echo "finished_at=$(date -u +%FT%TZ)"; [ -f "$W/status.txt" ] && cat "$W/status.txt"; } > "$W/run_meta.txt"
  ( cd "$W" && find . -type f ! -name run_meta.txt ! -name driver_log.txt ! -name SHA256SUMS_outputs.txt | sort | xargs -r sha256sum > SHA256SUMS_outputs.txt ) 2>/dev/null
}
trap 'write_meta' EXIT
fatal() { META_RC=$1; echo "FATAL($1): $2" | tee -a "$W/status.txt"; exit 0; }
st() { echo "$*" | tee -a "$W/status.txt"; }
left() { echo $(( CAP - $(el) )); }
echo "start $(date -u +%FT%TZ)"; nvidia-smi | head -15
IN=""; BUNDLE=""
for i in $(seq 1 30); do
  [ -z "$IN" ] && f=$(find -L /kaggle/input -maxdepth 4 -name SOTM2S1_SHA256SUMS.txt -print -quit 2>/dev/null) && [ -n "$f" ] && IN=$(dirname "$f")
  [ -z "$BUNDLE" ] && f=$(find -L /kaggle/input -maxdepth 6 -name BUNDLE_SHA256SUMS.txt -print -quit 2>/dev/null) && [ -n "$f" ] && BUNDLE=$(dirname "$f")
  [ -n "$IN" ] && [ -n "$BUNDLE" ] && break; echo "waiting for mounts ($i)"; sleep 10
done
[ -n "$IN" ] || fatal 20 "inputs dataset missing"; [ -n "$BUNDLE" ] || fatal 21 "bundle missing"
( cd "$IN" && sha256sum -c SOTM2S1_SHA256SUMS.txt --quiet ) > "$W/logs/inputs_sha.txt" 2>&1 || fatal 20 "inputs sha mismatch"
st "inputs sha OK ($(el)s)"
( cd "$BUNDLE" && grep -E "ic001env.tgz.part|open3dsot_f08451d.tarball" BUNDLE_SHA256SUMS.txt | sha256sum -c --quiet ) > "$W/logs/bundle_sha.txt" 2>&1 || fatal 21 "bundle sha mismatch"
cat "$BUNDLE"/ic001env.tgz.part* | tar -xzf - -C / || fatal 22 "env unpack"
mkdir -p "$S/o3d" "$S/repo" && tar -xf "$BUNDLE/open3dsot_f08451d.tarball" -C "$S/o3d" || fatal 22 "untar Open3DSOT"
tar -xzf "$IN/code/ic001_sotm2_code.tgz" -C "$S/repo" || fatal 22 "untar code"
O3D=$(dirname "$(find "$S/o3d" -name main.py -print -quit)")
CK="$IN/ckpt/mmtrack_nuscenes_car.ckpt"
echo "3b19f52cc20c07f3f30cc0bf903c50f3bbd7039315785643b21a8a35332f0270  $CK" | sha256sum -c --quiet || fatal 22 "M2 ckpt sha"
PY=/opt/ic001env/bin/python; export PYTHONUNBUFFERED=1 CUDA_VISIBLE_DEVICES=0 PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=/opt/ic001env/ov_o3d:$S/repo
$PY -c "import torch;print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))" > "$W/env_check.txt" 2>&1 || fatal 22 "torch/cuda"
st "env OK ($(el)s)"
TE="$PY -m gpu_jobs.sotm2.train_eval"; COMMON=(--o3d "$O3D" --ckpt "$CK")
# G1: pretrained arms A,B on kill-test tracklets 12,13 reproduce the box-CPU reference
timeout 900 $TE eval "${COMMON[@]}" --data "$IN/eval" --out "$W/g1_probe" --arms A,B --tids 12,13 > "$W/logs/g1_probe.log" 2>&1 || fatal 23 "G1 probe run"
$PY - "$IN/eval/probe_ref_frames.csv" "$W/g1_probe/frames.csv" > "$W/logs/g1_cmp.txt" <<'PYEOF' || fatal 23 "G1 probe mismatch"
import csv, sys
ref = {(r["tid"], r["k"], r["arm"]): float(r["iou"]) for r in csv.DictReader(open(sys.argv[1]))}
got = {(r["tid"], r["k"], r["arm"]): float(r["iou"]) for r in csv.DictReader(open(sys.argv[2]))}
d = max(abs(got[k] - ref[k]) for k in got); print("rows", len(got), "max|dIoU|", d); sys.exit(0 if len(got) == 82 and d <= 1e-4 else 1)
PYEOF
st "G1 probe OK $(cat "$W/logs/g1_cmp.txt") ($(el)s)"
[ -n "$STATE" ] && cp -v "$STATE"/*_last.pt "$W/models/" 2>/dev/null
step_of() { [ -f "$W/models/$1_last.pt" ] && $PY -c "import torch;print(torch.load('$W/models/$1_last.pt',map_location='cpu')['step'])" || echo 0; }
BLK_EST=900; MAXDT=0  # before any block: 15 min guess; then slowest measured block + 60 s
train_block() {  # $1 arm -> one block; returns 1 if the budget does not allow it
  local a=$1 t1
  [ "$(step_of "$a")" -ge "$STEPS" ] && return 0
  [ $(( $(left) - EVAL_RESERVE )) -lt "$BLK_EST" ] && return 1
  t1=$(date +%s)
  $TE train "${COMMON[@]}" --data "$IN/train" --rollout "$IN/train/rollout" --out "$W/models" --arm "$a" --steps "$STEPS" \
      --block "$BLOCK" --batch "$BATCH" --workers "$WORKERS" --seed 0 --lr 1e-4 --one-block >> "$W/logs/train_$a.log" 2>&1 \
      || { [ "$WORKERS" != 0 ] && grep -q -i "segmentation\|DataLoader worker" "$W/logs/train_$a.log" && WORKERS=0 && st "workers->0 after loader crash" && return 0; fatal 25 "train $a"; }
  local dt=$(( $(date +%s) - t1 )); [ "$dt" -gt "$MAXDT" ] && MAXDT=$dt; BLK_EST=$(( MAXDT + 60 ))
  st "block $a step=$(step_of "$a") dt=${dt}s ($(el)s)"
}
done_arm() { [ "$(step_of "$1")" -ge "$STEPS" ]; }
while ! (done_arm C && done_arm I && done_arm D); do
  for a in C I D; do train_block "$a" || { META_RC=5; st "PARTIAL: cap reached before C/I/D budgets; resume in next chunk ($(el)s)"; exit 0; }; done
done
st "C, I, D budgets complete ($(el)s)"
while ! done_arm A_ft; do train_block A_ft || { st "A_ft skipped/partial for cap (reference only)"; break; }; done
ARMS=A,B,I,C,D; done_arm A_ft && ARMS=$ARMS,A_ft
timeout $(( $(left) - 120 )) $TE eval "${COMMON[@]}" --data "$IN/eval" --models "$W/models" --out "$W/eval" --arms "$ARMS" \
    > "$W/logs/eval.log" 2>&1 || { META_RC=5; st "PARTIAL: eval did not finish ($(el)s)"; exit 0; }
NA=$(echo "$ARMS" | tr ',' '\n' | wc -l); ROWS=$(( $(wc -l < "$W/eval/frames.csv") - 1 )); BROWS=$(( $(wc -l < "$W/eval/b_sweep_boxes.csv") - 1 ))
[ "$ROWS" -eq $(( 4674 * NA )) ] && [ "$BROWS" -eq 44693 ] || fatal 26 "row counts frames=$ROWS (want $((4674*NA))) b=$BROWS (want 44693)"
st "rows OK frames=$ROWS b_sweep=$BROWS ($(el)s)"
$PY -m gpu_jobs.sotm2.decide "$W/eval/frames.csv" "$IN/eval/bins.csv" "$W/decision.json" > "$W/logs/decide.log" 2>&1 || fatal 26 "decide"
$PY - "$W/decision.json" > "$W/logs/g2.txt" <<'PYEOF' || fatal 24 "G2: arm A differs from the kill-test reference"
import json, sys
r = json.load(open(sys.argv[1]))["per_arm"]; a = r["A"]["overall_o3d"]["success"]; b = r["B"]["overall_o3d"]["success"]
print("A", a, "B", b); sys.exit(0 if abs(a - 53.95) <= 0.1 and abs(b - 39.40) <= 0.1 else 1)
PYEOF
st "G2 OK $(cat "$W/logs/g2.txt"); verdict $($PY -c "import json;print(json.load(open('$W/decision.json'))['verdict'])") ($(el)s)"
META_RC=0
