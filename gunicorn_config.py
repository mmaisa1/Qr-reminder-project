from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import sqlite3
import pytz

scheduler = BackgroundScheduler()

def on_starting(server):
    from app import check_reminders
    scheduler.add_job(check_reminders, 'interval', minutes=1)
    scheduler.start()

def on_exit(server):
    scheduler.shutdown()