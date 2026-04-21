"""
Shared production analysis helpers for brokerage and team deep dives.
"""

from typing import Any, Dict, List

import pandas as pd

from src.utils.address_normalization import dedupe_cross_mls_transactions
from src.utils.pricing import calculate_jointly_business_mrr


LEASE_APPLICATION_SHARE = 28.0
CONCIERGE_OPT_IN_RATE = 0.30
CONCIERGE_SHARE_AMOUNT = 42.0
LEASE_PROPERTY_TYPES = ["RR", "RL"]


def analyze_roster_production(df: pd.DataFrame, roster: Dict[str, str]) -> Dict[str, Any]:
    """
    Calculate production, pricing, and revenue-share metrics for a roster.
    """
    if not roster:
        return {}

    seat_count = len(roster)
    mrr = calculate_jointly_business_mrr(seat_count)

    if df.empty:
        return {
            "summary": {
                "total_sides": 0,
                "seat_count": seat_count,
                "mrr_potential": mrr,
                "sales_sides": 0,
                "lease_sides": 0,
                "sales_gci": 0.0,
                "leases_gci": 0.0,
                "total_gci": 0.0,
                "distribution": {
                    "sales": {"buyer": 0, "listing": 0},
                    "leases": {"tenant": 0, "listing": 0},
                },
            },
            "revenue_share": {
                "lease_application": 0.0,
                "concierge": 0.0,
                "total": 0.0,
            },
            "top_producers": {"sales": [], "leases": []},
        }

    df = dedupe_cross_mls_transactions(df)

    lease_mask = df["property_type"].str.contains("Lease", case=False, na=False) | df[
        "property_type"
    ].isin(LEASE_PROPERTY_TYPES)

    sales_df = df[~lease_mask]
    leases_df = df[lease_mask]

    sales_gci = (sales_df["close_price"] * 0.03).sum()
    leases_gci = (leases_df["close_price"] * 0.50).sum()

    buyer_sides = len(sales_df[sales_df["side"] == "buyer"])
    listing_sides = len(sales_df[sales_df["side"] == "listing"])
    tenant_sides = len(leases_df[leases_df["side"] == "buyer"])
    lease_listing_sides = len(leases_df[leases_df["side"] == "listing"])

    lease_app_share = lease_listing_sides * LEASE_APPLICATION_SHARE
    concierge_share = (
        buyer_sides + tenant_sides
    ) * CONCIERGE_OPT_IN_RATE * CONCIERGE_SHARE_AMOUNT

    return {
        "summary": {
            "total_sides": len(df),
            "seat_count": seat_count,
            "mrr_potential": mrr,
            "sales_sides": len(sales_df),
            "lease_sides": len(leases_df),
            "sales_gci": float(sales_gci),
            "leases_gci": float(leases_gci),
            "total_gci": float(sales_gci + leases_gci),
            "distribution": {
                "sales": {"buyer": buyer_sides, "listing": listing_sides},
                "leases": {"tenant": tenant_sides, "listing": lease_listing_sides},
            },
        },
        "revenue_share": {
            "lease_application": float(lease_app_share),
            "concierge": float(concierge_share),
            "total": float(lease_app_share + concierge_share),
        },
        "top_producers": {
            "sales": _get_top_5(sales_df, roster),
            "leases": _get_top_5(leases_df, roster),
        },
    }


def _get_top_5(data_df: pd.DataFrame, roster: Dict[str, str]) -> List[Dict[str, Any]]:
    if data_df.empty:
        return []

    agent_stats = data_df.groupby("agent_license").agg({"close_price": ["count", "sum"]})
    agent_stats.columns = ["units", "volume"]
    agent_stats = agent_stats.sort_values(by="units", ascending=False).head(5)

    top_list = []
    for lic, row in agent_stats.iterrows():
        name = roster.get(str(lic), f"Unknown ({lic})")
        top_list.append(
            {
                "name": name,
                "license": lic,
                "units": int(row["units"]),
                "volume": float(row["volume"]),
            }
        )
    return top_list
