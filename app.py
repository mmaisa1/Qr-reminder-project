from flask import Flask, render_template, request, redirect, url_for, flash, send_file
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
def send_email(reminder_id, username, title, description, email):
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

            # Mark as sent in DB
            conn = sqlite3.connect('reminders.db')
            c = conn.cursor()
            c.execute('UPDATE reminders SET sent = 1 WHERE id = ?', (reminder_id,))
            conn.commit()
            conn.close()

            app.logger.info(f"Email sent to {email} for reminder '{title}'")
        except Exception as e:
            app.logger.error(f"Error sending email: {e}")

# --- Scheduler job ---
def check_reminders():
    with app.app_context():
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        conn = sqlite3.connect('reminders.db')
        c = conn.cursor()
        c.execute('''
            SELECT id, username, title, description, email
            FROM reminders
            WHERE sent = 0 AND reminder_datetime <= ?
        ''', (now,))
        due = c.fetchall()
        conn.close()

        for row in due:
            reminder_id, username, title, description, email = row
            send_email(reminder_id, username, title, description, email)

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

        conn = sqlite3.connect('reminders.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO reminders (username, email, title, description, reminder_datetime)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, title, description, reminder_datetime))
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

if __name__ == '__main__':
    init_db()
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_reminders, 'interval', minutes=1)
    scheduler.start()
    app.run(host='0.0.0.0', port=5000, debug=True)