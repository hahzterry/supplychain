"""Overflow checker for slide content.

Validates that slide content does not exceed PowerPoint rendering limits.
Returns a list of CritiqueIssue for any overflow violations found.
"""

from __future__ import annotations

from ..schemas.critique_spec import CritiqueIssue
from ..schemas.slide_spec import SlideSpec

# Overflow thresholds
MAX_BULLETS = 6
MAX_BULLET_LENGTH = 120
MAX_TABLE_ROWS = 8


def check_overflow(slides: list[SlideSpec]) -> list[CritiqueIssue]:
    """Check all slides for content overflow issues.

    Args:
        slides: List of SlideSpec objects to validate.

    Returns:
        List of CritiqueIssue for any overflow violations.
    """
    issues: list[CritiqueIssue] = []

    for slide in slides:
        issues.extend(_check_slide(slide))

    return issues


def _check_slide(slide: SlideSpec) -> list[CritiqueIssue]:
    """Check a single slide for overflow issues."""
    issues: list[CritiqueIssue] = []
    content = slide.content
    sid = slide.id

    # Check bullet count
    if len(content.bullets) > MAX_BULLETS:
        issues.append(
            CritiqueIssue(
                slide_id=sid,
                severity="error",
                category="overflow",
                description=(
                    f"Slide has {len(content.bullets)} bullets (max {MAX_BULLETS}). "
                    "Content will overflow the slide area."
                ),
                fix_instruction=f"Reduce to {MAX_BULLETS} bullets or split across multiple slides.",
            )
        )

    # Check bullet text length
    for i, bullet in enumerate(content.bullets, 1):
        if len(bullet) > MAX_BULLET_LENGTH:
            issues.append(
                CritiqueIssue(
                    slide_id=sid,
                    severity="warning",
                    category="overflow",
                    description=(
                        f"Bullet {i} is {len(bullet)} chars (max {MAX_BULLET_LENGTH}): "
                        f'"{bullet[:50]}..."'
                    ),
                    fix_instruction="Shorten the bullet text or split into two bullets.",
                )
            )

    # Check table row count
    if content.table and len(content.table.rows) > MAX_TABLE_ROWS:
        issues.append(
            CritiqueIssue(
                slide_id=sid,
                severity="error",
                category="overflow",
                description=(
                    f"Table has {len(content.table.rows)} rows (max {MAX_TABLE_ROWS}). "
                    "Content will overflow the slide area."
                ),
                fix_instruction=f"Reduce to {MAX_TABLE_ROWS} rows or split into multiple slides.",
            )
        )

    # Check columns for bullet overflow
    for col_name, col in [("left", content.left_column), ("right", content.right_column)]:
        if col is None:
            continue
        if len(col.bullets) > MAX_BULLETS:
            issues.append(
                CritiqueIssue(
                    slide_id=sid,
                    severity="error",
                    category="overflow",
                    description=f"{col_name.title()} column has {len(col.bullets)} bullets (max {MAX_BULLETS}).",
                    fix_instruction=f"Reduce {col_name} column to {MAX_BULLETS} bullets.",
                )
            )
        for i, bullet in enumerate(col.bullets, 1):
            if len(bullet) > MAX_BULLET_LENGTH:
                issues.append(
                    CritiqueIssue(
                        slide_id=sid,
                        severity="warning",
                        category="overflow",
                        description=(
                            f"{col_name.title()} column bullet {i} is {len(bullet)} chars "
                            f"(max {MAX_BULLET_LENGTH})."
                        ),
                        fix_instruction="Shorten the bullet text.",
                    )
                )

    return issues
