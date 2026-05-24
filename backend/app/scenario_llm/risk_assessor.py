"""RiskAssessor — Probability/severity scoring, cascading risk identification."""
from __future__ import annotations

import json
import logging
from typing import Any

from openai import AsyncAzureOpenAI

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a supply chain risk assessment specialist for AGI Food Division (UAE FMCG).
Given scenario impacts and proposed mitigations, assess:
1. Probability of worst-case outcome
2. Severity if no action taken
3. Cascading risks (second/third order effects)
4. Confidence in the analysis

Return JSON:
{
    "risk_narrative": "3-4 sentence executive risk assessment",
    "risk_matrix": {
        "probability": "high|medium|low",
        "severity": "critical|high|medium|low",
        "overall_risk_score": 8.5,
        "residual_risk_after_mitigation": 4.0
    },
    "cascading_risks": [
        {
            "risk": "Description of cascading risk",
            "trigger_condition": "What causes this",
            "probability": "high|medium|low",
            "impact": "Description of impact",
            "time_to_materialize_days": 14
        }
    ],
    "confidence_level": "high|medium|low",
    "key_uncertainties": ["uncertainty 1", "uncertainty 2"],
    "monitoring_indicators": ["KPI or signal to watch", ...]
}
"""


class RiskAssessor:
    def __init__(self, model: str, azure_endpoint: str, api_key: str) -> None:
        self._client = AsyncAzureOpenAI(
            azure_endpoint=azure_endpoint, api_key=api_key,
            api_version="2024-12-01-preview", timeout=60.0,
        )
        self._model = model

    async def assess(self, plan: dict[str, Any], impacts: dict[str, Any], mitigations: dict[str, Any]) -> dict[str, Any]:
        summary_stats = impacts.get("demand_impact", {}).get("summary_stats", {})
        kpi_deltas = impacts.get("kpi_projection", {}).get("deltas", {})
        mitigation_count = len(mitigations.get("mitigation_options", []))
        recovery_pct = mitigations.get("total_recovery_potential_pct", 0)

        user_msg = (
            f"Scenario: {plan.get('scenario_name', '')}\n"
            f"Type: {plan.get('scenario_type', '')}\n"
            f"Severity Estimate: {plan.get('severity_estimate', 'medium')}\n\n"
            f"Impacts:\n"
            f"- Affected SKUs: {summary_stats.get('total_affected_skus', 'N/A')}\n"
            f"- Critical: {summary_stats.get('critical_skus', 0)}\n"
            f"- KPI Deltas: {json.dumps(kpi_deltas)}\n\n"
            f"Mitigations: {mitigation_count} options proposed, {recovery_pct}% fill rate recovery potential\n\n"
            "Assess risks including cascading/second-order effects."
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
            logger.error("RiskAssessor LLM failed: %s", e)
            return {
                "risk_narrative": impacts.get("risk_assessment", "Risk assessment unavailable."),
                "risk_matrix": {"probability": "medium", "severity": "medium", "overall_risk_score": 5.0, "residual_risk_after_mitigation": 3.0},
                "cascading_risks": [],
                "confidence_level": "low",
                "key_uncertainties": ["LLM analysis unavailable"],
                "monitoring_indicators": [],
            }
