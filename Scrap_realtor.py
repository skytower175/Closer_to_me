## Scrap_realtor.py
# This script fetches property listings from the Realtor API via RapidAPI.
# It supports various filters like location, status, property type, price range, and number of bedrooms.
from config import RAPIDAPI_KEY
import requests
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional

def get_realtor_properties(
    location: str,
    status: str = "for_sale",
    property_type: str = "single_family",
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    bedrooms: Optional[int] = None,
    limit: int = 20,
    offset: int = 0
) -> List[Dict]:
    """
    Fetch property listings from Realtor API via RapidAPI
    
    Parameters:
    location (str): Search location (e.g., "Miami, FL", "90210")
    status (str): Property status - "for_sale", "for_rent", "sold"
    property_type (str): "single_family", "condo", "townhouse", "multi_family"
    min_price (int): Minimum price filter
    max_price (int): Maximum price filter
    bedrooms (int): Number of bedrooms
    limit (int): Results per page (max 50)
    offset (int): Pagination offset
    
    Returns:
    List of property dictionaries or empty list on error
    """
    # Load API key from environment
    load_dotenv()
    api_key = RAPIDAPI_KEY
    if not api_key:
        raise ValueError("Missing RAPIDAPI_KEY in environment variables")
    
    # API configuration
    url = "https://realtor-data1.p.rapidapi.com/property_list/"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "realtor-data1.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    
    # Build query payload
    payload = {
        "query": {
            "status": [status],
            "property_type": [property_type],
        },
        "limit": min(limit, 50),  # API max limit is 50
        "offset": offset,
        "sort": {"field": "list_date", "direction": "desc"}
    }
    
    # Add location filters (supports city, state, zip)
    if ',' in location:
        city, state = location.split(',', 1)
        payload["query"]["city"] = city.strip()
        payload["query"]["state_code"] = state.strip()
    elif location.isdigit() and len(location) == 5:
        payload["query"]["postal_code"] = location
    else:
        payload["query"]["city"] = location
    
    # Add optional filters
    if min_price:
        payload["query"]["min_price"] = min_price
    if max_price:
        payload["query"]["max_price"] = max_price
    if bedrooms:
        payload["query"]["beds"] = bedrooms
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Return results with simplified structure
        return [
            {
                "id": prop.get("property_id"),
                "price": prop.get("price"),
                "address": prop.get("address", {}).get("line"),
                "city": prop.get("address", {}).get("city"),
                "state": prop.get("address", {}).get("state_code"),
                "zip": prop.get("address", {}).get("postal_code"),
                "beds": prop.get("description", {}).get("beds"),
                "baths": prop.get("description", {}).get("baths"),
                "sqft": prop.get("description", {}).get("sqft"),
                "photo": prop.get("photos", [{}])[0].get("href") if prop.get("photos") else None,
                "listing_date": prop.get("list_date"),
                "permalink": prop.get("permalink")
            }
            for prop in data.get("data", {}).get("results", [])
        ]
    
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {str(e)}")
        return []
    except ValueError as e:
        print(f"JSON decode error: {str(e)}")
        return []