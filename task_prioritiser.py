"""
task_prioritiser.py - Rank tasks by urgency and impact using AI.
Usage: python task_prioritiser.py --tasks "Fix bug, Write docs, Deploy"
"""
import argparse, os
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM = """You are a productivity coach. Given a list of tasks:
1. Score each task on Urgency (1-5) and Impact (1-5)
2. Calculate Priority = Urgency + Impact
3. Return a ranked table: Priority | Task | Urgency | Impact | Recommended time
4. Add a 1-sentence recommendation on what to tackle first and why.
Format the table in Markdown."""

def prioritise(tasks: str) -> str:
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=SYSTEM,
        messages=[{"role": "user", "content": f"Tasks to prioritise:\n{tasks}"}],
    )
    return msg.content[0].text

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--tasks", help="Comma-separated task list")
    g.add_argument("--file", help="File with one task per line")
    args = p.parse_args()
    tasks = open(args.file).read() if args.file else args.tasks
    print("\n" + prioritise(tasks))
