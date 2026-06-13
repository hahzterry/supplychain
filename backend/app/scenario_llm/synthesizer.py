"""Synthesizer — Executive summary, key decision points, recommended path."""
from __future__ import annotations

import json
import logging
from typing import Any

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a senior supply chain strategist synthesizing analysis for Héroux-Devtek Inc. executives.
Given all analysis components, produce a clear executive synthesis.

Return JSON:
{
    "executive_brief": "3-5 sentence executive summary of the situation, impact, and recommended response",
    "decision_points": [
        {
            "decision": "What needs to be decided",
            "deadline": "By when",
            "options": ["Option A", "Option B"],
            "recommendation": "Which option and why",
            "risk_of_inaction": "What happens if no decision"
        }
    ],
    "recommended_actions": [
        "Prioritized action 1",
        "Prioritized action 2"
    ],
    "confidence_level": "high|medium|low",
    "next_review_trigger": "When to reassess (e.g., 'if fill rate drops below 94%')"
}
"""


class Synthesizer:
    def __init__(self, model: str, azure_endpoint: str, api_key: str) -> None:
        self._client = AsyncOpenAI(
            base_url=f"{azure_endpoint.rstrip('/')}/openai/v1",
            api_key=api_key, timeout=60.0,
        )
        self._model = model

    async def synthesize(
        self,
        plan: dict[str, Any],
        impacts: dict[str, Any],
        mitigations: dict[str, Any],
        risks: dict[str, Any],
    ) -> dict[str, Any]:
        summary_stats = impacts.get("demand_impact", {}).get("summary_stats", {})
        kpi_deltas = impacts.get("kpi_projection", {}).get("deltas", {})
        mitigation_options = mitigations.get("mitigation_options", [])[:5]
        risk_narrative = risks.get("risk_narrative", "")
        cascading = risks.get("cascading_risks", [])[:3]

        mit_summary = "\n".join(
            f"  - [{m.get('priority', '')}] {m.get('action', '')} (CAD {m.get('cost_cad', 0):,.0f}, +{m.get('fill_rate_recovery', 0)}% FR)"
            for m in mitigation_options
        )
        cascade_summary = "\n".join(f"  - {c.get('risk', '')}" for c in cascading)

        user_msg = (
            f"Scenario: {plan.get('scenario_name', '')}\n"
            f"Severity: {plan.get('severity_estimate', 'medium')}\n\n"
            f"Impact Summary:\n"
            f"  Affected SKUs: {summary_stats.get('total_affected_skus', 'N/A')} "
            f"(Critical: {summary_stats.get('critical_skus', 0)})\n"
            f"  KPI Deltas: {json.dumps(kpi_deltas)}\n\n"
            f"Risk Assessment: {risk_narrative}\n"
            f"Cascading Risks:\n{cascade_summary}\n\n"
            f"Top Mitigations:\n{mit_summary}\n\n"
            "Synthesize into executive brief with clear decision points."
        )

        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0.3,
                max_completion_tokens=1500,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content or "{}"
            return json.loads(content)
        except Exception as e:
            logger.error("Synthesizer LLM failed: %s", e)
            actions = impacts.get("recommended_actions", [])
            if not actions:
                actions = [m.get("action", "") for m in mitigation_options[:5]]
            return {
                "executive_brief": risk_narrative or "Analysis complete. Review impact details for recommended actions.",
                "decision_points": [],
                "recommended_actions": actions,
                "confidence_level": "low",
                "next_review_trigger": "Review in 48 hours or if KPIs deteriorate",
            }
