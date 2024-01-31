from flask import Flask, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models import db, User, Todo
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
db.init_app(app)

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    emailid = data.get("emailid")
    password = data.get("password")
    user = User.query.filter_by(emailid=emailid).first()

    if user and user.check_password(password):
        session["loggedin"] = True
        session["emailid"] = user.emailid
        session["user_id"] = user.id
        return jsonify({"message": "Login successful."}), 200
    else:
        return jsonify({"error": "Invalid user"}), 401

@app.route("/logout", methods=["GET"])
def logout():
    session.pop("loggedin", None)
    session.pop("emailid", None)
    session.pop("user_id", None)
    return jsonify({"message": "Logout successful."}), 200

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    emailid = data.get("emailid")
    password = data.get("password")
    user = User(username=username, emailid=emailid, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully."}), 201

@app.route("/todos", methods=["GET", "POST"])
def todos():
    if request.method == "GET":
        if "loggedin" in session:
            user_id = session["user_id"]
            allTodo = Todo.query.filter_by(user_id=user_id).all()
            return jsonify([todo.serialize() for todo in allTodo]), 200
        else:
            return jsonify({"error": "User not logged in."}), 401
    elif request.method == "POST":
        if "loggedin" in session:
            data = request.json
            title = data.get("title")
            description = data.get("description")
            user_id = session["user_id"]
            todo = Todo(title=title, description=description, user_id=user_id)
            db.session.add(todo)
            db.session.commit()
            return jsonify({"message": "Todo created successfully."}), 201
        else:
            return jsonify({"error": "User not logged in."}), 401

@app.route("/todos/<int:serial_no>", methods=["GET", "PUT"])
def todo_update(serial_no):
    if "loggedin" in session:
        todo = Todo.query.filter_by(serial_no=serial_no).first()
        if todo:
            if request.method == "GET":
                return jsonify(todo.serialize()), 200
            elif request.method == "PUT":
                data = request.json
                todo.title = data.get("title", todo.title)
                todo.description = data.get("description", todo.description)
                db.session.commit()
                return jsonify({"message": "Todo updated successfully."}), 200
        else:
            return jsonify({"error": "Todo not found."}), 404
    else:
        return jsonify({"error": "User not logged in."}), 401

@app.route("/todos/<int:serial_no>", methods=["GET", "DELETE"])
def todo_delete(serial_no):
    if "loggedin" in session:
        todo = Todo.query.filter_by(serial_no=serial_no).first()
        if todo:
            if request.method == "GET":
                return jsonify(todo.serialize()), 200
            elif request.method == "DELETE":
                data = request.json
                db.session.delete(todo)
                db.session.commit()
                return jsonify({"message": "Todo deleted successfully."}), 200
        else:
            return jsonify({"error": "Todo not found."}), 404
    else:
        return jsonify({"error": "User not logged in."}), 401

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)
