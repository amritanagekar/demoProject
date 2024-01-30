from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    emailid = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    todos = db.relationship("Todo", backref="user")

    def __repr__(self) -> str:
        return f"{self.id} - {self.username}"

    def __init__(self, emailid, password, username):
        self.username = username
        self.emailid = emailid
        self.password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    def check_password(self, password):
        stored_password = self.password.encode("utf-8")
        input_password = password.encode("utf-8")
        return bcrypt.checkpw(input_password, stored_password)

class Todo(db.Model):
    serial_no = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=True)
    description = db.Column(db.String(500), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
