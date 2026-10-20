from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import random
import smtplib
from email.message import EmailMessage


app = Flask(__name__)
app.secret_key = "Ayc3grfo87_ybndi"
app.debug = True


def get_db():
    try:
        host = os.environ.get('DB_HOST', 'mysql-5c087bc-signify.c.aivencloud.com')
        user = os.environ.get('DB_USER', 'avnadmin')
        password = os.environ.get('DB_PASSWORD', 'AVNS_efsZvqZeJxZE6eLwAS3')
        database = os.environ.get('DB_NAME', 'Sign_Up')
        port = int(os.environ.get('DB_PORT', 12070))

        ssl_config = {}
        if port != 12070:
            ssl_config = {'ssl_mode': 'REQUIRED'}

        return mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            **ssl_config
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


# @app.route("/OTP", methods=["GET","POST"])
# def OTP():
    # if request.method == "POST":
    #     user_otp = request.form["OTP"]

    #     real_OTP = random.randint(000000,999999)

    #     server = smtplib.SMTP('smtp.gmail.com',465)
    #     server.starttls()


    #     to_mail = request.form["email"].strip()

    #     msg = EmailMessage()
    #     msg['Subject'] = "OTP Verification"
    #     msg['From'] = from_mail
    #     msg['To'] = to_mail
    #     msg.set_content("Your OTP is : ", real_OTP)

    #     server.send_message(msg)
    #     flash("OTP is sent to your Email")

    #     if user_otp == real_OTP:
    #         flash("OTP Verified successfully","success")
    #         return redirect(url_for("reset_pass"))
    #     else:
    #         flash("Inalid OTP!","error")
    #         return redirect(url_for("forgot_pass"))

    # return render_template("otp.html")

@app.route("/reset_pass",methods=["GET","POST"])
def reset_pass():
    if "reset_email" not in session:
        flash("Please request an OTP first.", "error")
        return redirect(url_for("forgot_pass"))

    if request.method == "POST":
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password == confirm_password:
            conn = get_db()
            cursor = conn.cursor()

            new_pass = generate_password_hash(password)

            try:
                cursor.execute(
                    "Update Users Set Password_hash = %s Where email = %s ",
                    (new_pass,"reset_email") )
                conn.commit()
                session.pop("otp_email")
                flash("Passwords Changed Successfully")
                return redirect(url_for('sign_in'))
    
            except mysql.connector.Error:
                flash("Please try again later","error")
                return redirect(url_for("reset_pass"))
    
            finally:
                conn.close()
                cursor.close()

        else:
            flash("Enter the same Password","error")
            return redirect(url_for("reset_pass"))


    return render_template("reset_pass.html")



@app.route("/forgot_pass", methods=["GET", "POST"])
def forgot_pass():
    if request.method == "POST":
        email = request.form["email"].strip()

        conn = get_db()
        if conn is None:
            flash("Database configuration is offline.", "error")
            return redirect(url_for("forgot_pass"))

        cursor = conn.cursor(buffered=True)

        try:
            cursor.execute("SELECT email FROM Users WHERE email = %s", (email,))
            otp_email = cursor.fetchone()

            if otp_email:
                # 1. Generate the OTP
                real_otp = str(random.randint(100000, 999999))

                # 2. Save email and OTP into Flask Session so the next function can read it
                session["reset_email"] = email
                session["generated_otp"] = real_otp

                # 3. Send the Email
                # Note: For port 465, use smtplib.SMTP_SSL instead of starttls
                try:
                    msg = EmailMessage()
                    msg['Subject'] = "OTP Verification"
                    msg['From'] = os.environ["from_mail"]
                    msg['To'] = email
                    msg.set_content(f"Your OTP is: {real_otp}")

                    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                        server.login(os.environ["from_mail"],os.environ["mail_pass"])
                        server.send_message(msg)
                    
                    flash("OTP has been sent to your Email.", "success")
                    return redirect(url_for("OTP")) # Redirect to the verification page

                except Exception as e:
                    flash("Failed to send email. Try again later.", "error")
                    return redirect(url_for("forgot_pass"))

            else:
                flash("Enter a valid email!", "error")
                return redirect(url_for("forgot_pass"))

        except mysql.connector.Error:
            flash("Database error occurred.", "error")
            return redirect(url_for("forgot_pass"))
        
        finally:
            cursor.close()
            conn.close()

    return render_template("forgot_pass.html")


# --- 2. SECOND ROUTE: VERIFY THE USER'S INPUT ---
@app.route("/OTP", methods=["GET", "POST"])
def OTP():
    # Security check: Make sure they actually came from the forgot password page
    if "generated_otp" not in session:
        flash("Please request an OTP first.", "error")
        return redirect(url_for("forgot_pass"))

    if request.method == "POST":
        user_otp = request.form["OTP"].strip()
        real_otp = session.get("generated_otp")

        if user_otp == real_otp:
            flash("OTP Verified successfully!", "success")
            # Keep session['reset_email'] active so reset_pass route knows WHO is changing it
            # Remove OTP so it can't be used twice
            session.pop("generated_otp", None) 
            return redirect(url_for("reset_pass"))
        else:
            flash("Invalid OTP! Please try again.", "error")
            return redirect(url_for("OTP"))

    return render_template("otp.html")


# @app.route("/forgot_pass", methods=["POST","GET"])
# def forgot_pass():
#     if request.method == "POST":
#         email = request.form["email"].strip()

#         conn = get_db()
#         if conn is None:
#             flash("Database configuration is offline.", "error")
#             return redirect(url_for("forgot_pass"))

#         cursor = conn.cursor(buffered=True)

#         try:
#             cursor.execute(
#                 "Select email From Users Where email = %s",
#                 (email,)
#             )

#             otp_email = cursor.fetchone()

#             if otp_email:

#                 def OTP():
#                     if request.method == "POST":
#                         user_otp = request.form["OTP"]

#                         real_OTP = random.randint(000000,999999)

#                         server = smtplib.SMTP('smtp.gmail.com',465)
#                         server.starttls()

#                         from_mail = 'hasnat.dogar123@gmail.com'
#                         server.login = (from_mail,'bwri ukdb foqi omao')
#                         to_mail = request.form["email"].strip()

#                         msg = EmailMessage()
#                         msg['Subject'] = "OTP Verification"
#                         msg['From'] = from_mail
#                         msg['To'] = to_mail
#                         msg.set_content("Your OTP is : ", real_OTP)

#                         server.send_message(msg)
#                         flash("OTP is sent to your Email")

#                         if user_otp == real_OTP:
#                             flash("OTP Verified successfully","success")
#                             return redirect(url_for("reset_pass"))
#                         else:
#                             flash("Inalid OTP!","error")
#                             return redirect(url_for("forgot_pass"))

#                     return render_template("otp.html")

#                 conn.commit()
#                 return redirect(url_for("OTP"))

#             else:
#                 flash("Enter the Valid Emial!","error")
#                 return redirect(url_for("forgot_pass"))

#         except mysql.connector.Error:
#             flash("Enter a Valid Email", "error")
#             return redirect(url_for("forgot_pass"))
        
#         finally:
#             cursor.close()
#             conn.close()

#     return render_template("forgot_pass.html")


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

            session["new_user"] = username
            return redirect(url_for("submit"))
    
        except mysql.connector.IntegrityError:
            flash("Username or email already exists.", "error")
            return redirect(url_for("signup"))
        
        finally:
            cursor.close()
            conn.close()

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

# if __name__ == "__main__":
#     app.run(debug=True)
