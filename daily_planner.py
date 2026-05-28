"""
daily_planner.py - Generate a time-blocked daily plan from your task list.
Usage: python daily_planner.py --tasks "Fix bug, Write tests, Review PR" --hours 6
"""
import argparse, os
from datetime import datetime
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM = """You are a productivity expert. Create a realistic time-blocked daily plan.
Rules:
- Start at 9:00 AM unless specified
- Include 15-min breaks every 90 minutes
- Batch similar tasks
- Put hardest/most important work in the first 2 hours
- End with a 10-min review block
Format: time-blocked schedule as a Markdown table with Time | Task | Notes columns."""

def plan(tasks: str, hours: int, start_time: str = "9:00 AM") -> str:
    prompt = f"Tasks: {tasks}\nAvailable hours: {hours}\nStart time: {start_time}\nToday: {datetime.now():%A, %B %d}"
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--tasks")
    g.add_argument("--file")
    p.add_argument("--hours", type=int, default=8)
    p.add_argument("--start", default="9:00 AM")
    args = p.parse_args()
    tasks = open(args.file).read() if args.file else args.tasks
    print("\n" + plan(tasks, args.hours, args.start))
