#!/usr/bin/env python3
"""Minimal LLM JSON client for Review See-Through.

Single entry point: complete_json(system_cached, user, schema).
Provider is Anthropic by default; set LLM_PROVIDER=openai to switch.
The system prompt (shared preamble + paper text) is the stable cache
prefix, so repeated loop iterations within the cache TTL pay ~0.1x
input price on that span.
"""

from __future__ import annotations

import json
import os


class LLMUnavailable(Exception):
    """Raised when no provider credentials/SDK are usable."""


DEFAULT_ANTHROPIC_MODEL = "claude-opus-4-8"
# ponytail: OpenAI path is the event-day escape hatch; model name must be
# confirmed against the credits handed out at the venue (LLM_MODEL env).
DEFAULT_OPENAI_MODEL = "gpt-5.1"
ANTHROPIC_MAX_TOKENS = 16000
# Reasoning models spend max_completion_tokens on reasoning too — leave
# headroom so the JSON payload is never truncated mid-string.
OPENAI_MAX_TOKENS = 32000


def complete_json(system_cached: str, user: str, schema: dict) -> dict:
    provider = os.environ.get("LLM_PROVIDER", "anthropic").lower()
    if provider == "openai":
        return _openai_json(system_cached, user, schema)
    return _anthropic_json(system_cached, user, schema)


def _anthropic_json(system_cached: str, user: str, schema: dict) -> dict:
    try:
        import anthropic
    except ImportError as error:
        raise LLMUnavailable("anthropic SDK is not installed") from error

    client = anthropic.Anthropic()
    try:
        response = client.messages.create(
            model=os.environ.get("LLM_MODEL", DEFAULT_ANTHROPIC_MODEL),
            max_tokens=ANTHROPIC_MAX_TOKENS,
            thinking={"type": "adaptive"},
            system=[
                {
                    "type": "text",
                    "text": system_cached,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            output_config={"format": {"type": "json_schema", "schema": schema}},
            messages=[{"role": "user", "content": user}],
        )
    except anthropic.AuthenticationError as error:
        raise LLMUnavailable(f"anthropic auth failed: {error}") from error
    if response.stop_reason == "refusal":
        raise LLMUnavailable("anthropic request was refused")
    text = next(block.text for block in response.content if block.type == "text")
    return json.loads(text)


def _openai_json(system_cached: str, user: str, schema: dict) -> dict:
    try:
        from openai import OpenAI
    except ImportError as error:
        raise LLMUnavailable("openai SDK is not installed") from error

    client = OpenAI()
    response = client.chat.completions.create(
        model=os.environ.get("LLM_MODEL", DEFAULT_OPENAI_MODEL),
        max_completion_tokens=OPENAI_MAX_TOKENS,
        reasoning_effort=os.environ.get("LLM_REASONING_EFFORT", "low"),
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "result", "schema": schema, "strict": True},
        },
        messages=[
            {"role": "system", "content": system_cached},
            {"role": "user", "content": user},
        ],
    )
    return json.loads(response.choices[0].message.content)
