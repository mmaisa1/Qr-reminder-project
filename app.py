from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_mail import Mail, Message
from datetime import datetime
import threading
import time
import qrcode
import io

app = Flask(__name__)
app.secret_key = '1989f15fb5f5df6ae5ffb51a3b5157f2'  # Replace with your generated secret key

# Configuration for Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'medhamaisa.usa@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'wkkz rlnp izay hzdz'  # Replace with your email password
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

def send_email(subject, body, recipient, send_time):
    time_diff = (send_time - datetime.now()).total_seconds()
    if time_diff > 0:
        time.sleep(time_diff)

    msg = Message(subject, sender=app.config['MAIL_USERNAME'], recipients=[recipient])
    msg.body = body
    try:
        with app.app_context():
            mail.send(msg)
    except Exception as e:
        print(f"Error sending email: {e}")

@app.route('/')
def index():
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
        threading.Thread(target=send_email, args=(title, description, email, reminder_datetime)).start()

        flash('Reminder set successfully!', 'success')
    except ValueError as ve:
        flash(f'Error: {ve}', 'error')
    except Exception as e:
        flash(f'Error: {e}', 'error')

    return redirect(url_for('index'))

# Route to generate the QR code
@app.route('/qr-code')
def generate_qr():
    # URL of the form (local link for now)
    url = 'http://192.168.86.221:5000/'

    # Generate the QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)

    # Create an image from the QR code
    img = qr.make_image(fill='black', back_color='white')

    # Save the image in a BytesIO object to send it as a file
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
