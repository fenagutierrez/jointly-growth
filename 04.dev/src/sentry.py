import requests
import pandas as pd
from typing import Optional
import re

def get_sentry_replays(query: str, auth_token: Optional[str] = None, max_pages: Optional[int] = None) -> pd.DataFrame:
    """
    Fetch Sentry replays data based on a query string with pagination support.
    
    Args:
        query (str): The query string to filter replays (e.g. 'user.email:example@email.com')
        auth_token (str, optional): Sentry auth token. If not provided, will use default token.
        max_pages (int, optional): Maximum number of pages to fetch. If not provided, will fetch all pages.
        
    Returns:
        pd.DataFrame: DataFrame containing all the replays data across all pages
        
    Raises:
        requests.exceptions.RequestException: If the API request fails
    """
    # Default organization and auth token
    organization_slug = 'jointly-u7'
    if auth_token is None:
        import os
        auth_token = os.getenv('SENTRY_AUTH_TOKEN')
    
    if not auth_token:
        raise ValueError("Sentry Auth Token is required. Set SENTRY_AUTH_TOKEN environment variable.")
    
    # Set up the headers with the authorization token
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',
    }
    
    # Sentry API endpoint for retrieving replays with query filter
    base_url = f'https://sentry.io/api/0/organizations/{organization_slug}/replays/'
    
    # Initialize variables for pagination
    all_data = []
    url = base_url
    page_count = 0
    
    # Query parameters to filter replays  
    params = {
        'query': query
    }
    
    while url and (max_pages is None or page_count < max_pages):
        # Make the GET request to retrieve filtered replays
        if url == base_url:
            # First request with params
            response = requests.get(url, headers=headers, params=params)
        else:
            # Subsequent requests use full URL from Link header
            response = requests.get(url, headers=headers)
        
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Get data from response
        response_data = response.json()
        data = response_data.get('data', [])
        all_data.extend(data)
        
        print(f"Fetched page {page_count + 1}: {len(data)} replays")
        
        # Check for next page in Link header
        link_header = response.headers.get('Link', '')
        next_url = None
        
        if link_header:
            # Parse Link header to find next URL
            # Format: <URL>; rel="next"; results="true"; cursor="..."
            next_match = re.search(r'<([^>]+)>;\s*rel="next";\s*results="true"', link_header)
            if next_match:
                next_url = next_match.group(1)
        
        url = next_url
        page_count += 1
        
        # If no more results, break
        if not next_url:
            break
    
    print(f"Total replays fetched: {len(all_data)} across {page_count} pages")
    
    # Convert all data to DataFrame
    df = pd.DataFrame(all_data)
    return df 