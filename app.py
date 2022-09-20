from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from flask_mysqldb import MySQL
from functools import wraps
from flask import g, request, redirect, url_for

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# DB & MySQL Connection
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "quiz"
mysql = MySQL(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user")
    fetchdata = cur.fetchall()
    cur.close()
    return render_template("test.html", data = fetchdata)



# @app.route("/login", methods=["GET", "POST"])
# def login():
#     session.clear()
#     if request.method == "GET":
#         return render_template("login.html")
    
#     else:
#         if not request.form.get("username"):
#             return 

#         elif not request.form.get("password"):
#             return 

#         rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username").strip())
#         if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password").strip()):
#             return apology("invalid username and/or password", 403)

#         session["user_id"] = rows[0]["id"]
#         return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)
