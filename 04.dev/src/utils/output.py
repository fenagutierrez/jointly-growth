"""
Shared output helpers for deep-dive scripts.
"""

import json
from typing import Any, Dict, List, Optional


def build_entity_metadata(
    *,
    entity_id: Optional[str] = None,
    entity_type: Optional[str] = None,
    primary_contact_name: Optional[str] = None,
    primary_license: Optional[str] = None,
    website: Optional[str] = None,
    brand_names: Optional[List[str]] = None,
    brokerage_affiliation: Optional[str] = None,
    source: Optional[str] = None,
    config: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    metadata = {
        "entity_id": entity_id,
        "entity_type": entity_type,
        "primary_contact_name": primary_contact_name,
        "primary_license": primary_license,
        "website": website,
        "brand_names": brand_names or [],
        "brokerage_affiliation": brokerage_affiliation,
        "source": source,
        "config": config,
    }

    if extra:
        metadata.update(extra)

    return metadata


def build_analysis_payload(
    entity_type: str,
    entity_name: str,
    roster: Dict[str, str],
    analysis: Dict[str, Any],
    warnings: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return {
        "entity": {
            "type": entity_type,
            "name": entity_name,
            "roster_size": len(roster),
        },
        "roster": roster,
        "summary": analysis.get("summary", {}),
        "revenue_share": analysis.get("revenue_share", {}),
        "top_producers": analysis.get("top_producers", {}),
        "warnings": warnings or [],
        "metadata": metadata or {},
    }


def print_json_payload(payload: Dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def print_analysis_summary(title: str, payload: Dict[str, Any], gci_label: str) -> None:
    summary = payload["summary"]
    revenue_share = payload["revenue_share"]
    top_producers = payload["top_producers"]

    print("\n" + "=" * 40)
    print(title)
    print("=" * 40)
    print(f"Roster Size: {summary['seat_count']} analyzed seats")
    print(f"Total Sides: {summary['total_sides']}")
    print(
        f"Sales: {summary['sales_sides']} sides "
        f"({summary['distribution']['sales']['buyer']} Buyer / {summary['distribution']['sales']['listing']} Listing) "
        f"| GCI: ${summary['sales_gci']:,.2f}"
    )
    print(
        f"Leases: {summary['lease_sides']} sides "
        f"({summary['distribution']['leases']['tenant']} Tenant / {summary['distribution']['leases']['listing']} Listing) "
        f"| GCI: ${summary['leases_gci']:,.2f}"
    )
    print(f"Total Estimated {gci_label} GCI: ${summary['total_gci']:,.2f}")

    print("\n--- Platform Revenue Potential ---")
    print(f"Estimated Monthly Subscription (MRR): ${summary['mrr_potential']:,.2f}")

    print("\n--- Potential Jointly Revenue Share ---")
    print(f"Lease Application Share: ${revenue_share['lease_application']:,.2f}")
    print(f"Concierge Share: ${revenue_share['concierge']:,.2f}")
    print(f"Total Share Opportunity: ${revenue_share['total']:,.2f}")

    print("\n--- Top 5 Sales Producers ---")
    for i, producer in enumerate(top_producers["sales"], 1):
        print(
            f"{i}. {producer['name']} ({producer['license']}): "
            f"{producer['units']} units (${producer['volume']:,.2f})"
        )

    print("\n--- Top 5 Lease Producers ---")
    for i, producer in enumerate(top_producers["leases"], 1):
        print(
            f"{i}. {producer['name']} ({producer['license']}): "
            f"{producer['units']} units (${producer['volume']:,.2f})"
        )

    if payload["warnings"]:
        print("\n--- Validation Warnings ---")
        for warning in payload["warnings"]:
            print(f"- {warning}")

    print("=" * 40)
