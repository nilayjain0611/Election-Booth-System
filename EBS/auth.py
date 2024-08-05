# auth.py
import pyotp
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from .models import Voter, SuperUser
from flask_mail import Message
from . import db, mail  

auth = Blueprint('auth', __name__)

# voter login endpoint
@auth.route('/login')
def login():
    return render_template('login.html')

# admin login endpoint
@auth.route('/login-admin')
def loginAdmin():
    return render_template('login-admin.html')

# admin user logged in API
@auth.route('/login-admin', methods=['POST'])
def login_post_admin():
    email = request.form.get('email')
    password = request.form.get('password')
    
    superuser = SuperUser.query.filter_by(email=email).first()

    print(superuser)
    if superuser and superuser.password == password:
        login_user(superuser)
        flash('Logged in as SuperUser', 'success')
        print('Logged in as SuperUser', 'success')
        
        return redirect(url_for('elections.election_dashboard'))
    else:
        flash('Invalid Credentials', 'danger')
        print('Invalid Credentials', 'danger')
        return redirect(url_for('auth.loginAdmin'))
    
# Voter user loggedin API
@auth.route('/login', methods=['POST'])
def login_post_voter():
    email = request.form.get('email')
    voter = Voter.query.filter_by(email=email).first()

    if voter:
        # Generate a new TOTP secret for each login
        totp = pyotp.TOTP(pyotp.random_base32())
        otp = totp.now()

        # Store the TOTP secret in the database
        voter.otp_secret = totp.secret
        voter.otp = otp
        db.session.commit()

        print("----------------------OTP is: ",otp,"----------------------")
        
        # Send the OTP to the voter via email
        send_otp_email(voter.email, otp)

        # Redirect to OTP verification page
        return render_template('otp_verification.html', voter_id=voter.id)

    flash('Invalid Credentials', 'danger')
    return redirect(url_for('auth.login'))




def send_otp_email(recipient, otp):
    subject = 'Your OTP for Login'
    body = f'Your OTP is: {otp}'

    message = Message(subject, recipients=[recipient], body=body)

    try:
        mail.send(message)
        print(f"OTP sent to {recipient} successfully.")
    except Exception as e:
        print(f"Error sending OTP to {recipient}: {str(e)}")

@auth.route('/verify-otp/<string:voter_id>', methods=['POST'])
def verify_otp(voter_id):
    voter = Voter.query.get(voter_id)
    print(f"Voter ID from URL: {voter_id}")
    print(f"Voter: {voter}")
    if voter:
        otp = voter.otp
        otp_entered = request.form.get('otp')
        print(f"~~~~~~~~~~~~~~~~~~~~~~~~~OTP Entered: {otp_entered}~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(f"~~~~~~~~~~~~~~~~~~~~~~~~OTP from database: {otp}~~~~~~~~~~~~~~~~~~~~~~~")
        
        if otp==int(otp_entered):
            login_user(voter)
            flash('Logged in as Voter', 'success')
            print('Logged in as Voter', 'success')
            voter.otp_secret = None
            voter.otp = None
            db.session.commit()
            return redirect(url_for('elections.election_dashboard'))
    flash('Invalid OTP danger')
    print('Invalid OTP', 'danger')
    return redirect(url_for('auth.login'))

# logout endpoint
@auth.route('/logout')
@login_required
def logout():
    flash('Logged Out !!', 'success')
    logout_user()
    
    return redirect(url_for('main.index'))