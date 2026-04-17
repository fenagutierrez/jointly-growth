"""
Shared pricing helpers for Jointly Business revenue calculations.
"""


def calculate_jointly_business_mrr(seat_count: int) -> float:
    """
    Calculate monthly recurring revenue for Jointly Business based on seat count.

    Pricing tiers:
    - Base: $249 (includes 5 seats)
    - Seats 6-25: $25/seat
    - Seats 26-49: $15/seat
    - Seats 50-99: $10/seat
    - Seats 100+: $5/seat
    """
    if seat_count < 0:
        raise ValueError("seat_count cannot be negative")

    mrr = 249.0
    if seat_count <= 5:
        return mrr

    if seat_count <= 25:
        return mrr + (seat_count - 5) * 25

    if seat_count <= 49:
        return mrr + (20 * 25) + (seat_count - 25) * 15

    if seat_count <= 99:
        return mrr + (20 * 25) + (24 * 15) + (seat_count - 49) * 10

    return mrr + (20 * 25) + (24 * 15) + (50 * 10) + (seat_count - 99) * 5
