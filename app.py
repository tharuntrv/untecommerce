from flask import Flask, send_from_directory, request, redirect, url_for, flash
import random
import smtplib
import json
import os

app = Flask(__name__, static_url_path='/images', static_folder='images')
app.secret_key = 'ydajkkagidbxghio9ujzm'

# Helper function to read HTML files
def read_html_file(filename):
    with open(filename, 'r') as file:
        return file.read()

@app.route('/')
def index():
    return read_html_file('index.html')

# Add a route to serve static files
@app.route('/<filename>')
def serve_static(filename):
    return send_from_directory(os.path.abspath(os.path.dirname(__file__)), filename)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']

        # Check if the user is registered
        if not user_is_registered(email):
            return "User not registered. Please register first."

        # Generate OTP and send email
        OTP = generate_and_send_otp(email)

        # Save user info for OTP verification
        save_user_info(email, OTP)

        return redirect(url_for('verify_otp', email=email))

    return read_html_file('login.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        email = request.form['email'].lower()  # Normalize entered email to lowercase
        received_otp = int(request.form['otp'])

        # Check if the user is registered
        if not user_is_registered(email):
            flash("User not registered. Please register first.")
            return redirect(url_for('login'))

        saved_otp = get_saved_otp(email)

        if received_otp == saved_otp:
            return redirect(url_for('catalog'))
        else:
            flash("Invalid OTP. Please try again.")
            return redirect(url_for('login'))

    email = request.args.get('email')

    return read_html_file('verify_otp.html').replace('{{email}}', email)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if the user is already registered
        if user_is_registered(email):
            return "User already registered. Please log in or use a different email."

        # Generate OTP and send email
        OTP = generate_and_send_otp(email)

        # Save user info for OTP verification
        save_user_info(email, OTP)

        # Save user credentials (you might want to hash the password in a real application)
        save_user_credentials(username, email, password)

        return redirect(url_for('verify_otp', email=email))

    return read_html_file('register.html')

@app.route('/catalog')
def catalog():
    return read_html_file('catalog.html')

def generate_and_send_otp(email):
    OTP = random.randint(100000, 999999)

    body = f"Dear {email},\n\nYour OTP is {OTP}."
    subject = "OTP verification from Ecommerce"
    message = f'subject:{subject}\n\n{body}'

    # Add your email and password for SMTP login
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("josephmakaumunyao40@gmail.com", "sruq ywfg caqh sbvz")
    server.sendmail("josephmakaumunyao40@gmail.com", email, message)
    server.quit()

    return OTP

def email_verification(email):
    email_check1 = ["gmail", "hotmail", "yahoo", "outlook"]
    email_check2 = [".com", ".in", ".org", ".edu", ".co.in"]
    count = 0

    for domain in email_check1:
        if domain in email:
            count += 1
    for site in email_check2:
        if site in email:
            count += 1

    if "@" not in email or count != 2:
        print("Invalid email id")
        new_email = input("Enter correct email id:")
        return email_verification(new_email)
    else:
        return email.lower()  # Save email in lowercase for consistency

def save_user_info(email, otp):
    try:
        with open('users.json', 'r') as file:
            users = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        users = {}

    users[email] = otp

    with open('users.json', 'w') as file:
        json.dump(users, file)

def get_saved_otp(email):
    try:
        with open('users.json', 'r') as file:
            users = json.load(file)
            return users.get(email, 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

def user_is_registered(email):
    try:
        with open('users.json', 'r') as file:
            users = json.load(file)
            return email in users
    except (FileNotFoundError, json.JSONDecodeError):
        return False

def save_user_credentials(username, email, password):
    try:
        with open('credentials.json', 'r') as file:
            credentials = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        credentials = []

    credentials.append({
        'username': username,
        'email': email,
        'password': password
    })

    with open('credentials.json', 'w') as file:
        json.dump(credentials, file)

if __name__ == '__main__':
    app.run(debug=True)
