from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    is_admin = db.Column(db.Boolean, default=False)
    skin_type = db.Column(db.String(50))
    age = db.Column(db.Integer)
    concerns = db.Column(db.Text)
    quiz_results = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    addresses = db.relationship('Address', backref='user', lazy=True)

    def set_password(self, password):
        import hashlib
        # Creates a short 15-character hash for storage
        self.password_hash = hashlib.md5(password.encode()).hexdigest()[:15]

    def check_password(self, password):
        import hashlib
        # Checks against the short 15-character bash
        return self.password_hash == hashlib.md5(password.encode()).hexdigest()[:15]
        
    def get_concerns(self):
        if self.concerns:
            try:
                return json.loads(self.concerns)
            except:
                return []
        return []

    def set_concerns(self, concerns_list):
        self.concerns = json.dumps(concerns_list)

    def get_quiz_results(self):
        if self.quiz_results:
            try:
                return json.loads(self.quiz_results)
            except:
                return {}
        return {}

    def set_quiz_results(self, results_dict):
        self.quiz_results = json.dumps(results_dict)

    @property
    def budget(self):
        results = self.get_quiz_results()
        try:
            return float(results.get('budget', 2000.0))
        except (ValueError, TypeError):
            return 2000.0

    @budget.setter
    def budget(self, value):
        results = self.get_quiz_results()
        try:
            results['budget'] = float(value)
        except (ValueError, TypeError):
            results['budget'] = 2000.0
        self.set_quiz_results(results)

    @property
    def sensitivity(self):
        results = self.get_quiz_results()
        return results.get('sensitivity', 'mild')

    @sensitivity.setter
    def sensitivity(self, value):
        results = self.get_quiz_results()
        results['sensitivity'] = str(value)
        self.set_quiz_results(results)

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    brand = db.Column(db.String(100))
    category = db.Column(db.String(100))
    price = db.Column(db.Float)
    rating = db.Column(db.Float)
    ingredients = db.Column(db.Text)
    description = db.Column(db.Text)
    _image_url = db.Column('image_url', db.String(2048))

    @property
    def image_url(self):
        url = self._image_url
        if url:
            if url.startswith('/') or url.startswith('http://') or url.startswith('https://'):
                return url
            normalized = url.replace('\\', '/')
            filename = normalized.split('/')[-1]
            return f'/static/images/products/{filename}'
        return url

    @image_url.setter
    def image_url(self, value):
        self._image_url = value
    suitable_for = db.Column(db.String(50)) # e.g. Oily, Dry, etc
    concerns = db.Column(db.Text) # JSON list or comma-separated string
    stock = db.Column(db.Integer, default=100)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    transactions = db.relationship('Transaction', backref='product', lazy=True)

    @property
    def in_stock(self):
        return (self.stock or 0) > 0

    def get_key_ingredients(self, limit=3):
        """Returns first N ingredients from the comma-separated ingredients string."""
        if not self.ingredients:
            return []
        parts = [i.strip() for i in self.ingredients.split(',') if i.strip()]
        return parts[:limit]

    def get_concerns_list(self, limit=3):
        """Returns first N concerns from the comma-separated concerns string."""
        if not self.concerns:
            return []
        parts = [c.strip() for c in self.concerns.split(',') if c.strip()]
        return parts[:limit]

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    status = db.Column(db.String(50), default='completed')
    date = db.Column(db.DateTime, default=datetime.utcnow)
    address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'), nullable=True)
    
    address = db.relationship('Address', backref='transactions', lazy=True)
    payment = db.relationship('Payment', backref='transaction', uselist=False, lazy=True)

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), unique=True, nullable=False)
    payment_method = db.Column(db.String(50))
    payment_status = db.Column(db.String(50), default='paid')
    amount_paid = db.Column(db.Float, nullable=False)
    transaction_ref = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Address(db.Model):
    __tablename__ = 'addresses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    street_address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pin_code = db.Column(db.String(20), nullable=False)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
