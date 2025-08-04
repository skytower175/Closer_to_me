from flask import Flask, render_template, request, jsonify
import requests
import config
from config import IPINFO_TOKEN, GEOAPIFY_API_KEY    
import googlemaps
from geopy.distance import geodesic 
from datetime import datetime
import googlemaps   
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # or your preferred DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
 # Replace with your actual API key

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=True)
    def __init__(self, username, email, address=None):
        self.username = username
        self.email = email
        self.address = address

    def __repr__(self):
        return f'<User {self.username}>'

def get_property_listings(location, token):
    url = "https://realtor-com-real-estate.p.rapidapi.com/for-sale"
    querystring = {
        "location": location,
        "offset": "0",
        "limit": "10"  # Number of listings to show
    }
    headers = {
        "X-RapidAPI-Key": token,
        "X-RapidAPI-Host": REAL_ESTATE_HOST
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        return response.json().get('data', {}).get('results', [])
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return []

@app.route('/token', methods=['GET', 'POST'])
def token():
    message = None
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        address = request.form.get('address')
        if username and email and address:
            user = User(username=username, email=email, address=address)
            db.session.add(user)
            db.session.commit()
            message = "User registered successfully!"
        else:
            message = "All fields are required."
    return render_template('register.html', message=message)


@app.route('/users')
def users():
    all_users = User.query.all()
    return render_template('users.html', users=all_users)

@app.route('/', methods=['GET', 'POST'])
def home():
    token = None
    location = None
    lat = None
    lon = None
    school = None
    shopping = None
    
    
    geoapify_key = GEOAPIFY_API_KEY

    if request.method == 'POST':
        token = request.form.get('token')
        location = request.form.get('location')
        if location:
            # Geocode location using Geoapify
            url = f"https://api.geoapify.com/v1/geocode/search?text={location}&apiKey={geoapify_key}"
            response = requests.get(url)
            data = response.json()
            if data['features']:
                coords = data['features'][0]['geometry']['coordinates']
                lon = coords[0]
                lat = coords[1]
                # Find nearest school using Geoapify Places API
                places_url = (
                    f"https://api.geoapify.com/v2/places?categories=education.school"
                    f"&filter=circle:{lon},{lat},5000&limit=1&apiKey={geoapify_key}"
                )
                places_resp = requests.get(places_url)
                places_data = places_resp.json()
                if places_data['features']:
                    school_feature = places_data['features'][0]
                    school = {
                        'name': school_feature['properties'].get('name', 'Unknown'),
                        'address': school_feature['properties'].get('address_line2', 'Unknown'),
                        'distance': school_feature['properties'].get('distance', 0)
                    }
                # Find nearest shopping center
                shopping_url = (
                    f"https://api.geoapify.com/v2/places?categories=commercial.shopping_mall"
                    f"&filter=circle:{lon},{lat},5000&limit=1&apiKey={geoapify_key}"
                )
                shopping_resp = requests.get(shopping_url)
                shopping_data = shopping_resp.json()
                if shopping_data['features']:
                    shopping_feature = shopping_data['features'][0]
                    shopping = {
                        'name': shopping_feature['properties'].get('name', 'Unknown'),
                        'address': shopping_feature['properties'].get('address_line2', 'Unknown'),
                        'distance': shopping_feature['properties'].get('distance', 0)
                    }
    
            
    return render_template(
        'home.html',
        token=token,
        location=location,
        lat=lat,
        lon=lon,
        school=school,
        shopping=shopping
    )
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)