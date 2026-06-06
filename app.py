from flask import Flask
from database import init_db
from routes.qr import qr_bp
from routes.reminders import reminders_bp
from routes.auth import auth_bp
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import os
import sqlite3
import pytz

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.secret_key = os.getenv('FLASK_SECRET_KEY')
    app.permanent_session_lifetime = timedelta(minutes=10)

    # Logging
    log_handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
    log_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_handler.setFormatter(formatter)
    app.logger.addHandler(log_handler)
    app.logger.setLevel(logging.INFO)

    # Blueprints
    app.register_blueprint(qr_bp)
    app.register_blueprint(reminders_bp)
    app.register_blueprint(auth_bp)

    init_db()

    return app


def send_email(reminder_id, username, title, description, email, repeat='none'):
    app = create_app()
    with app.app_context():
        try:
            from extensions import send_brevo_email

            formatted_body = f"""
Hello {username},

This is a friendly reminder about {title}.

{description}

Regards,
Team
            """

            send_brevo_email(
                to=email,
                subject=title,
                body=formatted_body
            )

            conn = sqlite3.connect('reminders.db')
            c = conn.cursor()

            if repeat == 'none':
                c.execute('UPDATE reminders SET sent = 1 WHERE id = ?', (reminder_id,))
            else:
                c.execute('SELECT reminder_datetime FROM reminders WHERE id = ?', (reminder_id,))
                row = c.fetchone()
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

def check_reminders():
    app = create_app()
    with app.app_context():
        now = datetime.now(pytz.UTC).strftime('%Y-%m-%d %H:%M')
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


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)