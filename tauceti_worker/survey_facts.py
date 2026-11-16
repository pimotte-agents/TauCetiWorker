"""Compatibility import for shared survey reductions owned by TauCetiTools.

`in_scope` is narrowed for worker selection: a pinned `--roadmap-only` area admits only PRs
known to belong to it. The shared reduction keeps PRs whose area is unknown (`roadmap/Unknown`,
or an unlabeled `roadmap/` branch with no target marker) in every scope so the labeler cannot
strand them; a worker told to stay in one area must not pick them up.
"""

from tauceti_tools.survey_facts import *  # noqa: F403
from tauceti_tools.survey_facts import in_scope as _shared_in_scope
from tauceti_tools.survey_facts import roadmap_focuses


def in_scope(labels, targets=(), branch="", roadmap="any", skip=()):
    if roadmap not in ("", "any", "auto") and roadmap_focuses(labels, targets, branch) is None:
        return False
    return _shared_in_scope(labels, targets, branch, roadmap, skip)
