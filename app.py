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

@app.route('/input_location', methods=['GET', 'POST'])
def input_location():
    client_ip = request.remote_addr
    if client_ip == '127.0.0.1':
        client_ip = '8.8.8.8'
    geoapify_key = GEOAPIFY_API_KEY

    # Geocode IP address using Geoapify
    url = f"https://api.geoapify.com/v1/ipinfo?ip={client_ip}&apiKey={geoapify_key}"
    response = requests.get(url)
    geo_data = response.json()

    lat = geo_data.get('location', {}).get('latitude')
    lon = geo_data.get('location', {}).get('longitude')
    geo_data['lat'] = lat
    geo_data['lon'] = lon
    return render_template('input_location.html', geo_data=geo_data)

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
    return render_template('home.html', token=token, location=location, lat=lat, lon=lon)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)