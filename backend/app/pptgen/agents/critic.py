"""CriticAgent - Quality review and scoring.

Reviews the completed deck specification for quality issues including:
- Content overflow (delegated to overflow_checker)
- Data accuracy and consistency
- Clarity and readability
- Layout appropriateness
- Overall presentation flow

Scores 1-10, pass threshold 7+.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from openai import AsyncOpenAI

from ..ppt.overflow_checker import check_overflow
from ..schemas import CritiqueIssue, CritiqueResult, DeckRequest, DeckSpec

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a quality reviewer for Héroux-Devtek Inc. supply chain presentations.
Review the deck for issues and provide a quality score from 1-10.

Scoring criteria:
- 9-10: Excellent. Ready for executive presentation with no changes.
- 7-8: Good. Minor suggestions but no blocking issues.
- 5-6: Acceptable but needs improvement. Some issues affect clarity.
- 3-4: Below standard. Multiple issues need fixing.
- 1-2: Unacceptable. Major rework needed.

Review dimensions:
1. DATA ACCURACY: Numbers should be consistent across slides. KPIs should use correct units.
2. CLARITY: Bullet points should be concise and actionable. Titles should be descriptive.
3. FLOW: Slides should follow a logical narrative arc.
4. COMPLETENESS: All sections should have meaningful content, no placeholders.
5. LAYOUT FIT: Content should match its assigned layout type.
6. CONSISTENCY: Formatting, terminology, and style should be uniform.
7. EXECUTIVE READINESS: Appropriate detail level for the audience.

For each issue found, provide:
- slide_id: ID of the affected slide ("" for deck-level issues)
- severity: "error" (must fix), "warning" (should fix), or "suggestion" (nice to have)
- category: one of "overflow", "data_accuracy", "clarity", "layout", "consistency", "completeness", "flow"
- description: clear description of the issue
- fix_instruction: how to fix it

Respond with JSON: {"overall_score": int, "suggestions": ["str", ...], "issues": [...]}
"""


class CriticAgent:
    """Reviews deck quality and provides actionable feedback."""

    def __init__(self, model: str, azure_endpoint: str, api_key: str) -> None:
        self._client = AsyncOpenAI(
            base_url=f"{azure_endpoint.rstrip('/')}/openai/v1",
            api_key=api_key,
            timeout=60.0,
        )
        self._model = model

    async def review(self, deck: DeckSpec, request: Any = None) -> CritiqueResult:
        """Review the deck and return a quality assessment.

        Args:
            deck: Complete DeckSpec to review.
            request: Optional DeckRequest for additional context (unused currently).

        Returns:
            CritiqueResult with score, pass/fail, and issues list.
        """
        return await self.critique(deck)

    async def critique(self, deck: DeckSpec) -> CritiqueResult:
        """Review the deck and return a quality assessment.

        Args:
            deck: Complete DeckSpec to review.

        Returns:
            CritiqueResult with score, pass/fail, and issues list.
        """
        logger.info("CriticAgent: reviewing deck with %d slides", len(deck.slides))

        # Step 1: Run rules-based overflow checks
        overflow_issues = check_overflow(deck.slides)

        # Step 2: Run LLM-based quality review
        try:
            llm_result = await self._llm_review(deck)
        except Exception as e:
            logger.error("CriticAgent: LLM review failed: %s", e)
            score = 8 if not overflow_issues else max(4, 8 - len(overflow_issues))
            return CritiqueResult(
                overall_score=score,
                pass_threshold=score >= 7,
                issues=overflow_issues,
                suggestions=["LLM review unavailable. Overflow check completed."],
            )

        # Step 3: Merge issues (deduplicate)
        all_issues = overflow_issues + llm_result.get("issues", [])
        seen: set[tuple[str, str, str]] = set()
        deduped: list[CritiqueIssue] = []
        for issue in all_issues:
            if isinstance(issue, CritiqueIssue):
                key = (issue.slide_id, issue.category, issue.description[:50])
            else:
                key = (issue.get("slide_id", ""), issue.get("category", ""), issue.get("description", "")[:50])
            if key not in seen:
                seen.add(key)
                if isinstance(issue, CritiqueIssue):
                    deduped.append(issue)
                else:
                    deduped.append(CritiqueIssue(**issue))

        # Adjust score based on error count
        error_count = sum(1 for i in deduped if i.severity == "error")
        score = llm_result.get("overall_score", 7)
        if error_count > 0:
            score = min(score, max(3, score - error_count))

        result = CritiqueResult(
            overall_score=score,
            pass_threshold=score >= 7,
            issues=deduped,
            suggestions=llm_result.get("suggestions", []),
        )

        logger.info(
            "CriticAgent: score=%d, passed=%s, issues=%d",
            result.overall_score,
            result.pass_threshold,
            len(result.issues),
        )
        return result

    async def _llm_review(self, deck: DeckSpec) -> dict[str, Any]:
        """Run LLM-based quality review."""
        deck_summary = self._serialize_deck(deck)

        user_prompt = f"""Review this supply chain presentation deck:

{deck_summary}

Provide your quality assessment as JSON with:
- "overall_score": integer 1-10
- "suggestions": array of high-level improvement suggestions (strings)
- "issues": array of specific issue objects (can be empty if no issues found)
"""

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_completion_tokens=2000,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content or "{}"
        if not raw.strip() or raw.strip() == "{}":
            return CritiqueResult(overall_score=7, pass_threshold=True, issues=[], suggestions=[])

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return CritiqueResult(overall_score=7, pass_threshold=True, issues=[], suggestions=[])

        # Parse issues
        issues: list[dict[str, Any]] = []
        for issue_data in parsed.get("issues", []):
            issues.append({
                "slide_id": issue_data.get("slide_id", ""),
                "severity": issue_data.get("severity", "warning"),
                "category": issue_data.get("category", "clarity"),
                "description": issue_data.get("description", ""),
                "fix_instruction": issue_data.get("fix_instruction", ""),
            })

        return {
            "overall_score": parsed.get("overall_score", 7),
            "suggestions": parsed.get("suggestions", []),
            "issues": issues,
        }

    def _serialize_deck(self, deck: DeckSpec) -> str:
        """Serialize deck to compact string for LLM review."""
        lines: list[str] = [
            f"Title: {deck.title}",
            f"Template: {deck.template}",
            f"Slides: {len(deck.slides)}",
            "",
        ]

        for slide in deck.slides:
            lines.append(f"--- Slide [{slide.id}] [{slide.layout.value}] ---")
            lines.append(f"Title: {slide.title}")
            if slide.subtitle:
                lines.append(f"Subtitle: {slide.subtitle}")
            if slide.content.bullets:
                for b in slide.content.bullets:
                    lines.append(f"  - {b}")
            if slide.content.kpis:
                cards_str = ", ".join(f"{c.label}={c.value}" for c in slide.content.kpis)
                lines.append(f"KPIs: {cards_str}")
            if slide.content.table:
                lines.append(f"Table: {len(slide.content.table.headers)} cols x {len(slide.content.table.rows)} rows")
            if slide.content.chart_data:
                lines.append(f"Chart: {slide.content.chart_data.chart_type}")
            lines.append("")

        return "\n".join(lines)
