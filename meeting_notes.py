"""
meeting_notes.py - Summarise raw meeting notes into structured action items.
Usage: python meeting_notes.py --file notes.txt
"""
import argparse, os
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM = """You are an expert meeting facilitator. Given raw meeting notes:
1. Write a 2-sentence summary of what was discussed
2. List all decisions made (as bullets)
3. List all action items with owner and deadline if mentioned
4. List any open questions or blockers
Be concise. Use bullet points. Never invent information not in the notes."""

def summarise(text: str) -> str:
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=SYSTEM,
        messages=[{"role": "user", "content": f"Meeting notes:\n\n{text}"}],
    )
    return msg.content[0].text

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--file")
    g.add_argument("--text")
    args = p.parse_args()
    content = open(args.file).read() if args.file else args.text
    print("\n" + "="*60)
    print(summarise(content))
    print("="*60)
