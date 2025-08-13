## Scrap_realtor.py
# This script fetches property listings from the Realtor API via RapidAPI.
# It supports various filters like location, status, property type, price range, and number of bedrooms.
from quopri import decode
from config import RAPIDAPI_KEY
import requests
import os
import logging
import json
import http.client
from dotenv import load_dotenv
from typing import Dict, List, Optional
from flask import Flask, Blueprint, request, render_template




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
    conn = http.client.HTTPSConnection("us-real-estate-listings.p.rapidapi.com")
    load_dotenv()
    api_key = RAPIDAPI_KEY
    if not api_key:
        raise ValueError("Missing RAPIDAPI_KEY in environment variables")
    
    # API configuration
    #url = "https://realtor-data1.p.rapidapi.com/property_list/"
    url = "https://www.realtor.com/realestateandhomes-detail/11768-SW-245th-Ter_Homestead_FL_33032_M92527-64125"
    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': "us-real-estate-listings.p.rapidapi.com"
    }
    conn.request("GET", "/for-sale?location=Metairie%2C%20LA&offset=0&limit=50&sort=relevance&days_on=1", headers=headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    #print('This is the response:', data)

    try:
        properties = []
        json_data = json.loads(data)
        for listing in json_data["listings"]:
            # Extract address components
            addr = listing["location"]["address"]
            full_address = f"{addr['street_number']} {addr['street_name']} {addr['street_suffix']}"
            if addr.get("unit"):
                full_address += f" {addr['unit']}"
            full_address += f", {addr['city']}, {addr['state_code']} {addr['postal_code']}"
            
            # Extract property details
            details = listing["description"]
            price = listing["list_price"]
            prop_type = details["type"]
            beds = details.get("beds", "N/A")
            baths = details.get("baths", "N/A")
            sqft = details.get("sqft", "N/A")
            
            # Print formatted information
            properties.append({
                "address": full_address,
                "price": price,
                "type": prop_type,
                "beds": beds,
                "baths": baths,
                "sqft": sqft,
                "status": listing['status'].replace('_', ' ').title(),
                "listing_id": listing['listing_id'],
                "url": listing['href']
            })
            return properties
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {str(e)}")
        return []
    except ValueError as e:
        logging.error(f"JSON decode error: {str(e)}")
        return []
