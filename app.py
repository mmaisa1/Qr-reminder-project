from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
from flask_mail import Mail, Message
from datetime import datetime
import qrcode
import io
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
import os
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
import random
from datetime import timedelta

# Configure logging
log_handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
log_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler.setFormatter(formatter)

app = Flask(__name__)
app.logger.addHandler(log_handler)
app.logger.setLevel(logging.INFO)

load_dotenv()

app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.permanent_session_lifetime = timedelta(minutes=10)

# Mail config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

# --- Database setup ---
def init_db():
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            reminder_datetime TEXT NOT NULL,
            sent INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# --- Email sender ---
def send_email(reminder_id, username, title, description, email, repeat='none'):
    with app.app_context():
        try:
            formatted_body = f"""
Hello {username},

This is a friendly reminder about {title}.

{description}

Regards,
Team
            """
            msg = Message(title, sender=app.config['MAIL_USERNAME'], recipients=[email])
            msg.body = formatted_body
            mail.send(msg)

            conn = sqlite3.connect('reminders.db')
            c = conn.cursor()

            if repeat == 'none':
                c.execute('UPDATE reminders SET sent = 1 WHERE id = ?', (reminder_id,))
            else:
                from datetime import timedelta
                conn2 = sqlite3.connect('reminders.db')
                c2 = conn2.cursor()
                c2.execute('SELECT reminder_datetime FROM reminders WHERE id = ?', (reminder_id,))
                row = c2.fetchone()
                conn2.close()

                current_dt = datetime.strptime(row[0], '%Y-%m-%d %H:%M')

                if repeat == 'daily':
                    next_dt = current_dt + timedelta(days=1)
                elif repeat == 'weekly':
                    next_dt = current_dt + timedelta(weeks=1)
                elif repeat == 'monthly':
                    from dateutil.relativedelta import relativedelta
                    next_dt = current_dt + relativedelta(months=1)

                next_dt_str = next_dt.strftime('%Y-%m-%d %H:%M')
                c.execute('UPDATE reminders SET reminder_datetime = ? WHERE id = ?', (next_dt_str, reminder_id))

            conn.commit()
            conn.close()

            app.logger.info(f"Email sent to {email} for reminder '{title}', repeat: {repeat}")
        except Exception as e:
            app.logger.error(f"Error sending email: {e}")

# --- Scheduler job ---
def check_reminders():
    with app.app_context():
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        conn = sqlite3.connect('reminders.db')
        c = conn.cursor()
        c.execute('''
            SELECT id, username, title, description, email, repeat
            FROM reminders
            WHERE sent = 0 AND reminder_datetime <= ?
        ''', (now,))
        due = c.fetchall()
        conn.close()

        for row in due:
            reminder_id, username, title, description, email, repeat = row
            send_email(reminder_id, username, title, description, email, repeat)

# --- Routes ---
@app.route('/')
def qr_code_page():
    app.logger.info('Rendering QR code page')
    return render_template('qrcode.html')

@app.route('/set-reminder')
def set_reminder():
    app.logger.info('Rendering reminder form')
    return render_template('index.html')

@app.route('/create-reminder', methods=['POST'])
def create_reminder():
    try:
        username = request.form['username']
        email = request.form['email']
        title = request.form['title']
        description = request.form['description']
        reminder_date = request.form['reminder_date']
        reminder_time = request.form['reminder_time']

        reminder_datetime = f"{reminder_date} {reminder_time}"
        repeat = request.form.get('repeat', 'none')
        
        conn = sqlite3.connect('reminders.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO reminders (username, email, title, description, reminder_datetime, repeat)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, email, title, description, reminder_datetime, repeat))
        conn.commit()
        conn.close()

        app.logger.info(f"Reminder saved for {username} at {reminder_datetime}")
        return render_template('success.html', username=username)

    except Exception as e:
        app.logger.error(f"Error: {e}")
        return f"<h2>Error: {e}</h2>", 500

# --- QR code route ---
@app.route('/qr-code')
def generate_qr():
    url = os.getenv('URL')
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white').convert('RGB')
    img = img.resize((300, 300))
    img_with_corners = img.copy()
    corner_radius = 30

    for x in range(img.size[0]):
        for y in range(img.size[1]):
            if (
                x < corner_radius and y < corner_radius
            ) or (
                x < corner_radius and y >= img.size[1] - corner_radius
            ) or (
                x >= img.size[0] - corner_radius and y < corner_radius
            ) or (
                x >= img.size[0] - corner_radius and y >= img.size[1] - corner_radius
            ):
                img_with_corners.putpixel((x, y), (255, 255, 255))

    img_io = io.BytesIO()
    img_with_corners.save(img_io, 'PNG')
    img_io.seek(0)

    app.logger.info('Generated QR code')
    return send_file(img_io, mimetype='image/png')

import random

@app.route('/manage-reminders')
def manage_reminders():
    return render_template('manage_reminders.html')

@app.route('/send-otp', methods=['POST'])
def send_otp():
    email = request.form['email']

    # Check if email has any reminders
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute('SELECT id FROM reminders WHERE email = ?', (email,))
    exists = c.fetchone()
    conn.close()

    if not exists:
        flash('No reminders found for this email.', 'error')
        return redirect(url_for('manage_reminders'))

    # Generate OTP
    otp = str(random.randint(100000, 999999))
    expires_at = datetime.now().strftime('%Y-%m-%d %H:%M')

    # Save OTP to DB
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO otp_store (email, otp, expires_at)
        VALUES (?, ?, ?)
    ''', (email, otp, expires_at))
    conn.commit()
    conn.close()

    # Send OTP email
    try:
        msg = Message(
            'Your OTP for Reminder Access',
            sender=app.config['MAIL_USERNAME'],
            recipients=[email]
        )
        msg.body = f"Your OTP is: {otp}\n\nIt expires in 10 minutes. Do not share it with anyone."
        mail.send(msg)
        app.logger.info(f"OTP sent to {email}")
    except Exception as e:
        app.logger.error(f"Error sending OTP: {e}")
        flash('Error sending OTP. Please try again.', 'error')
        return redirect(url_for('manage_reminders'))

    return render_template('verify_otp.html', email=email)

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    email = request.form['email']
    otp_entered = request.form['otp']

    conn = sqlite3.connect('reminders.db')
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
        return redirect(url_for('manage_reminders'))

    otp_actual, expires_at = row
    expires_dt = datetime.strptime(expires_at, '%Y-%m-%d %H:%M')

    # Check expiry — 10 minutes
    if (datetime.now() - expires_dt).total_seconds() > 600:
        conn.close()
        flash('OTP expired. Please request a new one.', 'error')
        return redirect(url_for('manage_reminders'))

    if otp_entered != otp_actual:
        conn.close()
        flash('Incorrect OTP. Please try again.', 'error')
        return render_template('verify_otp.html', email=email)

    # Mark OTP as used
    c.execute('UPDATE otp_store SET used = 1 WHERE email = ? AND used = 0', (email,))
    conn.commit()
    conn.close()

    session['verified_email'] = email
    session.permanent = True

    return redirect(url_for('my_reminders'))

@app.route('/my-reminders')
def my_reminders():
    email = session.get('verified_email')
    if not email:
        flash('Session expired. Please verify again.', 'error')
        return redirect(url_for('manage_reminders'))

    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute('''
        SELECT id, username, title, description, reminder_datetime, repeat, sent
        FROM reminders WHERE email = ?
        ORDER BY reminder_datetime ASC
    ''', (email,))
    reminders = c.fetchall()
    conn.close()

    return render_template('my_reminders.html', reminders=reminders)

@app.route('/logout')
def logout():
    session.pop('verified_email', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('set_reminder'))
    
@app.route('/delete-reminder/<int:reminder_id>', methods=['POST'])
def delete_reminder(reminder_id):
    conn = sqlite3.connect('reminders.db')
    c = conn.cursor()
    c.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))
    conn.commit()
    conn.close()
    flash('Reminder deleted.', 'success')
    return redirect(url_for('set_reminder'))

if __name__ == '__main__':
    init_db()
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_reminders, 'interval', minutes=1)
    scheduler.start()
    app.run(host='0.0.0.0', port=5000, debug=True)