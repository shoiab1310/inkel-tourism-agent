from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin         # ← ADD THIS LINE!

db = SQLAlchemy()

class User(UserMixin, db.Model):          # ← INHERIT UserMixin HERE!
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sender = db.Column(db.String(50))  # 'user' or 'ai'
    text = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
