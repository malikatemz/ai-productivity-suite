"""Deterministic fallbacks and LLM-backed productivity tools."""

from __future__ import annotations

import re
from datetime import datetime, timedelta

from common import complete, llm_available

MEETING_SYSTEM = """You are an expert meeting facilitator. Given raw meeting notes:
1. Write a 2-sentence summary of what was discussed
2. List all decisions made (as bullets)
3. List all action items with owner and deadline if mentioned
4. List any open questions or blockers
Be concise. Use bullet points. Never invent information not in the notes.
Return Markdown with the headings: Summary, Decisions, Action Items, Open Questions / Blockers."""

TASK_SYSTEM = """You are a productivity coach. Given a list of tasks:
1. Score each task on Urgency (1-5) and Impact (1-5)
2. Calculate Priority = Urgency + Impact
3. Return a ranked Markdown table: Priority | Task | Urgency | Impact | Recommended time
4. Add a 1-sentence recommendation on what to tackle first and why."""

PLANNER_SYSTEM = """You are a productivity expert. Create a realistic time-blocked daily plan.
Rules:
- Start at the supplied time
- Include 15-min breaks every 90 minutes
- Batch similar tasks
- Put hardest/most important work in the first 2 hours
- End with a 10-min review block
Format: time-blocked schedule as a Markdown table with Time | Task | Notes columns."""

_DECISION_KEYWORDS = ("decided", "decision", "agreed", "approved", "chose", "will go with")
_ACTION_KEYWORDS = (
    "action",
    "todo",
    "to-do",
    "follow up",
    "will ",
    " to ",
    "owner",
    "assign",
    "next step",
    "by ",
)
_QUESTION_KEYWORDS = ("?", "blocker", "open question", "risk", "pending")

_URGENCY_KEYWORDS = {
    "urgent": 5,
    "asap": 5,
    "today": 5,
    "critical": 5,
    "security": 5,
    "outage": 5,
    "bug": 5,
    "deadline": 4,
    "blocker": 5,
    "customer": 4,
    "client": 4,
    "revenue": 4,
    "demo": 4,
    "release": 4,
    "tomorrow": 4,
    "review": 3,
    "fix": 3,
    "test": 3,
    "deploy": 3,
    "docs": 2,
    "documentation": 2,
    "clean up": 2,
    "cleanup": 2,
    "refactor": 2,
}

_IMPACT_KEYWORDS = {
    "revenue": 5,
    "security": 5,
    "outage": 5,
    "launch": 5,
    "strategic": 5,
    "customer": 4,
    "bug": 4,
    "release": 4,
    "demo": 4,
    "compliance": 4,
    "review": 3,
    "test": 3,
    "docs": 3,
    "documentation": 3,
    "automation": 3,
    "clean up": 2,
    "cleanup": 2,
    "refactor": 2,
}


def _clean_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines():
        line = re.sub(r"^[-*•\d.)\s]+", "", raw.strip()).strip()
        if line:
            lines.append(line)
    return lines


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        key = item.lower()
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def _section(title: str, items: list[str], empty: str = "None captured.") -> str:
    body = "\n".join(f"- {item}" for item in items) if items else f"- {empty}"
    return f"## {title}\n{body}"


def _heuristic_meeting(text: str) -> str:
    lines = _clean_lines(text)
    decisions = [
        line for line in lines if any(keyword in line.lower() for keyword in _DECISION_KEYWORDS)
    ]
    actions = [
        line
        for line in lines
        if any(keyword in line.lower() for keyword in _ACTION_KEYWORDS) and line not in decisions
    ]
    questions = [
        line
        for line in lines
        if any(keyword in line.lower() for keyword in _QUESTION_KEYWORDS)
        and line not in decisions
        and line not in actions
    ]
    summary_lines = [
        line
        for line in lines
        if line not in decisions and line not in actions and line not in questions
    ]
    summary = " ".join(summary_lines[:2]) if summary_lines else "No summary could be generated."
    return "\n\n".join(
        [
            _section("Summary", [summary]),
            _section("Decisions", _dedupe(decisions)),
            _section("Action Items", _dedupe(actions)),
            _section("Open Questions / Blockers", _dedupe(questions)),
        ]
    )


def summarise_meeting(text: str, use_llm: bool = False, model: str | None = None) -> str:
    if use_llm and llm_available():
        try:
            return complete(MEETING_SYSTEM, f"Meeting notes:\n\n{text}", model=model)
        except Exception:
            pass
    return _heuristic_meeting(text)


def parse_tasks(raw: str | list[str]) -> list[str]:
    if isinstance(raw, list):
        candidates = raw
    else:
        candidates = re.split(r"[\n,;]+", raw)
    tasks = []
    for candidate in candidates:
        task = re.sub(r"^\s*[-*•\d.)]+\s*", "", candidate).strip()
        if task:
            tasks.append(task)
    return _dedupe(tasks)


def _score(text: str, mapping: dict[str, int]) -> int:
    lowered = text.lower()
    score = 1
    for keyword, value in mapping.items():
        if keyword in lowered:
            score = max(score, value)
    return score


def _task_scores(tasks: list[str]) -> list[dict[str, object]]:
    scored = []
    for task in tasks:
        urgency = _score(task, _URGENCY_KEYWORDS)
        impact = _score(task, _IMPACT_KEYWORDS)
        scored.append(
            {
                "task": task,
                "urgency": urgency,
                "impact": impact,
                "priority": urgency + impact,
            }
        )
    return sorted(scored, key=lambda item: (-int(item["priority"]), -int(item["urgency"]), str(item["task"])))


def _recommended_time(priority: int) -> str:
    if priority >= 9:
        return "Deep work (90 min)"
    if priority >= 7:
        return "Focused (60 min)"
    if priority >= 5:
        return "Standard (45 min)"
    return "Quick win (25 min)"


def prioritise_tasks(raw: str | list[str], use_llm: bool = False, model: str | None = None) -> str:
    if use_llm and llm_available():
        try:
            return complete(TASK_SYSTEM, f"Tasks to prioritise:\n{raw}", model=model)
        except Exception:
            pass
    tasks = parse_tasks(raw)
    if not tasks:
        return "No tasks provided."
    scored = _task_scores(tasks)
    lines = [
        "| Priority | Task | Urgency | Impact | Recommended time |",
        "|:--------:|:-----|:-------:|:------:|:-----------------|",
    ]
    for item in scored:
        lines.append(
            f"| {item['priority']} | {item['task']} | {item['urgency']} | "
            f"{item['impact']} | {_recommended_time(int(item['priority']))} |"
        )
    top = scored[0]
    lines += [
        "",
        f"Start with **{top['task']}** (priority {top['priority']}/10) because it combines "
        "the highest urgency and impact.",
    ]
    return "\n".join(lines)


def _parse_start(start_time: str) -> datetime:
    for fmt in ("%I:%M %p", "%I%p", "%H:%M"):
        try:
            return datetime.strptime(start_time.strip(), fmt)
        except ValueError:
            continue
    raise ValueError(f"Could not parse start time: {start_time!r}. Use '9:00 AM' or '09:00'.")


def _format_time(value: datetime) -> str:
    return value.strftime("%I:%M %p").lstrip("0")


def plan_day(
    raw: str | list[str],
    hours: int = 8,
    start_time: str = "9:00 AM",
    use_llm: bool = False,
    model: str | None = None,
) -> str:
    if use_llm and llm_available():
        prompt = f"Tasks: {raw}\nAvailable hours: {hours}\nStart time: {start_time}\nToday: {datetime.now():%A, %B %d}"
        try:
            return complete(PLANNER_SYSTEM, prompt, model=model)
        except Exception:
            pass

    tasks = parse_tasks(raw)
    if not tasks:
        return "No tasks provided."
    if hours < 1:
        raise ValueError("hours must be at least 1")

    scored = _task_scores(tasks)
    remaining = max(30, hours * 60) - 10  # reserve a 10-minute review block
    current = _parse_start(start_time)
    rows: list[tuple[str, str, str]] = []
    deferred: list[str] = []
    work_since_break = 0

    for item in scored:
        task = str(item["task"])
        desired = int(_recommended_time(int(item["priority"])).split("(")[-1].split()[0])
        if remaining < 25:
            deferred.append(task)
            continue
        duration = min(desired, remaining)
        if duration < 25:
            deferred.append(task)
            continue
        if work_since_break and work_since_break + duration > 90 and remaining >= 40:
            rows.append((_format_time(current), "Break", "15 min"))
            current += timedelta(minutes=15)
            remaining -= 15
            work_since_break = 0
        rows.append(
            (
                _format_time(current),
                task,
                f"{duration} min | priority {item['priority']}/10",
            )
        )
        current += timedelta(minutes=duration)
        remaining -= duration
        work_since_break += duration

    if remaining >= 10:
        rows.append((_format_time(current), "Review & wrap-up", "10 min"))
        current += timedelta(minutes=10)
        remaining -= 10
    if remaining >= 30:
        rows.append((_format_time(current), "Open buffer / deep work", f"{remaining} min"))

    lines = ["| Time | Task | Notes |", "|:-----|:-----|:------|"]
    lines += [f"| {time} | {task} | {notes} |" for time, task, notes in rows]
    if deferred:
        lines += ["", "**Deferred (not enough time today):** " + ", ".join(deferred)]
    return "\n".join(lines)
