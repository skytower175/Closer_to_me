from datetime import datetime
from extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=True)
    token = db.Column(db.String(200), nullable=True)  # Token for API access
    properties = db.relationship('Property', backref='owner', lazy=True)

    
    # Relationship to properties (one-to-many)

    def __init__(self, username, email, address=None, token=None):
        self.username = username
        self.email = email
        self.address = address
        self.token = token

    def __repr__(self):
        return f'<User {self.username}>'

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Float)
    sqft = db.Column(db.Integer)
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    zip_code = db.Column(db.String(20))
    listed_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    

    def __init__(self, title, description, price, bedrooms, bathrooms, sqft, address, city, state, zip_code, owner_id):
        self.title = title
        self.description = description
        self.price = price
        self.bedrooms = bedrooms
        self.bathrooms = bathrooms
        self.sqft = sqft
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.owner_id = owner_id
    # Foreign key to User
    def __repr__(self):
        return f'<Property {self.title}>'