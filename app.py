from datetime import datetime, timedelta
from flask import Flask, make_response, jsonify, redirect, request, session
from flask_session import Session
from flask_mysqldb import MySQL
from functools import total_ordering, wraps
from werkzeug.security import check_password_hash, generate_password_hash
from flask import g, request, redirect, url_for
from flask_cors import CORS
import jwt

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
app.config['SECRET_KEY'] = 'test key'
mysql = MySQL(app)



def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        # return 401 if token is not passed
        if not token:
            return jsonify({'message' : 'Token is missing'}), 401
        
        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
            user_id = data["userID"]
            # TODO: look for current user data here
        except:
            return jsonify({
                'message' : 'Invalid token'
            }), 401
        # returns the current logged in users contex to the routes
        return  f(user_id, *args, **kwargs)
  
    return decorated

# HomePage
@app.route("/user", methods=["GET", "POST"])
@token_required
def home(user_id):

    db = mysql.connection.cursor()
    db.execute("SELECT score_easy, score_medium, score_hard, username FROM users WHERE userID = %s",[user_id])
    data = db.fetchone()
    return make_response(jsonify({'data': data}), 200)


# LoginPage
@app.route("/login", methods=["GET", "POST"])
def login():

    if not request.json["username"]:
        return make_response(jsonify({'errorMessage': 'Login failed'}), 401)
    if not request.json["password"]:
        return make_response(jsonify({'errorMessage': 'Login failed'}), 401)

    username = request.json["username"]
    password = request.json["password"]
    
    db = mysql.connection.cursor()
    db.execute("SELECT * FROM users WHERE username LIKE %s", [username])
    rows = db.fetchall()

    if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
        return make_response(jsonify({'errorMessage': 'Incorrect username or password'}), 401)

    token = jwt.encode({
        'userID': rows[0]["userID"],
        'exp': datetime.utcnow() + timedelta(minutes = 3000)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    return make_response(jsonify({'token' : token}), 200)


# RegisterPage
@app.route("/register", methods=["GET", "POST"])
def register():

    con = mysql.connection
    db = con.cursor()

    username = request.json["username"]
    password = request.json["password"]

    if not username:
        return make_response(jsonify({'errorMessage': 'Register failed'}), 401)
    if not password:
        return make_response(jsonify({'errorMessage': 'Register failed'}), 401)

    hash = generate_password_hash(password)
    try:
        db.execute("INSERT INTO users(username, hash, password) VALUES (%s,%s,%s)", (username, hash, password))
        con.commit()
        new_user = db.fetchall()
    except:
        return make_response(jsonify({'errorMessage': 'Account Existed!'}), 401)

    session["user_id"] = new_user
    return make_response(jsonify({'message': 'Register Success'}), 200)


# ForgetPassPage
@app.route("/forget", methods=["GET", "POST"])
def forget():
    con = mysql.connection
    db = con.cursor()

    username = request.json["username"]
    newpass = request.json["password"]

    if not newpass:
        return make_response(jsonify({'errorMessage': 'Changed failed'}), 401)

    hash = generate_password_hash(newpass)
    try:
        db.execute("UPDATE users SET hash = %s, password = %s WHERE username = %s", (hash, newpass, username))
        con.commit()
    except:
        return make_response(jsonify({'errorMessage': 'Unsuccessful!'}), 401)

    return make_response(jsonify({'message': 'Changed Password Success'}), 200)


# ContactUs
@app.route("/contact", methods=["GET", "POST"])
def contact():
    
    con = mysql.connection
    db = con.cursor()

    name = request.json["name"]
    email = request.json["email"]
    subject = request.json["subject"]
    message = request.json["message"]

    try:
        db.execute("INSERT INTO message(name, email, subject, message) VALUES (%s,%s,%s,%s)", (name, email, subject, message))
        con.commit()
    except:
        return make_response(jsonify({'errorMessage': 'Try Again!'}), 401)
    return make_response(jsonify({'message': 'Message sent.'}), 200)


# Score
@app.route("/score", methods=["GET", "POST"])
@token_required
def results(user_id):

    con = mysql.connection  
    db = con.cursor()

    # Get Input
    score = request.json["score"]
    mode = request.json["mode"]
    column = 'score_' + mode
    
    # Get total score from DB
    db.execute("SELECT total FROM users WHERE userID=(%s)",[user_id])
    dict = db.fetchone()
    total = 0
    for val in dict.values():
        total = val + score

    try:
        db.execute("UPDATE users SET total = %s," + column + " = %s WHERE userID = %s", (total, score, user_id))
        con.commit()

    except:
        return make_response(jsonify({'errorMessage': 'Try Again!'}), 401)
    
    return make_response(jsonify({'message': 'Score updated.'}), 200)


# Leaderboard
@app.route("/Leaderboard", methods=["GET", "POST"])
@token_required
def Leaderboard(user_id):  
    db = mysql.connection.cursor()
    # Get Top 5 highest score
    db.execute("SELECT username, total FROM users ORDER BY total DESC LIMIT 5")
    highest = db.fetchall()

    # User's current rank
    db.execute("WITH rankDB AS (SELECT userID, RANK() OVER (ORDER BY total DESC) AS rank FROM users) SELECT rank FROM rankDB WHERE userID = %s", (user_id))
    cur_rank = db.fetchone()

    return make_response(jsonify({'data': highest}, {'cur': cur_rank}), 200)