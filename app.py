from flask import Blueprint, Flask, json, render_template, request, jsonify
import requests
from datetime import datetime
import googlemaps   
from Scrap_realtor import get_realtor_properties
from extensions import db
from models import User, Property
from config import API_KEY, RAPIDAPI_KEY, GEOAPIFY_API_KEY
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
import os
from Scrap_realtor import get_realtor_properties
import logging

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db.init_app(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        address = request.form.get('address')
        token = request.form.get('token')
        if username and email and address and token:    
            user = User(username=username, email=email, address=address)
            db.session.add(user)
            db.session.commit()
            message = "User logged in successfully!"    
        else:
            message = "All fields are required."
    return render_template('register.html', message=message)
@app.route('/users')
def users():
    all_users = User.query.all()
    return render_template('users.html', users=all_users)

@app.route('/Listing', methods=['GET', 'POST'])
def listing():
    bp = Blueprint('listings', __name__)
   # location = request.args.get('location', 'New York, NY')
   # min_price = request.args.get('min_price', type=int)
   # max_price = request.args.get('max_price', type=int)
   # bedrooms = request.args.get('bedrooms', type=int)    
    properties = get_realtor_properties(
        location='New York, NY',
        min_price=0,
        max_price=99999,
        bedrooms=2,
        limit=24
    )
    app.logger.info(f"Fetched properties: {properties}")

    return render_template('listings.html', properties=properties)
@app.route('/', methods=['GET', 'POST'])
def home():
    token = GEOAPIFY_API_KEY
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
                        'distance': school_feature['properties'].get('distance', 10)
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
                        'distance': shopping_feature['properties'].get('distance', 10)
                    }
    
            
    return render_template(
        'home.html',
        #token=token,
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