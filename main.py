from flask import Flask, render_template, request, flash, redirect, url_for, session
import sqlite3
import re


app = Flask(__name__)
app.secret_key = "123#Ab!)(^%"


con = sqlite3.connect("table.db")
con.execute(
    """CREATE TABLE IF NOT EXISTS customer(
        pid integer primary key,
        username text,
        email text,
        password text)"""
)
con.close()


@app.route("/")
def home():
    if "loggedin" in session:
        return render_template("home.html", username=session["username"])
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    msg = ""
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
        and "email" in request.form
    ):
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]

        con = sqlite3.connect("table.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        data = cur.fetchone()

        if data:
            flash("Account already exists!", "danger")
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Invalid email address!", "danger")
        elif not re.match(r"[A-Za-z0-9]+", username):
            flash("Username must contain only characters and numbers!", "danger")

        elif not re.fullmatch(r"[A-Za-z0-9@#$%^&+=]{8,}", password):
            flash(
                "Password must contain 8 characters, upper and lowercases and numbers!",
                "danger",
            )
        elif not username or not password or not email:
            flash("Incorrect username/password!", "danger")
        else:

            cur.execute(
                "INSERT INTO customer(username,email,password)VALUES(?,?,?)",
                (username, email, password),
            )

            con.commit()
            flash("You have successfully registered!", "success")
        return redirect(url_for("login"))

    elif request.method == "POST":
        msg = "Please fill out the form!"
    return render_template("auth/register.html", title="Register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
    ):
        username = request.form["username"]
        password = request.form["password"]

        con = sqlite3.connect("table.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(
            "SELECT * FROM customer WHERE username=? AND password=?",
            (username, password),
        )

        data = cur.fetchone()

        if data:
            session["loggedin"] = True
            session["id"] = data["id"]
            session["username"] = data["username"]
            return redirect(url_for("home"))
        else:
            flash("Incorrect username/password!")

    return render_template("auth/login.html", title="login")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/profile")
def profile():
    if "loggedin" in session:
        con = sqlite3.connect("table.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM accounts WHERE id = %s", (session["id"],))
        account = cur.fetchone()
        return render_template("profile.html", account=account)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
