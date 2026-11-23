"""Generate a time-blocked daily plan from a task list.

Usage:
    python daily_planner.py --tasks "Fix bug, Write tests, Review PR" --hours 6
    python daily_planner.py --file tasks.txt --hours 8 --start "9:00 AM"
    python daily_planner.py --file tasks.txt --offline
"""

from __future__ import annotations

import argparse
from pathlib import Path

from common import llm_available
from logic import plan_day


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--tasks", help="Comma-separated task list")
    source.add_argument("--file", help="File with one task per line")
    parser.add_argument("--hours", type=int, default=8, help="Available working hours")
    parser.add_argument("--start", default="9:00 AM", help="Start time, e.g. '9:00 AM' or '09:00'")
    parser.add_argument("--offline", action="store_true", help="Force the deterministic fallback")
    parser.add_argument("--model", help="Override the provider model")
    args = parser.parse_args(argv)

    try:
        tasks = Path(args.file).read_text() if args.file else args.tasks
    except OSError as exc:
        parser.error(str(exc))
        return 2

    use_llm = not args.offline and llm_available()
    try:
        print(plan_day(tasks, hours=args.hours, start_time=args.start, use_llm=use_llm, model=args.model))
    except ValueError as exc:
        parser.error(str(exc))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
