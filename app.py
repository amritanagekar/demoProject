from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from flask_mysqldb import MySQL
import bcrypt

app = Flask(__name__)
app.secret_key = "many random bytes"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "Mypassword@123"
app.config["MYSQL_DB"] = "crud"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
mysql = MySQL(app)


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        emailid = request.form["emailid"]
        password = request.form["password"]
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM login WHERE emailid = %s", (emailid,))
        user = cur.fetchone()
        cur.close()

        if password and password == user["password"]:
            session["loggedin"] = True
            session["emailid"] = user["emailid"]
            session["user_id"] = user["id"]
            return redirect(url_for("dashboard"))
        else:
            render_template("login.html", error="Invalid user")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        emailid = request.form["emailid"]
        password = request.form["password"]

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO login (username,emailid, password) VALUES (%s,%s, %s)",
            (username, emailid, password),
        )
        mysql.connection.commit()
        cur.close()
        return redirect("/")
    return render_template("register.html")


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "loggedin" in session:
        return render_template("dashboard.html", emailid=session["emailid"])
    return redirect(url_for("login"))


@app.route("/index", methods=["GET", "POST"])
def index():
    if "loggedin" in session:
        if request.method == "POST":
            title = request.form["title"]
            description = request.form["description"]
            user_id = session["user_id"]

            cur = mysql.connection.cursor()
            cur.execute(
                "INSERT INTO todos (title, description, user_id) VALUES (%s, %s, %s)",
                (title, description, user_id),
            )
            mysql.connection.commit()
            cur.close()
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM todos WHERE user_id = %s", (session["user_id"],))
        allTodo = cur.fetchall()
        return render_template("index.html", allTodo=allTodo)
    return redirect(url_for("login"))


@app.route("/update/<int:serial_no>", methods=["GET", "POST"])
def update(serial_no):
    if "loggedin" in session:
        cur = mysql.connection.cursor()
        if request.method == "POST":
            title = request.form["title"]
            description = request.form["description"]
            cur.execute(
                "UPDATE todos SET title = %s, description = %s WHERE serial_no = %s AND user_id = %s",
                (title, description, serial_no, session["user_id"]),
            )
            mysql.connection.commit()
            cur.close()
            return redirect(url_for("index"))
        else:
            cur.execute(
                "SELECT * FROM todos WHERE serial_no = %s AND user_id = %s",
                (serial_no, session["user_id"]),
            )
            todo = cur.fetchone()
            cur.close()
            if todo:
                return render_template("update.html", todo=todo)
            else:
                flash("Todo not found", "error")
                return redirect(url_for("index"))
    return redirect(url_for("login"))


@app.route("/delete/<int:serial_no>")
def delete(serial_no):
    if "loggedin" in session:
        cur = mysql.connection.cursor()
        cur.execute(
            "DELETE FROM todos WHERE serial_no = %s AND user_id = %s",
            (serial_no, session["user_id"]),
        )
        mysql.connection.commit()
        cur.close()
        flash("Todo deleted successfully", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
