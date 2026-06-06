# QRemind

Scan a QR code, set a reminder, get an email when it's time. 
No account needed — just your email.

**Live demo:** https://qremind.onrender.com

Built this project to get hands-on with Flask, databases, and email delivery outside of tutorials.

## How it works

You scan a QR code, fill out a quick form, and QRemind emails you at the time you set. Reminders can repeat daily, weekly, or monthly. No account needed.

To manage your reminders, you verify with a one-time password sent to your email.

## Features

- Set reminders with a title, description, date and time
- Repeat options: one time, daily, weekly, monthly
- Email delivery via Brevo
- OTP-based reminder management — view and delete your reminders
- Session handling with 10 minute expiry
- QR code generation linking directly to the reminder form

## Tech stack

- Python / Flask
- SQLite (development — PostgreSQL recommended for production)
- Brevo (transactional email)
- APScheduler
- Jinja2
- pytz

## Project structure

```
QRemind/
│
├── app.py                    # app factory, email sender, scheduler logic
├── extensions.py             # brevo email helper
├── database.py               # db connection and table setup
├── migrate.py                # run manually for schema changes
├── gunicorn_config.py        # gunicorn hooks for scheduler startup
├── routes/
│   ├── __init__.py
│   ├── qr.py                 # qr code generation and landing page
│   ├── reminders.py          # create, view, delete reminders
│   └── auth.py               # otp flow and session management
├── templates/
│   ├── qrcode.html
│   ├── index.html
│   ├── success.html
│   ├── manage_reminders.html
│   ├── verify_otp.html
│   └── my_reminders.html
├── static/
│   └── styles.css
├── ENHANCEMENTS.md
├── PRODUCTION_INCIDENTS.md
├── requirements.txt
└── .env                      # not committed
```

## Running locally

```bash
git clone https://github.com/mmaisa1/Qr-reminder-project.git
cd Qr-reminder-project
pip install -r requirements.txt
```

Create a `.env` file:
```
FLASK_SECRET_KEY=your_secret_key
BREVO_API_KEY=your_brevo_api_key
BREVO_SENDER_EMAIL=your_sender_email
URL=http://your_local_ip:5000/set-reminder
```
Then run:

```bash
python migrate.py
python app.py
```

## What's next

See `ENHANCEMENTS.md` for planned improvements.
