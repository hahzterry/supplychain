"""Normalize fuzzy LLM category names to valid enum values."""
from __future__ import annotations

import difflib

VALID_CATEGORIES = ["Landing Gear", "Actuation Systems", "Hydraulics", "Structures", "MRO Parts", "Raw Materials", "Fasteners & Seals"]

CATEGORY_ALIASES: dict[str, str | None] = {
    "landing gear": "Landing Gear",
    "lg": "Landing Gear",
    "main landing gear": "Landing Gear",
    "nose landing gear": "Landing Gear",
    "mlg": "Landing Gear",
    "nlg": "Landing Gear",
    "gear": "Landing Gear",
    "undercarriage": "Landing Gear",
    "actuation": "Actuation Systems",
    "actuators": "Actuation Systems",
    "actuator": "Actuation Systems",
    "flight controls": "Actuation Systems",
    "flight control actuators": "Actuation Systems",
    "flap actuators": "Actuation Systems",
    "hydraulic": "Hydraulics",
    "hydraulic systems": "Hydraulics",
    "hydraulic components": "Hydraulics",
    "brake hydraulics": "Hydraulics",
    "servo valves": "Hydraulics",
    "cylinders": "Hydraulics",
    "structural": "Structures",
    "structure": "Structures",
    "forgings": "Structures",
    "castings": "Structures",
    "machined parts": "Structures",
    "fittings": "Structures",
    "mro": "MRO Parts",
    "maintenance": "MRO Parts",
    "overhaul": "MRO Parts",
    "repair": "MRO Parts",
    "spare parts": "MRO Parts",
    "spares": "MRO Parts",
    "consumables": "MRO Parts",
    "seals": "MRO Parts",
    "bearings": "MRO Parts",
    "raw material": "Raw Materials",
    "raw materials": "Raw Materials",
    "material": "Raw Materials",
    "titanium": "Raw Materials",
    "steel": "Raw Materials",
    "aluminum": "Raw Materials",
    "inconel": "Raw Materials",
    "bar stock": "Raw Materials",
    "billet": "Raw Materials",
    "plate": "Raw Materials",
    "fasteners": "Fasteners & Seals",
    "fastener": "Fasteners & Seals",
    "bolts": "Fasteners & Seals",
    "nuts": "Fasteners & Seals",
    "o-rings": "Fasteners & Seals",
    "seals and fasteners": "Fasteners & Seals",
    "hardware": "Fasteners & Seals",
    "electronics": None,
    "avionics": None,
    "engines": None,
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
    """Split compound category strings like 'Landing Gear and Hydraulics'."""
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
