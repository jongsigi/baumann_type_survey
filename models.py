from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    user_key = db.Column(db.String(64), unique=True, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    age_group = db.Column(db.String(10), nullable=False)
    baumann_type = db.Column(db.String(10), nullable=True)
    meta_baumann_type = db.Column(db.String(10), nullable=True)

class UserAnswer(db.Model):
    __tablename__ = 'user_answer'
    id = db.Column(db.Integer, primary_key=True)
    user_key = db.Column(db.String(64), nullable=False)
    for i in range(20):
        locals()[f'answer_{i}'] = db.Column(db.Integer, nullable=True)
