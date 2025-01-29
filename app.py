from flask import Flask, jsonify, abort
from geopy.distance import geodesic
import requests

app = Flask(__name__)

@app.route('/properties', methods=['GET'])
def get_properties():
    api_key = 'YOUR_API_KEY'
    url = 'https://api.domain.com.au/v1/listings'
    headers = {'Authorization': f'Bearer {api_key}'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        properties = response.json().get('data', [])
    except (requests.RequestException, ValueError) as e:
        app.logger.error(f"Error fetching properties: {e}")
        abort(500, description="Error fetching properties")
    
    hospital_location = (28.6139, 77.2090)  # Example coordinates for a hospital
    properties_with_distance = []
    
    for property in properties:
        property_location = (property['latitude'], property['longitude'])
        distance = geodesic(hospital_location, property_location).kilometers
        properties_with_distance.append({
            'address': property['address'],
            'distance': distance
        })
    
    return jsonify(properties_with_distance)

if __name__ == '__main__':
    app.run(debug=True)