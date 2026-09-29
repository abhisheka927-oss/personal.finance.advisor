from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True, nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    incomes = db.relationship("Income", backref="user", lazy=True)

    expenses = db.relationship("Expense", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    amount = db.Column(db.Float, nullable=False)

    source = db.Column(db.String(100), nullable=False)

    date = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    amount = db.Column(db.Float, nullable=False)

    category = db.Column(db.String(100), nullable=False)

    description = db.Column(db.String(200))

    date = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    category = db.Column(db.String(100), nullable=False)

    amount = db.Column(db.Float, nullable=False)

    month = db.Column(db.String(7), nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )