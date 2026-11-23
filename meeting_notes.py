"""Summarise raw meeting notes into structured decisions, actions, and questions.

Usage:
    python meeting_notes.py --file notes.txt
    python meeting_notes.py --text "We agreed to ship on Friday..."
    python meeting_notes.py --file notes.txt --offline
"""

from __future__ import annotations

import argparse
from pathlib import Path

from common import llm_available
from logic import summarise_meeting


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--file", help="Path to a text file with meeting notes")
    source.add_argument("--text", help="Meeting notes as a single argument")
    parser.add_argument("--offline", action="store_true", help="Force the deterministic fallback")
    parser.add_argument("--model", help="Override the provider model")
    args = parser.parse_args(argv)

    try:
        content = Path(args.file).read_text() if args.file else args.text
    except OSError as exc:
        parser.error(str(exc))
        return 2

    use_llm = not args.offline and llm_available()
    print(summarise_meeting(content, use_llm=use_llm, model=args.model))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
