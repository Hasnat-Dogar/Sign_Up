from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "Ayc3grfo87_ybndi"
app.debug = True

# 🛠️ Safe helper function: Prevents Vercel from crashing if the DB is unlinked
def get_db():
    try:
        if not os.getenv("MYSQLHOST"):
            print("⚠️ MYSQLHOST variable not found. Using local fallback values...")
        return mysql.connector.connect(
            host=os.getenv("MYSQLHOST", "localhost"),
            user=os.getenv("MYSQLUSER", "root"),
            password=os.getenv("MYSQLPASSWORD", "12345678"), 
            database=os.getenv("MYSQLDATABASE", "Sign_Up"),
            port=int(os.getenv("MYSQLPORT", 3306))
        )
    except Exception as e:
        print(f"⚠️ Cloud Database Connection Failed: {e}")
        return None


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/menu")
def menu():
    return render_template("menu.html")

@app.route("/change_pass", methods=["GET","POST"])
def change_pass():
    if "user_login" not in session:
        flash("Please log in first to change your password.", "error")
        return redirect(url_for("sign_in"))
    
    if request.method == "POST":
        login = request.form["login"].strip()
        old_pass = request.form["old_pass"]
        password = request.form["password"]
        confirm = request.form["confirm_password"]

        if password != confirm:
            flash("Passwords do not match.", "error")
            return redirect(url_for("change_pass"))

        conn = get_db()
        if conn is None:
            flash("Database configuration is offline.", "error")
            return redirect(url_for("change_pass"))
            
        cursor = conn.cursor()

        try:
            cursor.execute(
                "Select user_name, email, Password_hash From Users Where user_name = %s Or email = %s",
                (login, login)
            )
            user_input = cursor.fetchone()

            # 🛠️ FIXED: Access index [2] for the password hash string
            if user_input and check_password_hash(user_input[2], old_pass):
                new_pass = generate_password_hash(password)
                try:
                    cursor.execute(
                        "Update Users set Password_hash = %s where user_name = %s Or email = %s",
                        (new_pass, login, login)
                    )
                    conn.commit()
                    session.clear()
                    flash("Passwords Changed Successfully!", "success")
                    return redirect(url_for("sign_in"))
                except mysql.connector.Error:
                    flash("Enter valid Email or User_name", "error")
                    return redirect(url_for("change_pass"))
            else:
                flash("Invalid old password or login information.", "error")
                return redirect(url_for("change_pass"))
        except mysql.connector.Error:
            flash("Please try again later", "error")
            return redirect(url_for("change_pass"))
        finally:
            cursor.close()
            conn.close()

    return render_template("change_pass.html")

@app.route("/forgot_pass", methods=["POST","GET"])
def forgot_pass():
    if request.method == "POST":
        email = request.form["email"].strip()

        conn = get_db()
        if conn is None:
            flash("Database configuration is offline.", "error")
            return redirect(url_for("forgot_pass"))
            
        cursor = conn.cursor()
        try:
            cursor.execute(
                "Select * From Users Where email = %s",
                (email,)
            )
            conn.commit()
        except mysql.connector.Error:
            flash("Enter a Valid Email", "error")
            return redirect(url_for("forgot_pass"))
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for("forgot_pass"))
        
    return render_template("forgot_pass.html")

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        username = request.form["user_name"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]
        confirm = request.form["confirm_password"]

        if password != confirm:
            flash("Passwords do not match.", "error")
            return redirect(url_for("signup"))

        conn = get_db()
        if conn is None:
            flash("Database configuration is offline.", "error")
            return redirect(url_for("signup"))
            
        cursor = conn.cursor()
        try:
            cursor.execute(
                "Insert Into Users (user_name, email, Password_hash) Values (%s, %s, %s)",
                (username, email, generate_password_hash(password))
            )
            conn.commit()
        except mysql.connector.IntegrityError:
            flash("Username or email already exists.", "error")
            return redirect(url_for("signup"))
        finally:
            cursor.close()
            conn.close()

        session["new_user"] = username
        return redirect(url_for("submit"))

    return render_template("index.html")

@app.route("/submit")
def submit():
    return render_template("submit.html")


@app.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        login = request.form["login"].strip()
        password = request.form["password"] 

        conn = get_db()
        if conn is None:
            flash("Database configuration is offline.", "error")
            return redirect(url_for("sign_in"))
            
        cursor = conn.cursor()
        try:
            cursor.execute(
                "Select user_name, email, Password_hash From Users Where user_name = %s Or email = %s", 
                (login, login)
            )
            user_input = cursor.fetchone()

            # 🛠️ FIXED: Access index [2] for the password hash string
            if user_input and check_password_hash(user_input[2], password):
                flash("Logged in successfully!", "success")
                session["user_login"] = user_input[0]
                session["user_email"] = user_input[1]
                return redirect(url_for("menu"))
            else:
                flash("Invalid username or password.", "error")
                return redirect(url_for("sign_in"))
        except mysql.connector.Error:
            flash("Please try again later", "error")
            return redirect(url_for("sign_in"))
        finally:
            cursor.close()
            conn.close()

    return render_template("sign_in.html")


@app.route("/signout")
def signout():
    session.clear()
    return redirect(url_for("sign_in"))

@app.route("/login_pages")
def login_pages():
    if "user_login" not in session:
        flash("Please log in first to access this page.")
        return redirect(url_for("sign_in"))

    username = session["user_login"]
    return f"Welcome Back, {username}!"
