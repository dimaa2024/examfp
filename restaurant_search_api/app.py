import json
import random
import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from functools import wraps
from datetime import datetime, timedelta
import boto3
import os

app = Flask(__name__)

# Load secrets from AWS Secrets Manager
secrets_client = boto3.client('secretsmanager', region_name='us-east-1')
secret_name = "restaurant_api_secrets"
secret_response = secrets_client.get_secret_value(SecretId=secret_name)
secrets = json.loads(secret_response['SecretString'])

app.config['SECRET_KEY'] = secrets['SECRET_KEY']
app.config['SQLALCHEMY_DATABASE_URI'] = secrets['SQLALCHEMY_DATABASE_URI']
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Database Model
class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    website = db.Column(db.String(100), nullable=False)
    opening_hours = db.Column(db.String(100), nullable=False)
    cuisine_type = db.Column(db.String(50), nullable=False)
    is_kosher = db.Column(db.Boolean, nullable=False)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(100), nullable=False)
    ip = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Decorator to protect admin route
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/api/restaurants', methods=['GET'])
def get_restaurants():
    cuisine = request.args.get('cuisine')
    kosher = request.args.get('kosher')
    open_now = request.args.get('open_now')
    
    query = Restaurant.query
    if cuisine:
        query = query.filter_by(cuisine_type=cuisine)
    if kosher:
        query = query.filter_by(is_kosher=(kosher.lower() == 'true'))
    if open_now:
        current_hour = datetime.now().hour
        query = query.filter(Restaurant.opening_hours.contains(str(current_hour)))
    
    # Audit log
    ip = request.remote_addr
    country = request.headers.get('X-Country', 'Unknown')
    audit_entry = AuditLog(query=str(request.args), ip=ip, country=country)
    db.session.add(audit_entry)
    db.session.commit()
    
    restaurants = query.all()
    return jsonify([{
        'name': r.name,
        'address': r.address,
        'phone': r.phone,
        'website': r.website,
        'opening_hours': r.opening_hours,
        'cuisine_type': r.cuisine_type,
        'is_kosher': r.is_kosher
    } for r in restaurants])

@app.route('/admin', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == secrets['ADMIN_PASSWORD']:
            session['logged_in'] = True
            return redirect(url_for('admin_page'))
    return render_template('login.html')

@app.route('/admin_page')
@login_required
def admin_page():
    restaurants = Restaurant.query.all()
    return render_template('admin.html', restaurants=restaurants)

@app.route('/admin/add', methods=['POST'])
@login_required
def add_restaurant():
    data = request.form
    new_restaurant = Restaurant(
        name=data['name'],
        address=data['address'],
        phone=data['phone'],
        website=data['website'],
        opening_hours=data['opening_hours'],
        cuisine_type=data['cuisine_type'],
        is_kosher=(data['is_kosher'].lower() == 'true')
    )
    db.session.add(new_restaurant)
    db.session.commit()
    return redirect(url_for('admin_page'))

@app.route('/admin/delete/<int:id>', methods=['POST'])
@login_required
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    db.session.delete(restaurant)
    db.session.commit()
    return redirect(url_for('admin_page'))

@app.route('/admin/audit')
@login_required
def audit_log():
    last_day = datetime.now() - timedelta(days=1)
    logs = AuditLog.query.filter(AuditLog.timestamp >= last_day).all()
    return render_template('audit.html', logs=logs)

if __name__ == '__main__':
    app.run(debug=True)