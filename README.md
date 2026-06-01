# QR Reminder Project

## Overview
The QR Reminder Project is a Flask-based web application that allows users to set reminders and receive email notifications. Users can generate a QR code that links to a form for entering reminder details, making it easy to access the form on any device.

## Features
- Generate QR codes that link to a reminder form.
- Set reminders with a specified date and time.
- Receive email notifications for reminders.
- User-friendly interface accessible from any device.

## Requirements
- Python 3.x
- Flask
- Flask-Mail
- qrcode
- python-dotenv

## Installation
1. **Clone the repository:**
   ```bash
   git clone git@github.com:mmaisa1/Qr-reminder-project.git
   cd Qr-reminder-project
   ```

2. **Set up a virtual environment (optional but recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file:**
   ```plaintext
   FLASK_SECRET_KEY="your_secret_key"
   MAIL_USERNAME="your_email@gmail.com"
   MAIL_PASSWORD="your_email_password"
   URL="http://your_public_ip:5000/secret-form"
   ```

## Running the Application
1. **Start the Flask server:**
   ```bash
   python3 app.py
   ```

2. **Access the application:**
   Open your web browser and navigate to `http://your_public_ip:5000/` to access the QR code and reminder form.

## Usage
1. Scan the generated QR code with your mobile device.
2. Fill out the reminder form and submit it.
3. You will receive an email notification at the specified reminder time.
