"""PPTGen supervisor — orchestrates Planner → Content → Designer → Critic → Repair."""
from __future__ import annotations

import logging
from typing import Any, Callable, Awaitable

from ..schemas import DeckSpec, DeckRequest, CritiqueResult
from .planner import PlannerAgent
from .content import ContentAgent
from .designer import DesignerAgent
from .critic import CriticAgent
from .repair import RepairAgent

logger = logging.getLogger(__name__)

MAX_REPAIR_ITERATIONS = 2

ProgressCallback = Callable[[str, str], Awaitable[None]]


class SupervisorAgent:
    def __init__(self, model: str, azure_endpoint: str, api_key: str):
        self.planner = PlannerAgent(model=model, azure_endpoint=azure_endpoint, api_key=api_key)
        self.content = ContentAgent(model=model, azure_endpoint=azure_endpoint, api_key=api_key)
        self.designer = DesignerAgent(model=model, azure_endpoint=azure_endpoint, api_key=api_key)
        self.critic = CriticAgent(model=model, azure_endpoint=azure_endpoint, api_key=api_key)
        self.repair = RepairAgent(model=model, azure_endpoint=azure_endpoint, api_key=api_key)

    async def generate(
        self,
        request: DeckRequest,
        data_context: dict[str, Any],
        on_progress: ProgressCallback | None = None,
    ) -> DeckSpec:
        logger.info("Supervisor: starting deck generation for template=%s", request.template)

        async def _progress(step: str, status: str):
            if on_progress:
                try:
                    await on_progress(step, status)
                except Exception:
                    pass

        await _progress("planner", "running")
        outline = await self.planner.plan(request, data_context)
        logger.info("Planner: created %d-slide outline", len(outline.slides))
        await _progress("planner", "done")

        await _progress("content", "running")
        try:
            filled = await self.content.write(outline, data_context)
            logger.info("Content: filled slide content")
        except Exception as e:
            logger.error("Content agent failed: %s — returning outline with empty content", e)
            filled = outline
        await _progress("content", "done")

        await _progress("designer", "running")
        try:
            designed = await self.designer.design(filled)
            logger.info("Designer: assigned layouts")
        except Exception as e:
            logger.error("Designer agent failed: %s — using pre-design deck", e)
            designed = filled
        await _progress("designer", "done")

        await _progress("critic", "running")
        try:
            critique = await self.critic.review(designed, request)
            logger.info("Critic: score=%d, pass=%s, issues=%d", critique.overall_score, critique.pass_threshold, len(critique.issues))
        except Exception as e:
            logger.error("Critic agent failed: %s — skipping review", e)
            critique = CritiqueResult(overall_score=7, pass_threshold=True, issues=[], suggestions=[])
        await _progress("critic", "done")

        for i in range(MAX_REPAIR_ITERATIONS):
            if critique.pass_threshold:
                break
            logger.info("Repair: iteration %d", i + 1)
            await _progress("repair", "running")
            try:
                designed = await self.repair.fix(designed, critique)
                critique = await self.critic.review(designed, request)
                logger.info("Critic (post-repair): score=%d, pass=%s", critique.overall_score, critique.pass_threshold)
            except Exception as e:
                logger.warning("Repair iteration %d failed: %s — using pre-repair deck", i + 1, e)
                break
        await _progress("repair", "done")

        return designed
