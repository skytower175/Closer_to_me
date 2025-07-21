from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)
IPINFO_TOKEN = '1fa5cd7debaa74'


@app.route('/token', methods=['GET', 'POST'])
def token():
    user_token = None
    if request.method == 'POST':
        IPINFO_TOKEN = request.form.get('token')
        starting_location = request.form.get('site')
    return render_template('token.html', token=user_token)

@app.route('/get_location', methods=['GET']) 
def get_location():
    client_ip = request.remote_addr
    if client_ip == '127.0.0.1':
        client_ip = '8.8.8.8'
    response = requests.get(f'https://ipinfo.io/{client_ip}?token={IPINFO_TOKEN}')
    geo_data = response.json()
    # Split the 'loc' field into latitude and longitude
    if 'loc' in geo_data:
        lat, lon = geo_data['loc'].split(',')
        geo_data['lat'] = lat
        geo_data['lon'] = lon
    return render_template('get_location.html', geo_data=geo_data)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)