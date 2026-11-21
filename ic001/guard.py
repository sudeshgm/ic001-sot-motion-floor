"""Pre-registration guard: scoring real data is refused until a frozen,
approved pre-registration exists (PREP_STEPS C.2). The freeze is recorded by
committing PREREG*.md and writing its git hash to ``PREREG.githash``.
Synthetic data (tests) does not go through this guard."""
from __future__ import annotations

import os
import subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class PreregNotFrozen(RuntimeError):
    pass


def require_frozen_prereg(repo: str = REPO) -> str:
    p = os.path.join(repo, "PREREG.githash")
    if not os.path.isfile(p):
        raise PreregNotFrozen(
            "No PREREG.githash: the pre-registration is not frozen/approved. "
            "Real-data scoring is blocked (PREP_STEPS C.2).")
    h = open(p).read().strip()
    r = subprocess.run(["git", "-C", repo, "cat-file", "-e", h + "^{commit}"],
                       capture_output=True)
    if r.returncode != 0:
        raise PreregNotFrozen(f"PREREG.githash {h} is not a commit in this repo")
    return h
