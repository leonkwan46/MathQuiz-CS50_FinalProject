from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from flask_mysqldb import MySQL
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from flask import g, request, redirect, url_for

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

if __name__ == '__main__':
    app.run(debug=True)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# DB & MySQL Connection
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "quiz"
mysql = MySQL(app)
db = mysql.connection.cursor()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
@login_required
def home():
    if request.method == "GET":
        user_id = session["user_id"]
        score_data = db.execute("SELECT score_easy, score_medium, score_hard FROM users WHERE user_id=? ORDER BY ASC", user_id)
        return render_template(".js", score_data=score_data)


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "GET":
        return render_template("login.html")
    
    else:
        if not request.form.get("username"):
            return ERROR 
        if not request.form.get("password"):
            return ERROR

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username").strip())
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password").strip()):
            return ERROR

        session["user_id"] = rows[0]["id"]
        return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    session.clear()

    if request.method == "GET":
        return render_template(".js")

    else:
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        confirm = request.form.get("confirmation").strip()

        if not username:
            return ERROR
        if not password:
            return ERROR
        if not confirm:
            return ERROR
        if password != confirm:
            return ERROR

        else:
            hash = generate_password_hash(password)
            try:
                new_user = db.execute("INSERT INTO users(username, hash, password) VALUES (?,?,?)", username, hash, password)
            except:
                return ERROR

            session["user_id"] = new_user
            return redirect("/")