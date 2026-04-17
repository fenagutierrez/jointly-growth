#!/usr/bin/env python3
import requests
import sys

def fetch_trec_data(license_number):
    """Fetches full details including DBA, Team Names, Designated Broker, and Sales Agents."""
    url = f"https://www.trec.texas.gov/acaif/api/licenseDetail/{license_number}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
    }
    
    result = {
        "dbas": [],
        "teams": [],
        "designated_broker": "None",
        "sales_agents": []
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                detail = data[0]
                result["dbas"] = detail.get("dbas", [])
                result["teams"] = detail.get("teamNames", [])
                
                sponsoring = detail.get("sponsoringData", {})
                if isinstance(sponsoring, dict):
                    sponsored_licenses = [v["sponsorLicenseNumber"] for v in sponsoring.values() if "sponsorLicenseNumber" in v]
                    
                    for i, lic in enumerate(sponsored_licenses, 1):
                        # Fetch detail for each sponsored license to get Name and Type
                        agent_url = f"https://www.trec.texas.gov/acaif/api/licenseDetail/{lic}"
                        agent_resp = requests.get(agent_url, headers=headers, timeout=5)
                        if agent_resp.status_code == 200:
                            agent_data = agent_resp.json()
                            if isinstance(agent_data, list) and len(agent_data) > 0:
                                agent_detail = agent_data[0]
                                name = f"{agent_detail.get('firstName', '')} {agent_detail.get('lastName', '')}".strip()
                                lic_type = agent_detail.get("type", "")
                                
                                if "Broker" in lic_type:
                                    result["designated_broker"] = f"{name} ({lic})"
                                else:
                                    result["sales_agents"].append(f"{name} ({lic})")
                        
    except Exception as e:
        print(f"Error fetching {license_number}: {e}")
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fetch_trec_details.py <license_number>")
        sys.exit(1)
    
    lic = sys.argv[1]
    data = fetch_trec_data(lic)
    print(f"License: {lic}")
    print(f"DBAs: {', '.join(data['dbas']) if data['dbas'] else 'None'}")
    print(f"Teams: {', '.join(data['teams']) if data['teams'] else 'None'}")
    print(f"Designated Broker: {data['designated_broker']}")
    print(f"Sales Agents Sponsored ({len(data['sales_agents'])}):")
    for agent in data['sales_agents']:
        print(f"  - {agent}")
