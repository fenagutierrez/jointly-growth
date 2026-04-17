import csv
import requests
import time

def fetch_trec_data(license_number):
    """Fetches DBA and Team Names from the TREC background API."""
    url = f"https://www.trec.texas.gov/acaif/api/licenseDetail/{license_number}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # The API returns a list of results
            if isinstance(data, list) and len(data) > 0:
                detail = data[0]
                dbas = ", ".join(detail.get("dbas", []))
                teams = ", ".join(detail.get("teamNames", []))
                return dbas, teams
    except Exception as e:
        print(f"Error fetching {license_number}: {e}")
    return "", ""

def process_csv(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    for row in rows:
        # Check if we need to enrich (DBAs or Team Names might be empty)
        # We'll re-run for all to be sure
        print(f"Enriching: {row['Company Name']} ({row['License Number']})")
        dbas, teams = fetch_trec_data(row['License Number'])
        row["DBAs"] = dbas
        row["Team Names"] = teams
        time.sleep(0.5) # Polite delay

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) > 2:
        process_csv(sys.argv[1], sys.argv[2])
    else:
        INPUT = "00.companies/brokerages/output/summaries/top_100_active_brokerages_march_2026.csv"
        process_csv(INPUT, INPUT)
