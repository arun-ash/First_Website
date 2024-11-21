from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import bcrypt
from dotenv import load_dotenv
import os

app = Flask(__name__)

DATABASE = "database.db"

app.secret_key = os.urandom(24) #Used for session management apparently?

#load env variables
load_dotenv

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD')


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS submissions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        message TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


@app.route("/")
def index():
    #To render the user input form
    return render_template("index.html")


@app.route("/submit", methods=['POST'])
def submit():
    #To handle form submissions and to save the same to the DB
    name  = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    #Saving the data to the DataBase
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO submissions (name, email, message) VALUES (?, ?, ?)",
        (name, email, message),
    )
    conn.commit()
    conn.close()

    return redirect(url_for('thank_you',name=name))

#Thankyou page
@app.route('/thank-you')
def thank_you():
    name = request.args.get('name')
    return render_template('thankyou.html',name=name)


@app.route("/admin", methods=["GET","POST"])
def admin():
    #If admin is not logged in, redirect to login page
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    
    #Display the submissions to the admin
    conn   = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(" SELECT * FROM submissions")
    rows = cursor.fetchall()
    conn.close()

    return render_template("admin.html", submissions = rows)

@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        #Validate credentials
        if username== ADMIN_USERNAME and bcrypt.checkpw(password.encode("utf-8"),ADMIN_PASSWORD_HASH.encode("utf-8")):
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))
        
        else:
            return render_template("admin_login.html",error="Invalid Credentials")
        
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in",None)
    return redirect(url_for("admin_login"))


@app.route('/erase',methods=['POST'])
def erase_data():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Submissions")
    conn.commit()
    conn.close()

    return redirect(url_for('admin'))



#Initialize the Db before the app runs
init_db()


if __name__ == "__main__":
    #init_db()
    app.run(debug = True, port=8080)