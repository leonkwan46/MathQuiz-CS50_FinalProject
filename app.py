from flask import Flask, flash, make_response, jsonify, redirect, render_template, request, session
from flask_session import Session
from flask_mysqldb import MySQL
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from flask import g, request, redirect, url_for
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
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
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/", methods=["GET", "POST"])
# @login_required

def home():
    db = mysql.connection.cursor()
    # user_id = session["user_id"]
    if request.method == "GET":
        db.execute("SELECT score_easy, score_medium, score_hard FROM users WHERE userID=(%s)",'1')
        data = db.fetchall()
        return make_response(jsonify(data))

@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if not request.json["username"]:
        return make_response(jsonify({'errorMessage': 'Login failed'}), 401)
    if not request.json["password"]:
        return make_response(jsonify({'errorMessage': 'Login failed'}), 401)

    username = request.json["username"]
    password = request.json["password"]
    
    db = mysql.connection.cursor()
    db.execute("SELECT * FROM users WHERE username LIKE %s", [username])
    rows = db.fetchall()

    if len(rows) != 1 or not check_password_hash(rows[0]["password"] != password):
        return make_response(jsonify({'errorMessage': 'Login failed 2'}), 401)

    session["user_id"] = rows[0]["userID"]
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():

    session.clear()

    con = mysql.connection
    db = con.cursor()

    username = request.json["username"]
    password = request.json["password"]

    if not username:
        return make_response(jsonify({'errorMessage': 'Register failed'}), 401)
    if not password:
        return make_response(jsonify({'errorMessage': 'Register failed'}), 403)

    hash = generate_password_hash(password)
    try:
        db.execute("INSERT INTO users(username, hash, password) VALUES (%s,%s,%s)", (username, hash, password))
        con.commit()
        new_user = db.fetchall()
    except:
        return make_response(jsonify({'errorMessage': 'Account Existed!'}), 403)

    session["user_id"] = new_user
    return redirect("/")