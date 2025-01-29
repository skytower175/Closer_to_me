import googlemaps
from datetime import datetime
from flask import Flask, jsonify 
from geopy.distance import geodesic
import requests



# Initialize the Google Maps client with your API key
gmaps = googlemaps.Client(key=API_KEY)


def find_nearest(destination, gmaps, type):
    # Initialize the client
    # Geocode the destination to get the latitude and longitude
    geocode_result = gmaps.geocode(destination)
    location = geocode_result[0]['geometry']['location']
    destination_coords = (location['lat'], location['lng'])

    # Find nearby schools
    places_result = gmaps.places_nearby(location=destination_coords, radius=5000, type=type)

    # Get the nearest school
    if places_result['results']:
        nearest_school = places_result['results'][0]
        name = nearest_school['name']
        address = nearest_school['vicinity']
        return name, address
    else:
        return None, None
    
# Define the origin and destination (can be addresses or coordinates)
origin = "Manila, Philippines"  # Example: starting point
destination = "Quezon City, Philippines"  # Example: destination

school_name, school_address = find_nearest(destination, gmaps, type='school')
# Request the distance matrix data
distance_matrix = gmaps.distance_matrix(origins=origin, destinations=destination, mode="driving")

# Extract the distance and duration from the response
distance = distance_matrix['rows'][0]['elements'][0]['distance']['text']  # e.g., "10.3 km"
duration = distance_matrix['rows'][0]['elements'][0]['duration']['text']  # e.g., "15 mins"

def get_properties():
    api_key = 'GET'
    url = 'https://api.domain.com.au/v1/listings'
    headers = {'Authorization': f'Bearer {api_key}'}
    response = requests.get(url, headers=headers)
    properties = response.json()['data']
    hospital_location = (28.6139, 77.2090)  # Example coordinates for a hospital
    properties_with_distance = []    
    for property in properties:
        property_location = (property['latitude'], property['longitude'])
        distance = geodesic(hospital_location, property_location).kilometers
        properties_with_distance.append({
            'address': property['address'],
            'distance': distance
        })    
    return jsonify(properties_with_distance)# Output the results

print(f"Distance: {distance}")
print(f"Duration: {duration}")
