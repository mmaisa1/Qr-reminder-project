# QRemind

Scan a QR code, set a reminder, get an email when it's time. 
No account needed — just your email.

**Live demo:** https://qremind.onrender.com

Built this project to get hands-on with Flask, databases, and email delivery outside of tutorials.

## How it works

You scan a QR code, fill out a quick form, and QRemind emails you at the time you set. Reminders can repeat daily, weekly, or monthly. No account needed.

To manage your reminders, you verify with a one-time password sent to your email. Kept auth intentionally lightweight — OTP over email felt like the right tradeoff for an app that doesn't need a full user system.

## Features

- Set reminders with a title, description, date and time
- Repeat options — one time, daily, weekly, monthly
- Email delivery via Gmail SMTP
- OTP-based reminder management — view and delete your reminders
- Session handling with 10 minute expiry
- QR code generation linking directly to the reminder form

## Tech stack

- Python / Flask
- SQLite (development — PostgreSQL recommended for production)
- Flask-Mail
- APScheduler
- Jinja2

## Project structure

```
QRemind/
│
├── app.py              # app factory, scheduler, db init
├── extensions.py       # mail instance
├── database.py         # db connection and table setup
├── migrate.py          # run manually for schema changes
├── routes/
│   ├── qr.py           # qr code generation and landing page
│   ├── reminders.py    # create, view, delete reminders
│   └── auth.py         # otp flow and session management
├── templates/
├── static/
└── .env                # not committed
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
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_gmail_app_password
URL=http://your_local_ip:5000/set-reminder
```
Then run:

```bash
python migrate.py
python app.py
```

## What's next

See `ENHANCEMENTS.md` for planned improvements.
