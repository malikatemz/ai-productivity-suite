# AI Productivity Suite

Three focused AI productivity tools in one repository: meeting-note summarisation, task prioritisation, and time-blocked daily planning.

![Status](https://img.shields.io/badge/status-complete-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)

## Tools

| Tool | What it does |
|---|---|
| `meeting_notes.py` | Turns raw notes into a summary, decisions, action items, and open questions |
| `task_prioritiser.py` | Scores tasks on urgency and impact and returns a ranked Markdown table |
| `daily_planner.py` | Builds a realistic time-blocked day with breaks, a review block, and deferred items |

## Offline-first design

Every tool works without an API key. The deterministic engine handles the full workflow. If `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` is set, the tool uses the provider for a richer response; if the call fails, it falls back to the deterministic result automatically.

This means the suite is usable in CI, on a laptop with no network, or in a demo without provisioning credentials.

## Quick start

```bash
git clone https://github.com/malikatemz/ai-productivity-suite.git
cd ai-productivity-suite
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Optional provider configuration:

```bash
cp .env.example .env
# export ANTHROPIC_API_KEY=...
# or export OPENAI_API_KEY=...
```

## Usage

### Meeting notes

```bash
python meeting_notes.py --file samples/meeting_notes.txt
python meeting_notes.py --text "We agreed to ship Friday. Amina will update the docs."
python meeting_notes.py --file samples/meeting_notes.txt --offline
```

### Task prioritisation

```bash
python task_prioritiser.py --tasks "Fix login bug, Write docs, Prepare customer demo"
python task_prioritiser.py --file samples/tasks.txt
python task_prioritiser.py --file samples/tasks.txt --offline
```

### Daily planner

```bash
python daily_planner.py --tasks "Fix bug, Write tests, Review PR" --hours 6
python daily_planner.py --file samples/tasks.txt --hours 8 --start "9:00 AM"
python daily_planner.py --file samples/tasks.txt --hours 4 --offline
```

All scripts support `--model` to override the provider model.

## Example output

```markdown
| Priority | Task | Urgency | Impact | Recommended time |
|:--------:|:-----|:-------:|:------:|:-----------------|
| 10 | Fix security outage in login | 5 | 5 | Deep work (90 min) |
| 8 | Prepare customer demo | 4 | 4 | Focused (60 min) |
| 6 | Review PR #42 | 3 | 3 | Standard (45 min) |
| 5 | Write documentation for the API | 2 | 3 | Standard (45 min) |
| 4 | Clean up old feature flags | 2 | 2 | Quick win (25 min) |

Start with **Fix security outage in login** (priority 10/10) because it combines the highest urgency and impact.
```

## Project structure

```text
ai-productivity-suite/
├── common.py             # lazy Anthropic/OpenAI client
├── logic.py              # deterministic engines + LLM wrappers
├── meeting_notes.py      # CLI wrapper
├── task_prioritiser.py   # CLI wrapper
├── daily_planner.py      # CLI wrapper
├── samples/              # example notes and tasks
├── tests/                # pytest suite
├── requirements.txt
└── .github/workflows/ci.yml
```

## How the deterministic engines work

- **Meeting notes:** classifies lines by decision, action, and question keywords, then emits a four-section Markdown brief.
- **Task prioritisation:** scores urgency and impact from keyword signals (security/outage/customer/revenue/docs/cleanup), sums them, and sorts by priority.
- **Daily planning:** reuses the priority ranking, allocates 25–90 minute blocks, inserts a 15-minute break after roughly 90 minutes of work, reserves a 10-minute review, and lists anything that does not fit as deferred.

## Tests

```bash
pytest -q
```

The suite covers meeting extraction, prioritisation ordering, task parsing, short-day deferral, full-day breaks, and all three CLI entry points.

## Roadmap

- [x] Core functionality
- [x] Offline fallbacks
- [x] Tests
- [x] Documentation
- [x] CI workflow

---

*Part of the [Cybersecurity + Automation + AI 5-Month Roadmap](https://github.com/malikatemz).*
