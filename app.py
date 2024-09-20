from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_mail import Mail, Message
from datetime import datetime
import threading
import time
import qrcode
import io
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
log_handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
log_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler.setFormatter(formatter)

# Add the file handler to the app's logger
app = Flask(__name__)
app.logger.addHandler(log_handler)

#9-20-24:1 Add a console handler to ensure logging shows up in the console as well
'''console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
app.logger.addHandler(console_handler)'''

#9-20-24:1  Set the logger's level explicitly to capture all messages
app.logger.setLevel(logging.INFO)

app.secret_key = '1989f15fb5f5df6ae5ffb51a3b5157f2'  # Replace with your generated secret key

# Configuration for Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'medhamaisa.usa@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'wkkz rlnp izay hzdz'  # Replace with your email password
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

def send_email(subject, body, recipient, username, title, send_time):
    time_diff = (send_time - datetime.now()).total_seconds()
    if time_diff > 0:
        time.sleep(time_diff)

    # Format the email body
    formatted_body = f"""
Hi {username},

This email is a friendly reminder about {title}.

{body}

Regards,
Team
    """

    msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[recipient])
    msg.body = formatted_body
    try:
        with app.app_context():
            mail.send(msg)
            app.logger.info(f"Email sent to {recipient} at '{send_time}'")
    except Exception as e:
        app.logger.error(f"Error sending email: {e}")


@app.route('/')
def qr_code_page():
    app.logger.info('Rendering QR code page')
    return render_template('qrcode.html')

@app.route('/secret-form')
def secret_form():
    app.logger.info('Rendering secret form page')
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

        # Combine date and time into a datetime object
        reminder_datetime = datetime.strptime(f"{reminder_date} {reminder_time}", '%Y-%m-%d %H:%M')

        # Send email at the specified time using a separate thread
        threading.Thread(
            target=send_email, 
            args=(title, description, email, username, title, reminder_datetime)
        ).start()

        flash('Reminder set successfully!', 'success')
        app.logger.info(f"Reminder set for {username} ({email}) at '{reminder_datetime}'")
    except ValueError as ve:
        flash(f'Error: {ve}', 'error')
        app.logger.error(f'ValueError: {ve}')
    except Exception as e:
        flash(f'Error: {e}', 'error')
        app.logger.error(f'Exception: {e}')

    return redirect(url_for('secret_form'))

# Route to generate the QR code
@app.route('/qr-code')
def generate_qr():
    # URL of the form
    url = 'http://172.20.10.7:5000/secret-form'

    # Generate the QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)

    # Create an image from the QR code
    img = qr.make_image(fill='black', back_color='white').convert('RGB')
    # Create a new image with curved corners
    img = img.resize((300, 300))
    img_with_corners = img.copy()
    corner_radius = 30

    # Draw the curved corners
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
    app.run(host='0.0.0.0', port=5000, debug=True)
