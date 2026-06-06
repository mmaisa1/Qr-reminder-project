from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from database import get_db
from flask_mail import Message
from datetime import datetime
import random
from extensions import send_brevo_email

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/manage-reminders')
def manage_reminders():
    return render_template('manage_reminders.html')

@auth_bp.route('/send-otp', methods=['POST'])
def send_otp():
    email = request.form['email']

    otp = str(random.randint(100000, 999999))
    expires_at = datetime.now().strftime('%Y-%m-%d %H:%M')

    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO otp_store (email, otp, expires_at)
        VALUES (?, ?, ?)
    ''', (email, otp, expires_at))
    conn.commit()
    conn.close()

    try:
        send_brevo_email(
            to=email,
            subject='Your OTP for Reminder Access',
            body=f"Your OTP is: {otp}\n\nIt expires in 10 minutes. Do not share it with anyone."
        )
        current_app.logger.info(f"OTP sent to {email}")
    except Exception as e:
        current_app.logger.error(f"Error sending OTP: {e}")
        flash('Error sending OTP. Please try again.', 'error')
        return redirect(url_for('auth.manage_reminders'))

    return render_template('verify_otp.html', email=email)

@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    email = request.form['email']
    otp_entered = request.form['otp']

    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT otp, expires_at FROM otp_store
        WHERE email = ? AND used = 0
        ORDER BY id DESC LIMIT 1
    ''', (email,))
    row = c.fetchone()

    if not row:
        conn.close()
        flash('OTP not found. Please request a new one.', 'error')
        return redirect(url_for('auth.manage_reminders'))

    otp_actual, expires_at = row[0], row[1]
    expires_dt = datetime.strptime(expires_at, '%Y-%m-%d %H:%M')

    if (datetime.now() - expires_dt).total_seconds() > 600:
        conn.close()
        flash('OTP expired. Please request a new one.', 'error')
        return redirect(url_for('auth.manage_reminders'))

    if otp_entered != otp_actual:
        conn.close()
        flash('Incorrect OTP. Please try again.', 'error')
        return render_template('verify_otp.html', email=email)

    c.execute('UPDATE otp_store SET used = 1 WHERE email = ? AND used = 0', (email,))
    conn.commit()
    conn.close()

    session['verified_email'] = email
    session.permanent = True

    return redirect(url_for('reminders.my_reminders'))

@auth_bp.route('/logout')
def logout():
    session.pop('verified_email', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('reminders.set_reminder'))