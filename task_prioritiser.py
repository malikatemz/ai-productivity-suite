"""Rank tasks by urgency and impact.

Usage:
    python task_prioritiser.py --tasks "Fix bug, Write docs, Deploy"
    python task_prioritiser.py --file tasks.txt
    python task_prioritiser.py --file tasks.txt --offline
"""

from __future__ import annotations

import argparse
from pathlib import Path

from common import llm_available
from logic import prioritise_tasks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--tasks", help="Comma-separated task list")
    source.add_argument("--file", help="File with one task per line")
    parser.add_argument("--offline", action="store_true", help="Force the deterministic fallback")
    parser.add_argument("--model", help="Override the provider model")
    args = parser.parse_args(argv)

    try:
        tasks = Path(args.file).read_text() if args.file else args.tasks
    except OSError as exc:
        parser.error(str(exc))
        return 2

    use_llm = not args.offline and llm_available()
    print(prioritise_tasks(tasks, use_llm=use_llm, model=args.model))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
