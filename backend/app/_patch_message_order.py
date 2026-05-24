"""Monkey-patch AG-UI message normalizer to fix CopilotKit message ordering.

CopilotKit sends tool-result messages *before* the assistant message that
contains the corresponding toolCalls.  The Responses API requires:
assistant(toolCalls) -> tool(result).

This module patches ``normalize_agui_input_messages`` so that out-of-order
tool results are relocated after their matching assistant message before the
rest of the pipeline sees them.
"""
from __future__ import annotations

from typing import Any

import agent_framework_ag_ui._message_adapters as _adapters
import agent_framework_ag_ui._agent_run as _agent_run

_original_normalize = _adapters.normalize_agui_input_messages


def _reorder_raw_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tool_call_to_assistant_idx: dict[str, int] = {}
    for i, msg in enumerate(messages):
        tool_calls = msg.get("toolCalls") or msg.get("tool_calls") or []
        if msg.get("role") == "assistant" and tool_calls:
            for tc in tool_calls:
                tc_id = tc.get("id", "")
                if tc_id:
                    tool_call_to_assistant_idx[tc_id] = i

    orphaned: list[tuple[int, dict]] = []
    keep: list[tuple[int, dict]] = []

    for i, msg in enumerate(messages):
        if msg.get("role") == "tool":
            tc_id = msg.get("toolCallId") or msg.get("tool_call_id") or ""
            asst_idx = tool_call_to_assistant_idx.get(tc_id)
            if asst_idx is not None and asst_idx > i:
                orphaned.append((i, msg))
                continue
        keep.append((i, msg))

    if not orphaned:
        return messages

    orphan_by_tc: dict[str, list[dict]] = {}
    for _, msg in orphaned:
        tc_id = msg.get("toolCallId") or msg.get("tool_call_id") or ""
        orphan_by_tc.setdefault(tc_id, []).append(msg)

    result: list[dict] = []
    for _, msg in keep:
        result.append(msg)
        tool_calls = msg.get("toolCalls") or msg.get("tool_calls") or []
        if msg.get("role") == "assistant" and tool_calls:
            for tc in tool_calls:
                tc_id = tc.get("id", "")
                for orphan in orphan_by_tc.pop(tc_id, []):
                    result.append(orphan)

    return result


def _patched_normalize(messages, **kwargs):
    messages = _reorder_raw_messages(messages)
    return _original_normalize(messages, **kwargs)


_adapters.normalize_agui_input_messages = _patched_normalize
_agent_run.normalize_agui_input_messages = _patched_normalize
