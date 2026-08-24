from __future__ import annotations

import json
from collections.abc import AsyncIterator

import httpx

from app.config import settings


class LLMError(RuntimeError):
    pass


def _headers() -> dict[str, str]:
    if not settings.openrouter_api_key or settings.openrouter_api_key == "replace-me":
        raise LLMError("Set OPENROUTER_API_KEY in .env before starting an interview.")
    return {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": settings.http_referer,
        "X-Title": settings.app_name,
    }


async def stream_chat(messages: list[dict[str, str]]) -> AsyncIterator[str]:
    url = f"{settings.openrouter_base_url.rstrip('/')}/chat/completions"
    payload = {
        "model": settings.openrouter_model,
        "messages": messages,
        "stream": True,
        "temperature": 0.3,
    }
    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=15.0)) as client:
        async with client.stream("POST", url, headers=_headers(), json=payload) as response:
            if response.status_code >= 400:
                body = (await response.aread()).decode("utf-8", errors="replace")
                raise LLMError(f"OpenRouter error {response.status_code}: {body[:500]}")
            async for line in response.aiter_lines():
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if not data or data == "[DONE]":
                    continue
                try:
                    chunk = json.loads(data)
                except json.JSONDecodeError:
                    continue
                delta = chunk.get("choices", [{}])[0].get("delta", {})
                content = delta.get("content")
                if content:
                    yield content
