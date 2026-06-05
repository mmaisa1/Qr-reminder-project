# QRemind: Enhancements Backlog

## Security
- [ ] OTP cleanup job: delete used/expired OTPs older than 24 hours from otp_store
- [ ] Rate limiting on /send-otp: restrict to 3 requests per minute per IP

## Features
- [ ] Edit reminder: update datetime or description from my-reminders page
- [ ] Confirmation dialog before deleting a reminder
- [ ] Confirmation message after submitting email on manage reminders page

## Infrastructure
- [ ] Replace SQLite with PostgreSQL for production
- [ ] Migrate OTP storage to Redis with TTL auto-expiry
- [ ] Add Docker support
- [ ] Offload scheduler to external cron trigger or always-on background worker

## UX
- [ ] Timezone support: store and convert reminder times to user's local timezone
- [ ] Search and filter on my-reminders page
- [ ] Mobile responsive design improvements
