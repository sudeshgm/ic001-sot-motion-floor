"""Deterministic SOT-M2 Stage 1 training-scene choice.

Rank = position in ``numpy.random.default_rng(seed).permutation`` of the sorted nuScenes ``train_track``
scene names (seed 0). The training subset is the first ``n_target`` ranked scenes that are complete in the
streamed archive; fewer than ``n_min`` complete scenes is a stop condition, never a silent shrink.

    python -m gpu_jobs.sotm2.select_scenes rank  data_manifest/nuscenes_train_track_scenes.txt OUT
    python -m gpu_jobs.sotm2.select_scenes pick  RANK_FILE COMPLETE_FILE OUT
"""
import sys
import numpy as np

SEED = 0
N_TARGET = 40
N_MIN = 30


def rank(names, seed=SEED):
    names = sorted(set(names))
    perm = np.random.default_rng(seed).permutation(len(names))
    return [names[i] for i in perm]


def pick(ranked, complete, n_target=N_TARGET, n_min=N_MIN):
    complete = set(complete)
    chosen = [s for s in ranked if s in complete][:n_target]
    if len(chosen) < n_min:
        raise SystemExit(f"STOP: only {len(chosen)} complete train_track scenes (< {n_min})")
    return chosen


def _read(path):
    return [l.strip() for l in open(path) if l.strip() and not l.startswith("#")]


def main(argv):
    mode = argv[0]
    if mode == "rank":
        r = rank(_read(argv[1]))
        open(argv[2], "w").write(f"# rank order, numpy default_rng({SEED}).permutation of sorted train_track\n" + "\n".join(r) + "\n")
    elif mode == "pick":
        c = pick(_read(argv[1]), _read(argv[2]))
        open(argv[3], "w").write("\n".join(c) + "\n")
        print(len(c), "scenes")
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
