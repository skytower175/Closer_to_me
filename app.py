from flask import Flask, render_template, request, jsonify
import requests
import googlemaps
from datetime import datetime
import googlemaps   
from flask_sqlalchemy import SQLAlchemy


from flask_migrate import Migrate
from config import Config


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'


# Initialize database
db = SQLAlchemy(app)

from models import User, Property
# Replace with your actual API key
IPINFO_TOKEN = "1fa5cd7debaa74"
GEOAPIFY_API_KEY = "f3e6910ed731470e8f7463759f3d5b37"

@app.route('/init_db')
def init_db():
    # Create tables
    db.create_all()
    
    # Create sample data
    user1 = User(username='john', email='john@example.com', token=GEOAPIFY_API_KEY)
    user2 = User(username='sarah', email='sarah@example.com', token=GEOAPIFY_API_KEY)

    property1 = Property(
        title='Beautiful Family Home',
        description='Spacious 4-bedroom house with garden',
        price=750000,
        bedrooms=4,
        bathrooms=2.5,
        sqft=2400,
        address='123 Main St',
        city='San Francisco',
        state='CA',
        zip_code='94105',
        owner=user1
    )
    
    property2 = Property(
        title='Modern Downtown Condo',
        description='Luxury condo with city views',
        price=950000,
        bedrooms=2,
        bathrooms=2,
        sqft=1200,
        address='456 Market St',
        city='San Francisco',
        state='CA',
        zip_code='94103',
        owner=user2
    )
    
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(property1)
    db.session.add(property2)
    db.session.commit()

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        address = request.form.get('address')
        token = request.form.get('token')
        if username and email and address and token:    
            # Here you would typically verify the token and authenticate the user
            # For simplicity, we will just create a new user
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

@app.route('/', methods=['GET', 'POST'])
def home():

    token = "f3e6910ed731470e8f7463759f3d5b37"
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