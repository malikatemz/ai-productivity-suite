"""Shared LLM client helpers for the AI Productivity Suite."""

from __future__ import annotations

import os

DEFAULT_ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-latest")
DEFAULT_OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def llm_available() -> bool:
    """Return True when at least one supported provider key is configured."""
    return bool(os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY"))


def complete(system: str, prompt: str, model: str | None = None) -> str:
    """Call the configured LLM provider and return plain text.

    Raises RuntimeError when no provider is configured. Callers are expected to
    fall back to their deterministic implementation.
    """
    if os.getenv("ANTHROPIC_API_KEY"):
        import anthropic

        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        message = client.messages.create(
            model=model or DEFAULT_ANTHROPIC_MODEL,
            max_tokens=1500,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

    if os.getenv("OPENAI_API_KEY"):
        from openai import OpenAI

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=model or DEFAULT_OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""

    raise RuntimeError("No LLM provider configured")
