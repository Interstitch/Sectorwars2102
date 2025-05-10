from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    credits = db.Column(db.Integer, default=1000)
    location = db.Column(db.Integer, default=1)
    ship_type = db.Column(db.String(80), default="Light Freighter")
    ship_name = db.Column(db.String(80))
    fighters = db.Column(db.Integer, default=0)
    turns = db.Column(db.Integer, default=100)
    docked = db.Column(db.Boolean, default=False)
    landed = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Cargo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    commodity = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Integer, default=0)
    user = db.relationship('User', backref=db.backref('cargo_items', lazy=True))

class Sector(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    has_planet = db.Column(db.Boolean, default=False)
    planet_owner = db.Column(db.Integer, db.ForeignKey('user.id'))
    port_data = db.Column(db.JSON)
    links = db.Column(db.JSON)
    planet_fighters = db.Column(db.Integer, default=0)
    sector_fighters = db.Column(db.Integer, default=0)
    is_earth = db.Column(db.Boolean, default=False)

def init_db():
    with app.app_context():
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()