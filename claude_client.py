from collections.abc import Iterator
from typing import Optional

import anthropic
from anthropic import APIStatusError, AuthenticationError

from config import settings

_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


def call_claude(prompt: str, max_tokens: Optional[int] = None) -> str:
    response = _client.messages.create(
        model=settings.model_name,
        max_tokens=max_tokens or settings.max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


call_claude.model_name = settings.model_name


def stream_claude(prompt: str, max_tokens: Optional[int] = None) -> Iterator[str]:
    with _client.messages.stream(
        model=settings.model_name,
        max_tokens=max_tokens or settings.max_tokens,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for event in stream:
            if event.type == "content_block_delta":
                yield event.delta.text


stream_claude.model_name = settings.model_name


def check_health() -> dict:
    """Check Claude API connectivity with a minimal call."""
    try:
        _client.messages.create(
            model=settings.model_name,
            max_tokens=1,
            messages=[{"role": "user", "content": "hi"}],
        )
        return {"status": "healthy", "model": settings.model_name}
    except AuthenticationError:
        return {"status": "unhealthy", "reason": "认证失败"}
    except anthropic.APIStatusError as e:
        return {"status": "unhealthy", "reason": f"API 错误: {e.message}"}
    except Exception as e:
        return {"status": "unhealthy", "reason": str(e)}
