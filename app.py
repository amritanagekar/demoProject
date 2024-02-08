from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from dotenv import load_dotenv
import os
from models import db,User,Todo

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        emailid = request.form["emailid"]
        password = request.form["password"]
        user = User.query.filter_by(emailid=emailid).first()

        if user and user.check_password(password):
            print(user)
            print(password)
            session["loggedin"] = True
            session["emailid"] = user.emailid
            session["user_id"] = user.id
            return redirect("/dashboard")
        else:
            render_template("login.html", error="Invalid user")

    return render_template("login.html")

@app.route("/login_api", methods=["POST"])
def login_api():
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
    
@app.route("/logout_api", methods=["GET", "POST"])
def logout_api():
    session.pop("loggedin", None)
    session.pop("user_id", None)
    return jsonify({"message": "Logout successful."}), 200

@app.route("/logout")
def logout():
    session.pop("loggedin", None)
    session.pop("user_id", None)
    return redirect("/")

@app.route("/register_api", methods=["POST"])
def register_api():
    data = request.json
    username = data.get("username")
    emailid = data.get("emailid")
    password = data.get("password")
    user = User(username=username, emailid=emailid, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully."}), 201


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        emailid = request.form["emailid"]
        password = request.form["password"]
        user = User(username=username, emailid=emailid, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect("/")
    return render_template("register.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "loggedin" in session:
        return render_template("dashboard.html")
    return redirect(url_for("login"))


@app.route("/todos_api", methods=["GET", "POST"])
def todos_api():
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

@app.route("/todos_api/<int:serial_no>", methods=["GET", "PUT", "DELETE"])
def todo_crud(serial_no):
    if "loggedin" not in session:
        return jsonify({"error": "User not logged in."}), 401

    todo = Todo.query.get_or_404(serial_no)

    if request.method == "GET":
        return jsonify(todo.serialize()), 200

    elif request.method == "PUT":
        data = request.json
        todo.title = data.get("title", todo.title)
        todo.description = data.get("description", todo.description)
        db.session.commit()
        return jsonify({"message": "Todo updated successfully."}), 200

    elif request.method == "DELETE":
        db.session.delete(todo)
        db.session.commit()
        return jsonify({"message": "Todo deleted successfully."}), 200



@app.route("/index", methods=["GET", "POST"])
def index():
    if "loggedin" in session:
        if request.method == "POST":
            title = request.form["title"]
            description = request.form["description"]
            user_id = session["user_id"]
            print(description)
            print(user_id)
            todo = Todo(title=title, description=description, user_id=user_id)
            db.session.add(todo)
            db.session.commit()
        allTodo = Todo.query.filter_by(user_id=session["user_id"]).all()
        return render_template("index.html", allTodo=allTodo)
    return redirect(url_for("login"))


@app.route("/update/<int:serial_no>", methods=["GET", "POST"])
def update(serial_no):
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        todo = Todo.query.filter_by(serial_no=serial_no).first()
        todo.title = title
        todo.description = description
        db.session.add(todo)
        db.session.commit()
        return redirect("/index")
    todo = Todo.query.filter_by(serial_no=serial_no).first()
    return render_template("update.html", todo=todo)


@app.route("/delete/<int:serial_no>")
def delete(serial_no):
    todo = Todo.query.filter_by(serial_no=serial_no).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/index")


if __name__ == "__main__":
    # This ensures that the database tables are created before running the app
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
