from flask import Flask, render_template, request, redirect, url_for
from flask_mail import Mail, Message
from datetime import datetime
import threading
import time

app = Flask(__name__)

# Configuration for Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.example.com'  # Replace with your SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your_email@example.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'your_password'  # Replace with your email password
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

def send_email(subject, body, recipient, send_time):
    time_diff = (send_time - datetime.now()).total_seconds()
    if time_diff > 0:
        time.sleep(time_diff)

    msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[recipient])
    msg.body = body
    with app.app_context():
        mail.send(msg)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create-reminder', methods=['POST'])
def create_reminder():
    username = request.form['username']
    email = request.form['email']
    title = request.form['title']
    description = request.form['description']
    reminder_date = request.form['reminder_date']
    reminder_time = request.form['reminder_time']

    # Combine date and time into a datetime object
    reminder_datetime = datetime.strptime(f"{reminder_date} {reminder_time}", '%Y-%m-%d %H:%M')

    # Send email at the specified time using a separate thread
    threading.Thread(target=send_email, args=(title, description, email, reminder_datetime)).start()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
