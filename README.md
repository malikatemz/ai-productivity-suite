# 📅 AI Productivity Suite

Three AI tools in one repo: meeting note summariser, task prioritiser, and daily planner.
Each is a standalone CLI tool powered by Claude.

## Tools

| Tool | Description |
|------|-------------|
| `meeting_notes.py` | Summarise raw meeting notes into action items |
| `task_prioritiser.py` | Rank a list of tasks by urgency and impact |
| `daily_planner.py` | Generate a structured daily plan from your task list |

## Setup
```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here
```

## Usage
```bash
# Summarise meeting notes
python meeting_notes.py --file notes.txt
python meeting_notes.py --text "We discussed Q3 roadmap..."

# Prioritise tasks
python task_prioritiser.py --tasks "Fix login bug, Write docs, Deploy to prod, Team 1:1"

# Generate a daily plan
python daily_planner.py --tasks tasks.txt --hours 6
```

## Part of
[Cybersecurity + Automation + AI 5-Month Roadmap](https://github.com/malikatemz) — Month 3
