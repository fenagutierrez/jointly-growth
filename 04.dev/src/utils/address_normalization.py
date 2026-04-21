"""
Helpers for normalizing MLS address data and deduplicating cross-MLS transactions.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict

import pandas as pd


SUFFIX_MAP = {
    "avenue": "AVE",
    "ave": "AVE",
    "boulevard": "BLVD",
    "blvd": "BLVD",
    "circle": "CIR",
    "cir": "CIR",
    "court": "CT",
    "ct": "CT",
    "drive": "DR",
    "dr": "DR",
    "highway": "HWY",
    "hwy": "HWY",
    "lane": "LN",
    "ln": "LN",
    "loop": "LOOP",
    "parkway": "PKWY",
    "pkwy": "PKWY",
    "place": "PL",
    "pl": "PL",
    "road": "RD",
    "rd": "RD",
    "street": "ST",
    "st": "ST",
}

DIR_MAP = {
    "north": "N",
    "n": "N",
    "south": "S",
    "s": "S",
    "east": "E",
    "e": "E",
    "west": "W",
    "w": "W",
    "northeast": "NE",
    "ne": "NE",
    "northwest": "NW",
    "nw": "NW",
    "southeast": "SE",
    "se": "SE",
    "southwest": "SW",
    "sw": "SW",
}


def canonicalize_address(address: Any) -> str:
    """
    Build a canonical key from MLS address payloads.
    """
    parsed = _parse_address(address)
    if not parsed:
        return ""

    street_name, inferred_suffix = _normalize_street_name(parsed.get("streetName"))
    suffix = _normalize_suffix(parsed.get("streetSuffix")) or inferred_suffix

    parts = [
        _normalize_scalar(parsed.get("streetNumber")),
        street_name,
        suffix,
        _normalize_direction(parsed.get("streetDirPrefix")),
        _normalize_direction(parsed.get("streetDirSuffix")),
        _normalize_scalar(parsed.get("unitNumber")),
        _normalize_scalar(parsed.get("city")),
        _normalize_state(parsed.get("state")),
        _normalize_postal_code(parsed.get("postalCode")),
    ]
    return "|".join(parts)


def dedupe_cross_mls_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Deduplicate mirrored MLS transaction rows using a canonical address key.
    """
    if df.empty:
        return df.copy()

    required_columns = {"agent_license", "side", "close_date", "close_price", "address"}
    if not required_columns.issubset(df.columns):
        return df.copy()

    normalized = df.copy()
    normalized["canonical_address_key"] = normalized["address"].apply(canonicalize_address)

    group_columns = [
        "agent_license",
        "side",
        "close_date",
        "close_price",
        "canonical_address_key",
    ]

    sortable_columns = [col for col in ["mls_definition_id", "listing_id"] if col in normalized.columns]
    if sortable_columns:
        normalized = normalized.sort_values(sortable_columns, na_position="last")

    deduped = normalized.drop_duplicates(subset=group_columns, keep="first")
    return deduped.drop(columns=["canonical_address_key"])


def _parse_address(address: Any) -> Dict[str, Any]:
    if isinstance(address, dict):
        return address
    if isinstance(address, str):
        stripped = address.strip()
        if not stripped:
            return {}
        try:
            parsed = json.loads(stripped)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def _normalize_street_name(value: Any) -> tuple[str, str]:
    text = _normalize_scalar(value)
    if not text:
        return "", ""

    tokens = text.split()
    inferred_suffix = ""
    cleaned_tokens = []

    for token in tokens:
        mapped_suffix = SUFFIX_MAP.get(token)
        if mapped_suffix:
            inferred_suffix = inferred_suffix or mapped_suffix
            continue
        cleaned_tokens.append(token)

    return " ".join(cleaned_tokens), inferred_suffix


def _normalize_suffix(value: Any) -> str:
    text = _normalize_scalar(value)
    if not text:
        return ""
    return SUFFIX_MAP.get(text, text.upper())


def _normalize_direction(value: Any) -> str:
    text = _normalize_scalar(value)
    if not text:
        return ""
    return DIR_MAP.get(text, text.upper())


def _normalize_state(value: Any) -> str:
    text = _normalize_scalar(value)
    return text.upper() if text else ""


def _normalize_postal_code(value: Any) -> str:
    text = _normalize_scalar(value)
    return re.sub(r"[^0-9]", "", text)


def _normalize_scalar(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip().lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
