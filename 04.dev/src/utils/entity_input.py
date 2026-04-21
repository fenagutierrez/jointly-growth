"""
Helpers for loading and merging structured entity input metadata.
"""

import json
from typing import Any, Dict, Optional


def load_entity_input(path: Optional[str]) -> Dict[str, Any]:
    """Load a JSON object from disk for entity metadata input."""
    if not path:
        return {}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("Entity input file must contain a JSON object")

    return data


def merge_entity_input(file_data: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge file-provided entity metadata with CLI overrides.

    Non-empty override values win over file data.
    """
    merged = dict(file_data)
    for key, value in overrides.items():
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        if isinstance(value, list) and len(value) == 0:
            continue
        merged[key] = value
    return merged
