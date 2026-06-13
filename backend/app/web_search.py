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

    Disabled: requires OpenAI Responses API with web_search_preview tool (gpt-5.4-mini).
    Re-enable when switching back to a model that supports the Responses API.
    """
    return ""
