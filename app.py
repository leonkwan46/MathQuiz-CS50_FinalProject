from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from flask_mysqldb import MySQL
from functools import wraps
from flask import g, request, redirect, url_for

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
mysql = MySQL(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# HomePage (Logged)
@app.route("/")
@login_required
def home():
    return render_template("??.html")

# Register
@app.route("/register", method = ["GET", "POST"])
def register():
    name = request.form.get("name")
    password = request.form.get("password")
    confirmpass = request.form.get("confirmpass")


    return render_template("register.html")

# LogIn
@app.route("/login", method = ["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name").strip()
        password = request.form.get("password").strip()

        session["user_id"] = name[0]["id"]

    return render_template("login.html")

