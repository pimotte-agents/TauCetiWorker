#!/usr/bin/env python3
"""A pinned --roadmap-only area selects only PRs known to belong to it: unknown areas are excluded."""

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tauceti_tools import survey_facts as shared

from tauceti_worker import survey_facts


def main():
    fails = 0

    def check(message, actual, expected):
        nonlocal fails
        ok = actual == expected
        print(f"[{'OK ' if ok else 'XX '}] {message}: {actual!r} (want {expected!r})")
        fails += not ok

    in_scope = survey_facts.in_scope
    check(
        "roadmap/Unknown is excluded from a pinned area", in_scope(["roadmap/Unknown"], (), "roadmap/x", "PDE"), False
    )
    check(
        "an unlabeled roadmap/ branch without a target is excluded from a pinned area",
        in_scope([], (), "roadmap/work", "PDE"),
        False,
    )
    check("the pinned area itself is selected", in_scope(["roadmap/PDE"], (), "roadmap/x", "PDE"), True)
    check(
        "a known area label outranks roadmap/Unknown",
        in_scope(["roadmap/PDE", "roadmap/Unknown"], (), "roadmap/x", "PDE"),
        True,
    )
    check("a target marker places an unlabeled roadmap/ branch", in_scope([], ("PDE",), "roadmap/work", "PDE"), True)
    check("another area stays excluded", in_scope(["roadmap/Topology"], (), "roadmap/x", "PDE"), False)
    check("non-roadmap maintenance PRs stay in the shared pool", in_scope([], (), "feature", "PDE"), True)
    check("roadmap/none stays in the shared pool", in_scope(["roadmap/none"], (), "feature", "PDE"), True)
    for scope in ("", "any", "auto"):
        check(f"unpinned scope {scope!r} keeps roadmap/Unknown", in_scope(["roadmap/Unknown"], (), "", scope), True)
    check(
        "skip does not admit unknown areas under a pinned area",
        in_scope(["roadmap/Unknown"], (), "", "PDE", ["Topology"]),
        False,
    )
    check("the shared reduction is unchanged", shared.in_scope(["roadmap/Unknown"], (), "", "PDE"), True)

    # Every worker selection path must use the strict variant, not the shared reduction.
    survey = importlib.import_module("tauceti_worker.survey")
    check("survey selection uses the strict scope", survey.in_scope is in_scope, True)
    source = Path(importlib.import_module("tauceti_worker.source_survey").__file__).read_text()
    check(
        "source survey imports the strict scope",
        source.count("from .survey_facts import in_scope") >= 2
        and "tauceti_tools.survey_facts import in_scope" not in source,
        True,
    )

    print(f"\n{'PASS' if not fails else 'FAIL'}: {fails} assertion failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
