"""ReportSupervisor - Routes report generation by format."""
from __future__ import annotations

import logging
from typing import Any, Callable, Optional

from ..schemas import (
    DocSpec,
    ReportFormat,
    ReportRequest,
    SheetSpec,
)
from .doc_planner import DocPlanner
from .doc_content import DocContentWriter
from .sheet_content import SheetContentGenerator

logger = logging.getLogger(__name__)


class ReportSupervisor:
    """
    Top-level orchestrator for report generation.

    Routes by format:
      - DOCX/PDF -> DocPlanner -> DocContentWriter (2-agent LLM pipeline)
      - XLSX -> SheetContentGenerator (deterministic, no LLM)
    """

    def __init__(
        self,
        model: str,
        azure_endpoint: str,
        api_key: str,
    ) -> None:
        self.model = model
        self.azure_endpoint = azure_endpoint
        self.api_key = api_key

        # Initialize sub-agents
        self._doc_planner = DocPlanner(
            model=model,
            azure_endpoint=azure_endpoint,
            api_key=api_key,
        )
        self._doc_writer = DocContentWriter(
            model=model,
            azure_endpoint=azure_endpoint,
            api_key=api_key,
        )
        self._sheet_generator = SheetContentGenerator()

    async def generate(
        self,
        request: ReportRequest,
        data_context: dict[str, Any],
        on_progress: Optional[Callable[[str, float], None]] = None,
    ) -> DocSpec | SheetSpec:
        """
        Generate a report based on the request format.

        Args:
            request: The report request with template, format, etc.
            data_context: Supply chain data (kpis, inventory, forecasts, etc.)
            on_progress: Optional callback(stage_name, pct) for UI streaming.

        Returns:
            DocSpec for DOCX/PDF, SheetSpec for XLSX.
        """
        fmt = request.format

        if fmt in (ReportFormat.DOCX, ReportFormat.PDF):
            return await self._generate_document(request, data_context, on_progress)
        elif fmt == ReportFormat.XLSX:
            return await self._generate_spreadsheet(request, data_context, on_progress)
        elif fmt == ReportFormat.PPTX:
            raise ValueError(
                "PPTX generation is handled by the pptgen pipeline, not reportgen."
            )
        else:
            raise ValueError(f"Unsupported report format: {fmt}")

    async def _generate_document(
        self,
        request: ReportRequest,
        data_context: dict[str, Any],
        on_progress: Optional[Callable[[str, float], None]] = None,
    ) -> DocSpec:
        """Two-agent LLM pipeline: DocPlanner -> DocContentWriter."""

        # Stage 1: Plan the document structure
        if on_progress:
            on_progress("planning", 0.1)

        logger.info(f"[ReportSupervisor] Planning document: template={request.template}")
        doc_plan = await self._doc_planner.plan(
            template=request.template,
            focus_area=request.focus_area,
            audience=request.audience,
            data_context=data_context,
        )

        if on_progress:
            on_progress("planning_complete", 0.3)

        # Stage 2: Fill sections with content
        if on_progress:
            on_progress("writing_content", 0.4)

        logger.info(
            f"[ReportSupervisor] Writing content for {len(doc_plan.sections)} sections"
        )
        doc_spec = await self._doc_writer.write(
            doc_plan=doc_plan,
            data_context=data_context,
            audience=request.audience,
        )

        if on_progress:
            on_progress("complete", 1.0)

        return doc_spec

    async def _generate_spreadsheet(
        self,
        request: ReportRequest,
        data_context: dict[str, Any],
        on_progress: Optional[Callable[[str, float], None]] = None,
    ) -> SheetSpec:
        """Deterministic spreadsheet generation (no LLM)."""

        if on_progress:
            on_progress("generating_spreadsheet", 0.2)

        logger.info(
            f"[ReportSupervisor] Generating spreadsheet: template={request.template}"
        )
        sheet_spec = self._sheet_generator.generate(
            template=request.template,
            data_context=data_context,
        )

        if on_progress:
            on_progress("complete", 1.0)

        return sheet_spec
