#!/usr/bin/env python3
"""
Jointly Business MRR Calculator (Official March 2026 Logic)
Calculates the Monthly Recurring Revenue (MRR) for a brokerage based on 
the official tiered pricing structure.
"""

def calculate_mrr(total_seats):
    """
    Calculates MRR based on tiered pricing structure:
    - Base Fee: $249.00 (Includes first 5 seats)
    - Tier 2 (6-25): $25.00/seat
    - Tier 3 (26-49): $15.00/seat
    - Tier 4 (50-99): $10.00/seat
    - Tier 5 (100+): $5.00/seat
    """
    if total_seats <= 0:
        return 0.0
    
    mrr = 249.0  # Base platform fee (includes seats 1-5)
    
    # Tier 2: Seats 6-25 (max 20 additional seats)
    if total_seats >= 6:
        tier2_seats = min(total_seats, 25) - 5
        mrr += tier2_seats * 25.0
        
    # Tier 3: Seats 26-49 (max 24 additional seats)
    if total_seats >= 26:
        tier3_seats = min(total_seats, 49) - 25
        mrr += tier3_seats * 15.0
        
    # Tier 4: Seats 50-99 (max 50 additional seats)
    if total_seats >= 50:
        tier4_seats = min(total_seats, 99) - 49
        mrr += tier4_seats * 10.0
        
    # Tier 5: Seats 100+ (all remaining seats)
    if total_seats >= 100:
        tier5_seats = total_seats - 99
        mrr += tier5_seats * 5.0
        
    return mrr

def main():
    import sys
    if len(sys.argv) > 1:
        try:
            seats = int(sys.argv[1])
            mrr = calculate_mrr(seats)
            print(f"MRR for {seats} seats: ${mrr:,.2f}")
        except ValueError:
            print("Please provide a valid integer for total seats.")
    else:
        # Standard test cases from documentation
        test_cases = [1, 5, 25, 49, 99, 650]
        print("Jointly Business MRR Calculation Tests:")
        for seats in test_cases:
            mrr = calculate_mrr(seats)
            print(f" - {seats} seats: ${mrr:,.2f}")

if __name__ == "__main__":
    main()
