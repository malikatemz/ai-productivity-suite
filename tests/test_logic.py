from logic import parse_tasks, plan_day, prioritise_tasks, summarise_meeting

NOTES = """Product sync — 12 March
Attendees: Amina, Ben, Chen
We discussed the Q3 roadmap and the delayed payments integration.
Decision: ship the CSV importer before the API integration.
Amina will draft the migration guide by Friday.
Ben to follow up with the payments vendor about sandbox access.
Action: Chen to add regression tests for the importer.
Open question: do we need a data-retention policy before launch?
Blocker: legal review is still pending.
"""


def test_meeting_sections():
    result = summarise_meeting(NOTES, use_llm=False)
    assert "## Summary" in result
    assert "## Decisions" in result
    assert "ship the CSV importer" in result
    assert "## Action Items" in result
    assert "Amina will draft" in result
    assert "## Open Questions / Blockers" in result
    assert "legal review" in result


def test_prioritise_security_first():
    result = prioritise_tasks(
        "Write docs, Fix security outage, Review PR, Clean up files", use_llm=False
    )
    assert "| Priority | Task |" in result
    assert result.index("Fix security outage") < result.index("Write docs")
    assert "Start with **Fix security outage**" in result


def test_parse_tasks():
    assert parse_tasks("Fix bug, Write docs\nReview PR") == ["Fix bug", "Write docs", "Review PR"]


def test_plan_day_includes_review_and_deferred():
    result = plan_day(
        "Fix security outage, Prepare customer demo, Write docs",
        hours=2,
        start_time="9:00 AM",
        use_llm=False,
    )
    assert "| Time | Task | Notes |" in result
    assert "Review & wrap-up" in result
    assert "Deferred" in result


def test_plan_day_full_day_has_breaks():
    result = plan_day(
        "Fix security outage, Prepare customer demo, Review PR, Clean up files, Write docs",
        hours=8,
        start_time="9:00 AM",
        use_llm=False,
    )
    assert "Break" in result
    assert "Open buffer" in result or "Review & wrap-up" in result
