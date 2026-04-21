"""
Shared roster normalization helpers.
"""

from typing import Dict, Iterable, List, Tuple


def normalize_license(value: object) -> str:
    """Normalize a license-like value to digits without leading zeroes."""
    return "".join(filter(str.isdigit, str(value))).lstrip("0")


def normalize_license_list(licenses: Iterable[object]) -> List[str]:
    """Normalize a sequence of licenses and preserve order while removing duplicates."""
    normalized = []
    seen = set()

    for lic in licenses:
        cleaned = normalize_license(lic)
        if cleaned and cleaned not in seen:
            normalized.append(cleaned)
            seen.add(cleaned)

    return normalized


def normalize_roster(roster: Dict[object, object]) -> Tuple[Dict[str, str], List[str]]:
    """Normalize roster license keys and collect validation warnings."""
    normalized = {}
    warnings = []

    for raw_license, raw_name in roster.items():
        cleaned_license = normalize_license(raw_license)
        cleaned_name = str(raw_name).strip() if raw_name is not None else ""

        if not cleaned_license:
            warnings.append(f"Skipped roster entry with invalid license: {raw_license!r}")
            continue

        if not cleaned_name:
            cleaned_name = f"Agent {cleaned_license}"
            warnings.append(f"Filled missing roster name for license {cleaned_license}")

        if cleaned_license in normalized and normalized[cleaned_license] != cleaned_name:
            warnings.append(
                f"Duplicate license {cleaned_license} kept as {normalized[cleaned_license]!r}, ignored {cleaned_name!r}"
            )
            continue

        normalized[cleaned_license] = cleaned_name

    return normalized, warnings
