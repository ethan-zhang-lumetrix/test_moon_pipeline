from collections.abc import Iterator

import anthropic

from config import settings

_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


def call_claude(prompt: str) -> str:
    response = _client.messages.create(
        model=settings.model_name,
        max_tokens=settings.max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


call_claude.model_name = settings.model_name


def stream_claude(prompt: str) -> Iterator[str]:
    with _client.messages.stream(
        model=settings.model_name,
        max_tokens=settings.max_tokens,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for event in stream:
            if event.type == "content_block_delta":
                yield event.delta.text


stream_claude.model_name = settings.model_name
