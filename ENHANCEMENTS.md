# Enhancements Backlog

## Security
- [ ] OTP cleanup job — delete used/expired OTPs older than 24 hours from otp_store

## Features
- [ ] Edit reminder — allow users to update datetime or description from my-reminders page

## Infrastructure
- [ ] Replace SQLite with PostgreSQL for production
- [ ] Add Redis caching for OTP storage
- [ ] Rate limiting on /send-otp to prevent abuse

## UX
- [ ] Mobile responsive design
- [ ] Search and filter on my-reminders page