"""Normalize fuzzy LLM category names to valid enum values."""
from __future__ import annotations

import difflib

VALID_CATEGORIES = ["Flour", "Pasta", "Cooking Oil", "Animal Feed", "Rice", "Sugar", "Specialty"]

CATEGORY_ALIASES: dict[str, str | None] = {
    "oil": "Cooking Oil",
    "oils": "Cooking Oil",
    "oils and fats": "Cooking Oil",
    "cooking oils": "Cooking Oil",
    "sunflower oil": "Cooking Oil",
    "vegetable oil": "Cooking Oil",
    "edible oil": "Cooking Oil",
    "edible oils": "Cooking Oil",
    "fats": "Cooking Oil",
    "feed": "Animal Feed",
    "animal feeds": "Animal Feed",
    "poultry feed": "Animal Feed",
    "cattle feed": "Animal Feed",
    "livestock": "Animal Feed",
    "livestock feed": "Animal Feed",
    "wheat": "Flour",
    "wheat flour": "Flour",
    "bread flour": "Flour",
    "atta": "Flour",
    "semolina": "Flour",
    "grains": "Flour",
    "grain": "Flour",
    "cereals": "Flour",
    "noodles": "Pasta",
    "macaroni": "Pasta",
    "spaghetti": "Pasta",
    "pasta products": "Pasta",
    "rice products": "Rice",
    "basmati": "Rice",
    "basmati rice": "Rice",
    "sugar products": "Sugar",
    "sweeteners": "Sugar",
    "specialty items": "Specialty",
    "premix": "Specialty",
    "mixes": "Specialty",
    "baking": "Specialty",
    "baking mixes": "Specialty",
    "dairy": None,
    "beverages": None,
    "frozen": None,
}

_VALID_LOWER = [v.lower() for v in VALID_CATEGORIES]


def normalize_categories(raw_categories: list) -> list[str]:
    """Normalize LLM category names to valid enum values."""
    if not raw_categories:
        return []

    normalized: set[str] = set()

    for raw in raw_categories:
        if not isinstance(raw, str) or not raw.strip():
            continue

        parts = _split_compound(raw.strip())

        for part in parts:
            matched = _match_single(part.strip())
            if matched:
                normalized.add(matched)

    return list(normalized)


def _split_compound(text: str) -> list[str]:
    """Split compound category strings like 'Flour and Sugar' or 'Flour, Pasta'."""
    for sep in [" and ", " & ", ",", ";", "/"]:
        if sep in text:
            return [p.strip() for p in text.split(sep) if p.strip()]
    return [text]


def _match_single(part: str) -> str | None:
    """Match a single category name to a valid enum value."""
    part_lower = part.lower()

    # Direct match
    for i, valid_lower in enumerate(_VALID_LOWER):
        if part_lower == valid_lower:
            return VALID_CATEGORIES[i]

    # Alias lookup
    if part_lower in CATEGORY_ALIASES:
        return CATEGORY_ALIASES[part_lower]

    # Fuzzy match
    matches = difflib.get_close_matches(part_lower, _VALID_LOWER, n=1, cutoff=0.6)
    if matches:
        idx = _VALID_LOWER.index(matches[0])
        return VALID_CATEGORIES[idx]

    return None
