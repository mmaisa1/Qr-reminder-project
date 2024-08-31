from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

@app.route('/submit', methods=['POST'])
def submit_reminder():
    data = request.form
    # Extract form data
    username = data.get('username')
    email = data.get('email')
    heading = data.get('heading')
    description = data.get('description')
    alerts = data.getlist('alerts')

    # Process and schedule reminders (simple placeholder logic)
    for alert in alerts:
        # Convert alert to timedelta
        if alert == '1 day before':
            alert_time = timedelta(days=1)
        elif alert == '1 hour before':
            alert_time = timedelta(hours=1)
        elif alert == '5 minutes before':
            alert_time = timedelta(minutes=5)
        elif alert == '10 minutes before':
            alert_time = timedelta(minutes=10)

        send_time = datetime.now() + alert_time
        # Send email (placeholder logic)
        send_email(email, heading, description)

    return jsonify({'message': 'Reminder created successfully!'})

def send_email(recipient, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'your_email@example.com'
    msg['To'] = recipient

    with smtplib.SMTP('smtp.example.com') as server:
        server.login('your_email@example.com', 'your_password')
        server.send_message(msg)

if __name__ == '__main__':
    app.run(debug=True)
