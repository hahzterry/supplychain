"""Web search context using Azure OpenAI Responses API built-in web_search tool."""
from __future__ import annotations

import logging
import re
import time

from .config import settings

logger = logging.getLogger(__name__)

_cache: dict[str, tuple[float, str]] = {}
CACHE_TTL_SECONDS = 1800


async def web_search_context(query: str) -> str:
    """Search the web for context and return a summarized text response.

    Uses Azure OpenAI Responses API with built-in web_search tool.
    Results are cached for 30 minutes.
    """
    cache_key = query.lower().strip()
    now = time.time()

    if cache_key in _cache:
        cached_time, cached_result = _cache[cache_key]
        if now - cached_time < CACHE_TTL_SECONDS:
            logger.info("Web search cache hit for: %s", query[:50])
            return cached_result

    try:
        from openai import AzureOpenAI

        client = AzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version="2025-03-01-preview",
        )

        resp = client.responses.create(
            model=settings.azure_openai_deployment,
            input=(
                f"Search for the latest information about: {query}\n\n"
                "Provide a concise summary (3-5 bullet points) of the most relevant and recent "
                "information found. Focus on facts, news, and data. Include source names where possible."
            ),
            tools=[{"type": "web_search", "search_context_size": "medium"}],
            max_output_tokens=1500,
        )

        text = ""
        for item in resp.output:
            if item.type == "message":
                for content in item.content:
                    if hasattr(content, "text"):
                        text += content.text

        text = re.sub(r'citeturn\d+\w*\d*', '', text).strip()

        if text:
            _cache[cache_key] = (now, text)
            logger.info("Web search completed for: %s (%d chars)", query[:50], len(text))
        return text

    except Exception as e:
        logger.warning("Web search failed for '%s': %s", query[:50], e)
        if cache_key in _cache:
            return _cache[cache_key][1]
        return ""
