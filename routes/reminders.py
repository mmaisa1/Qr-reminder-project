from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from database import get_db
from datetime import datetime, timedelta
import pytz

reminders_bp = Blueprint('reminders', __name__)

@reminders_bp.route('/set-reminder')
def set_reminder():
    current_app.logger.info('Rendering reminder form')
    return render_template('index.html')

@reminders_bp.route('/create-reminder', methods=['POST'])
def create_reminder():
    try:
        username = request.form['username']
        email = request.form['email']
        title = request.form['title']
        description = request.form['description']
        reminder_date = request.form['reminder_date']
        reminder_time = request.form['reminder_time']
        repeat = request.form.get('repeat', 'none')
        timezone_str = request.form.get('timezone', 'UTC')

        reminder_datetime = f"{reminder_date} {reminder_time}"
        reminder_datetime_obj = datetime.strptime(reminder_datetime, '%Y-%m-%d %H:%M')

        try:
            user_tz = pytz.timezone(timezone_str)
        except pytz.UnknownTimeZoneError:
            user_tz = pytz.UTC

        reminder_datetime_utc = user_tz.localize(reminder_datetime_obj).astimezone(pytz.UTC)

        if reminder_datetime_utc < datetime.now(pytz.UTC) + timedelta(minutes=1):
            flash('Please select a time at least 1 minute from now.', 'error')
            return redirect(url_for('reminders.set_reminder'))

        reminder_datetime_str = reminder_datetime_utc.strftime('%Y-%m-%d %H:%M')

        conn = get_db()
        c = conn.cursor()
        c.execute('''
            INSERT INTO reminders (username, email, title, description, reminder_datetime, repeat)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, email, title, description, reminder_datetime_str, repeat))
        conn.commit()
        conn.close()

        current_app.logger.info(f"Reminder saved for {username} at {reminder_datetime_str} UTC")
        return render_template('success.html', username=username)

    except Exception as e:
        current_app.logger.error(f"Error: {e}")
        return f"<h2>Error: {e}</h2>", 500

@reminders_bp.route('/my-reminders')
def my_reminders():
    email = session.get('verified_email')
    if not email:
        flash('Session expired. Please verify again.', 'error')
        return redirect(url_for('auth.manage_reminders'))

    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT id, username, title, description, reminder_datetime, repeat, sent
        FROM reminders WHERE email = ?
        ORDER BY reminder_datetime ASC
    ''', (email,))
    reminders = c.fetchall()
    conn.close()

    return render_template('my_reminders.html', reminders=reminders)

@reminders_bp.route('/delete-reminder/<int:reminder_id>', methods=['POST'])
def delete_reminder(reminder_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))
    conn.commit()
    conn.close()
    flash('Reminder deleted.', 'success')
    return redirect(url_for('reminders.my_reminders'))