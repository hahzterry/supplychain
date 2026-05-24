"""RepairAgent - Fixes issues identified by the CriticAgent.

Takes the critique feedback and applies targeted fixes to the deck,
addressing overflow issues, clarity problems, and other quality concerns.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from openai import AsyncAzureOpenAI

from ..schemas import (
    ChartData,
    ChartSeries,
    ColumnContent,
    CritiqueIssue,
    CritiqueResult,
    DeckSpec,
    KPICard,
    SlideContent,
    SlideLayout,
    SlideSpec,
    TableContent,
)

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a supply chain presentation repair agent for AGI Food Division.
Your job is to fix specific issues identified in a quality review.

When fixing slides:
1. Preserve the original meaning and data accuracy
2. Only change what is necessary to fix the identified issue
3. Keep bullets concise (max 120 chars, max 6 per slide)
4. Keep tables to max 8 rows
5. Maintain professional executive tone
6. Do not invent new data - only reformulate existing content

Respond with the corrected slide content as JSON matching the original schema.
"""


class RepairAgent:
    """Fixes quality issues identified by CriticAgent."""

    def __init__(self, model: str, azure_endpoint: str, api_key: str) -> None:
        self._client = AsyncAzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version="2024-12-01-preview",
            timeout=60.0,
        )
        self._model = model

    async def fix(self, deck: DeckSpec, critique: CritiqueResult) -> DeckSpec:
        """Alias for repair() — used by SupervisorAgent."""
        return await self.repair(deck, critique)

    async def repair(self, deck: DeckSpec, critique: CritiqueResult) -> DeckSpec:
        """Apply repairs to the deck based on critique feedback.

        Args:
            deck: The DeckSpec to repair.
            critique: CritiqueResult with issues to fix.

        Returns:
            Repaired DeckSpec.
        """
        if not critique.issues:
            logger.info("RepairAgent: no issues to fix")
            return deck

        # Separate issues by type
        overflow_issues = [i for i in critique.issues if i.category == "overflow"]
        llm_issues = [i for i in critique.issues if i.category != "overflow"]

        logger.info(
            "RepairAgent: fixing %d overflow + %d other issues",
            len(overflow_issues),
            len(llm_issues),
        )

        # Step 1: Apply deterministic overflow fixes
        if overflow_issues:
            deck = self._fix_overflow_issues(deck, overflow_issues)

        # Step 2: Apply LLM-based fixes for non-overflow issues
        if llm_issues:
            # Group issues by slide_id
            issues_by_slide: dict[str, list[CritiqueIssue]] = {}
            for issue in llm_issues:
                if issue.slide_id:
                    issues_by_slide.setdefault(issue.slide_id, []).append(issue)

            for slide_id, issues in issues_by_slide.items():
                # Find the slide by id
                slide_idx = next(
                    (i for i, s in enumerate(deck.slides) if s.id == slide_id), None
                )
                if slide_idx is not None:
                    try:
                        repaired_slide = await self._repair_slide(deck.slides[slide_idx], issues)
                        deck.slides[slide_idx] = repaired_slide
                    except Exception as e:
                        logger.warning(
                            "RepairAgent: failed to repair slide %s: %s", slide_id, e
                        )

        # Step 3: Validate layout enum values
        deck = self._fix_layouts(deck)

        logger.info("RepairAgent: repairs complete")
        return deck

    @staticmethod
    def _fix_layouts(deck: DeckSpec) -> DeckSpec:
        """Validate and fix layout enum values on all slides."""
        valid_layouts = {layout.value for layout in SlideLayout}
        for slide in deck.slides:
            if slide.layout.value not in valid_layouts:
                slide.layout = SlideLayout.BULLETS
        return deck

    def _fix_overflow_issues(self, deck: DeckSpec, issues: list[CritiqueIssue]) -> DeckSpec:
        """Apply deterministic fixes for overflow issues."""
        for issue in issues:
            # Find slide by id
            slide = next((s for s in deck.slides if s.id == issue.slide_id), None)
            if slide is None:
                continue

            content = slide.content
            desc_lower = issue.description.lower()

            if "bullets" in desc_lower and "column" not in desc_lower:
                # Truncate bullets to max 6
                if len(content.bullets) > 6:
                    content.bullets = content.bullets[:6]
                # Shorten long bullets
                content.bullets = [
                    b[:117] + "..." if len(b) > 120 else b for b in content.bullets
                ]

            elif "table" in desc_lower and "column" not in desc_lower:
                # Truncate table rows to max 8
                if content.table and len(content.table.rows) > 8:
                    content.table.rows = content.table.rows[:8]

            elif "left column" in desc_lower:
                if content.left_column:
                    if len(content.left_column.bullets) > 6:
                        content.left_column.bullets = content.left_column.bullets[:6]
                    content.left_column.bullets = [
                        b[:117] + "..." if len(b) > 120 else b
                        for b in content.left_column.bullets
                    ]

            elif "right column" in desc_lower:
                if content.right_column:
                    if len(content.right_column.bullets) > 6:
                        content.right_column.bullets = content.right_column.bullets[:6]
                    content.right_column.bullets = [
                        b[:117] + "..." if len(b) > 120 else b
                        for b in content.right_column.bullets
                    ]

        return deck

    async def _repair_slide(
        self, slide: SlideSpec, issues: list[CritiqueIssue]
    ) -> SlideSpec:
        """Use LLM to repair a single slide based on identified issues."""
        # Serialize current slide content
        slide_json = {
            "title": slide.title,
            "subtitle": slide.subtitle,
            "speaker_notes": slide.speaker_notes,
            "content": slide.content.model_dump(exclude_none=True),
        }

        issues_text = "\n".join(
            f"- [{issue.severity}] {issue.category}: {issue.description}"
            + (f" (Fix: {issue.fix_instruction})" if issue.fix_instruction else "")
            for issue in issues
        )

        user_prompt = f"""Fix the following issues in this slide:

Slide [{slide.id}] [{slide.layout.value}]:
Current content:
{json.dumps(slide_json, indent=2)}

Issues to fix:
{issues_text}

Return the corrected slide as JSON with: title, subtitle, speaker_notes, and content object.
Remember:
- Max 6 bullets, each max 120 chars
- Max 8 table rows
- Preserve data accuracy
- Only fix the identified issues
"""

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content or "{}"
        data = json.loads(raw)

        # Parse repaired slide
        title = data.get("title", slide.title)
        subtitle = data.get("subtitle", slide.subtitle)
        speaker_notes = data.get("speaker_notes", slide.speaker_notes)

        content_data = data.get("content", data)
        repaired_content = self._parse_repaired_content(content_data)

        return SlideSpec(
            id=slide.id,
            title=title,
            subtitle=subtitle,
            layout=slide.layout,
            content=repaired_content,
            speaker_notes=speaker_notes,
            emphasis=slide.emphasis,
        )

    def _parse_repaired_content(self, data: dict[str, Any]) -> SlideContent:
        """Parse repaired content from LLM response."""
        left_column = None
        right_column = None
        table = None
        kpis: list[KPICard] = []
        chart_data = None

        if "left_column" in data and data["left_column"]:
            lc = data["left_column"]
            left_column = ColumnContent(
                heading=lc.get("heading", ""),
                bullets=lc.get("bullets", []),
            )

        if "right_column" in data and data["right_column"]:
            rc = data["right_column"]
            right_column = ColumnContent(
                heading=rc.get("heading", ""),
                bullets=rc.get("bullets", []),
            )

        if "table" in data and data["table"]:
            t = data["table"]
            table = TableContent(
                headers=t.get("headers", []),
                rows=[[str(c) for c in row] for row in t.get("rows", [])],
            )

        if "kpis" in data and data["kpis"]:
            for card in data["kpis"]:
                kpis.append(
                    KPICard(
                        label=card.get("label", ""),
                        value=str(card.get("value", "")),
                        trend=card.get("trend", ""),
                    )
                )

        if "chart_data" in data and data["chart_data"]:
            c = data["chart_data"]
            series = [
                ChartSeries(name=s.get("name", ""), values=[float(v) for v in s.get("values", [])])
                for s in c.get("series", [])
            ]
            chart_data = ChartData(
                chart_type=c.get("chart_type", "bar"),
                labels=c.get("labels", []),
                series=series,
            )

        return SlideContent(
            bullets=data.get("bullets", []),
            left_column=left_column,
            right_column=right_column,
            table=table,
            kpis=kpis,
            chart_data=chart_data,
        )
