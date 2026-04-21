import unittest

import pandas as pd

from src.utils.address_normalization import (
    canonicalize_address,
    dedupe_cross_mls_transactions,
)
from src.utils.pricing import calculate_jointly_business_mrr
from src.utils.production_analysis import analyze_roster_production
from src.utils.entity_input import merge_entity_input
from src.utils.output import build_entity_metadata


class PricingTests(unittest.TestCase):
    def test_pricing_boundaries(self):
        cases = {
            0: 249.0,
            5: 249.0,
            6: 274.0,
            25: 749.0,
            26: 764.0,
            49: 1109.0,
            50: 1119.0,
            99: 1609.0,
            100: 1614.0,
        }

        for seat_count, expected in cases.items():
            with self.subTest(seat_count=seat_count):
                self.assertEqual(calculate_jointly_business_mrr(seat_count), expected)

    def test_negative_seat_count_raises(self):
        with self.assertRaises(ValueError):
            calculate_jointly_business_mrr(-1)


class ProductionAnalysisTests(unittest.TestCase):
    def test_empty_roster_returns_empty_result(self):
        result = analyze_roster_production(pd.DataFrame(), {})
        self.assertEqual(result, {})

    def test_empty_dataframe_still_returns_pricing_summary(self):
        roster = {"101": "Alice", "202": "Bob"}

        result = analyze_roster_production(pd.DataFrame(), roster)

        self.assertEqual(result["summary"]["seat_count"], 2)
        self.assertEqual(result["summary"]["mrr_potential"], 249.0)
        self.assertEqual(result["summary"]["total_sides"], 0)
        self.assertEqual(result["revenue_share"]["total"], 0.0)
        self.assertEqual(result["top_producers"]["sales"], [])
        self.assertEqual(result["top_producers"]["leases"], [])

    def test_mixed_sales_and_leases_analysis(self):
        roster = {
            "101": "Alice",
            "202": "Bob",
            "303": "Cara",
            "404": "Drew",
            "505": "Evan",
            "606": "Fern",
        }
        df = pd.DataFrame(
            [
                {"agent_license": "101", "side": "buyer", "close_price": 100000.0, "property_type": "Residential"},
                {"agent_license": "101", "side": "listing", "close_price": 200000.0, "property_type": "Residential"},
                {"agent_license": "202", "side": "buyer", "close_price": 300000.0, "property_type": "Condo"},
                {"agent_license": "202", "side": "listing", "close_price": 1500.0, "property_type": "Lease"},
                {"agent_license": "303", "side": "buyer", "close_price": 1200.0, "property_type": "RR"},
                {"agent_license": "404", "side": "listing", "close_price": 900.0, "property_type": "RL"},
                {"agent_license": "505", "side": "listing", "close_price": 250000.0, "property_type": "Residential"},
                {"agent_license": "505", "side": "buyer", "close_price": 260000.0, "property_type": "Residential"},
                {"agent_license": "606", "side": "buyer", "close_price": 110000.0, "property_type": "Residential"},
            ]
        )

        result = analyze_roster_production(df, roster)

        self.assertEqual(result["summary"]["seat_count"], 6)
        self.assertEqual(result["summary"]["mrr_potential"], 274.0)
        self.assertEqual(result["summary"]["total_sides"], 9)
        self.assertEqual(result["summary"]["sales_sides"], 6)
        self.assertEqual(result["summary"]["lease_sides"], 3)
        self.assertEqual(result["summary"]["distribution"]["sales"]["buyer"], 4)
        self.assertEqual(result["summary"]["distribution"]["sales"]["listing"], 2)
        self.assertEqual(result["summary"]["distribution"]["leases"]["tenant"], 1)
        self.assertEqual(result["summary"]["distribution"]["leases"]["listing"], 2)
        self.assertAlmostEqual(result["summary"]["sales_gci"], 36600.0)
        self.assertAlmostEqual(result["summary"]["leases_gci"], 1800.0)
        self.assertAlmostEqual(result["summary"]["total_gci"], 38400.0)
        self.assertAlmostEqual(result["revenue_share"]["lease_application"], 56.0)
        self.assertAlmostEqual(result["revenue_share"]["concierge"], 63.0)
        self.assertAlmostEqual(result["revenue_share"]["total"], 119.0)

        self.assertEqual(result["top_producers"]["sales"][0]["name"], "Alice")
        self.assertEqual(result["top_producers"]["sales"][0]["units"], 2)
        self.assertEqual(result["top_producers"]["leases"][0]["name"], "Bob")
        self.assertEqual(result["top_producers"]["leases"][0]["units"], 1)

    def test_cross_mls_duplicates_are_deduped_before_analysis(self):
        roster = {"770612": "Amy Kirk"}
        df = pd.DataFrame(
            [
                {
                    "agent_license": "770612",
                    "mls_definition_id": "752",
                    "listing_id": "21023666",
                    "side": "listing",
                    "list_price": 619000.0,
                    "close_price": 605000.0,
                    "property_type": "Residential",
                    "close_date": "2025-10-03",
                    "address": {
                        "streetNumber": "1626",
                        "streetName": "Eagle Bluff",
                        "streetSuffix": "Drive",
                        "city": "Troy",
                        "state": "TX",
                        "postalCode": "76579",
                    },
                },
                {
                    "agent_license": "770612",
                    "mls_definition_id": "765",
                    "listing_id": "588579",
                    "side": "listing",
                    "list_price": 619000.0,
                    "close_price": 605000.0,
                    "property_type": "Residential",
                    "close_date": "2025-10-03",
                    "address": {
                        "streetNumber": "1626",
                        "streetName": "Eagle Bluff",
                        "streetSuffix": "DR",
                        "city": "Troy",
                        "state": "TX",
                        "postalCode": "76579",
                    },
                },
                {
                    "agent_license": "770612",
                    "mls_definition_id": "787",
                    "listing_id": "5071419",
                    "side": "listing",
                    "list_price": 619000.0,
                    "close_price": 605000.0,
                    "property_type": "Commercial",
                    "close_date": "2025-10-03",
                    "address": {
                        "streetNumber": "1626",
                        "streetName": "Eagle Bluff DR",
                        "streetSuffix": None,
                        "city": "Troy",
                        "state": "TX",
                        "postalCode": "76579",
                    },
                },
            ]
        )

        result = analyze_roster_production(df, roster)

        self.assertEqual(result["summary"]["total_sides"], 1)
        self.assertEqual(result["summary"]["sales_sides"], 1)
        self.assertAlmostEqual(result["summary"]["sales_gci"], 18150.0)


class AddressNormalizationTests(unittest.TestCase):
    def test_canonicalize_address_handles_suffix_and_name_variants(self):
        variants = [
            {
                "streetNumber": "1626",
                "streetName": "Eagle Bluff",
                "streetSuffix": "Drive",
                "city": "Troy",
                "state": "TX",
                "postalCode": "76579",
            },
            {
                "streetNumber": "1626",
                "streetName": "Eagle Bluff",
                "streetSuffix": "DR",
                "city": "Troy",
                "state": "TX",
                "postalCode": "76579",
            },
            {
                "streetNumber": "1626",
                "streetName": "Eagle Bluff DR",
                "streetSuffix": None,
                "city": "Troy",
                "state": "TX",
                "postalCode": "76579",
            },
        ]

        keys = {canonicalize_address(address) for address in variants}
        self.assertEqual(keys, {"1626|eagle bluff|DR||||troy|TX|76579"})

    def test_canonicalize_address_infers_highway_suffix_from_street_name(self):
        variants = [
            {
                "streetNumber": "16597",
                "streetName": "Old HWY 81",
                "streetSuffix": "Highway",
                "city": "Troy",
                "state": "TX",
                "postalCode": "76579",
            },
            {
                "streetNumber": "16597",
                "streetName": "Old 81",
                "streetSuffix": "HWY",
                "city": "Troy",
                "state": "TX",
                "postalCode": "76579",
            },
            {
                "streetNumber": "16597",
                "streetName": "Old Hwy 81",
                "streetSuffix": None,
                "city": "Troy",
                "state": "TX",
                "postalCode": "76579",
            },
        ]

        keys = {canonicalize_address(address) for address in variants}
        self.assertEqual(keys, {"16597|old 81|HWY||||troy|TX|76579"})

    def test_dedupe_cross_mls_transactions_uses_canonical_address(self):
        df = pd.DataFrame(
            [
                {
                    "agent_license": "770612",
                    "side": "listing",
                    "close_date": "2025-06-30",
                    "close_price": 429000.0,
                    "property_type": "Residential",
                    "mls_definition_id": "765",
                    "listing_id": "575537",
                    "address": {
                        "streetNumber": "16597",
                        "streetName": "Old 81",
                        "streetSuffix": "Hwy",
                        "city": "Troy",
                        "state": "TX",
                        "postalCode": "76579",
                    },
                },
                {
                    "agent_license": "770612",
                    "side": "listing",
                    "close_date": "2025-06-30",
                    "close_price": 429000.0,
                    "property_type": "Residential",
                    "mls_definition_id": "752",
                    "listing_id": "229432",
                    "address": {
                        "streetNumber": "16597",
                        "streetName": "Old HWY 81",
                        "streetSuffix": "Highway",
                        "city": "Troy",
                        "state": "TX",
                        "postalCode": "76579",
                    },
                },
                {
                    "agent_license": "770612",
                    "side": "listing",
                    "close_date": "2025-06-30",
                    "close_price": 429000.0,
                    "property_type": "Land",
                    "mls_definition_id": "787",
                    "listing_id": "8011933",
                    "address": {
                        "streetNumber": "16597",
                        "streetName": "Old Hwy 81",
                        "streetSuffix": None,
                        "city": "Troy",
                        "state": "TX",
                        "postalCode": "76579",
                    },
                },
            ]
        )

        deduped = dedupe_cross_mls_transactions(df)

        self.assertEqual(len(deduped), 1)
        self.assertEqual(deduped.iloc[0]["mls_definition_id"], "752")


class OutputMetadataTests(unittest.TestCase):
    def test_build_entity_metadata_returns_shared_schema(self):
        metadata = build_entity_metadata(
            entity_id="12345",
            entity_type="brokerage",
            primary_contact_name="Jane Broker",
            primary_license="12345",
            website=None,
            brand_names=["Acme Realty"],
            brokerage_affiliation=None,
            source="trec_api",
            config="janet.ini",
            extra={"team_names": ["Alpha Team"]},
        )

        self.assertEqual(
            set(metadata.keys()),
            {
                "entity_id",
                "entity_type",
                "primary_contact_name",
                "primary_license",
                "website",
                "brand_names",
                "brokerage_affiliation",
                "source",
                "config",
                "team_names",
            },
        )
        self.assertEqual(metadata["entity_type"], "brokerage")
        self.assertEqual(metadata["brand_names"], ["Acme Realty"])

    def test_merge_entity_input_prefers_cli_overrides(self):
        merged = merge_entity_input(
            {
                "team_name": "File Team",
                "team_lead_name": "File Lead",
                "brand_names": ["File Brand"],
            },
            {
                "team_name": "CLI Team",
                "team_lead_name": None,
                "brand_names": ["CLI Brand"],
                "website": "https://example.com",
            },
        )

        self.assertEqual(merged["team_name"], "CLI Team")
        self.assertEqual(merged["team_lead_name"], "File Lead")
        self.assertEqual(merged["brand_names"], ["CLI Brand"])
        self.assertEqual(merged["website"], "https://example.com")


if __name__ == "__main__":
    unittest.main()
