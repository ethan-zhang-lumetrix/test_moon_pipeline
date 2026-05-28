import time
from collections.abc import Iterator

import anthropic

from config import settings
from logger import get_logger

logger = get_logger(__name__)
_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)


def call_claude(prompt: str) -> str:
    start = time.time()
    response = _client.messages.create(
        model=settings.model_name,
        max_tokens=settings.max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    duration_ms = (time.time() - start) * 1000
    logger.info(
        "call_claude | model=%s | prompt_len=%d | duration=%.2fms",
        settings.model_name,
        len(prompt),
        duration_ms,
    )
    return response.content[0].text


call_claude.model_name = settings.model_name


def stream_claude(prompt: str) -> Iterator[str]:
    start = time.time()
    token_count = 0
    with _client.messages.stream(
        model=settings.model_name,
        max_tokens=settings.max_tokens,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for event in stream:
            if event.type == "content_block_delta":
                token_count += 1
                yield event.delta.text
    duration_ms = (time.time() - start) * 1000
    logger.info(
        "stream_claude | model=%s | prompt_len=%d | tokens=%d | duration=%.2fms",
        settings.model_name,
        len(prompt),
        token_count,
        duration_ms,
    )


stream_claude.model_name = settings.model_name
