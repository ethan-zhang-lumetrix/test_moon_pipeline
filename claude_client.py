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
