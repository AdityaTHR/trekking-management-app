# Trekking Management Application — V2

A role-based trekking management platform for **Admin**, **Trek Staff**, and **Trekkers**, built with Flask, Vue 3, SQLite, Redis, and Celery.

## Technology Stack

| Layer | Technology |
|---|---|
| Backend | Flask 3, Flask-SQLAlchemy, SQLite |
| Authentication | Flask-Security-Too, token-based RBAC |
| Frontend | Vue 3, Vue Router 4, Bootstrap 5 |
| Background jobs | Celery + Redis |
| Caching | Flask-Caching + Redis |
| Email testing | smtplib + Jinja2 templates + MailHog |
| Analytics | Chart.js |

## One-Time Setup

### Backend

```bash
cd backend
python3 -m venv .myenv
source .myenv/bin/activate
python -m pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

### Redis

```bash
sudo service redis-server start
redis-cli ping
```

Expected response: `PONG`.

## Run the Application

Use separate terminals.

### Flask API

```bash
cd backend
source .myenv/bin/activate
python app.py
```

### Vue Frontend

```bash
cd frontend
npm run serve
```

### Celery Worker

```bash
cd backend
source .myenv/bin/activate
celery -A app.celery worker --loglevel INFO
```

### Celery Beat

```bash
cd backend
source .myenv/bin/activate
celery -A app.celery beat --loglevel INFO
```

### MailHog

Run MailHog separately.

- SMTP: `localhost:1025`
- Browser inbox: `http://localhost:8025`

## Default Admin Login

- Email: `admin@trekking.com`
- Password: `Admin@123`

Staff accounts are created by Admin. Trekkers self-register.

## Core Features

1. Programmatic SQLite schema and predefined Admin
2. Token authentication and role-based access
3. Admin management of treks, staff, users, bookings, search, and blacklisting
4. Staff management restricted to assigned treks
5. Trekker browsing, filtering, booking, profile, and dashboard
6. Booking history, cancellation, status tracking, duplicate/overbooking prevention
7. Celery jobs for reminders, monthly HTML report, and async CSV export
8. Redis caching of open trek listings with timeout and invalidation

## Additional Features

- Active blacklist enforcement
- Server-side validation and transaction rollback
- Global Vue Router role guard
- Public landing page with one Chart.js difficulty chart
- Cache demonstration using `X-Cache: MISS` and `X-Cache: HIT`

PWA support was deliberately not implemented because it is optional.

## Redis Databases

- DB 0: Celery broker
- DB 1: Celery result backend
- DB 2: Flask API cache

## Submission Notes

- Keep the GitHub repository private.
- Do not commit `.myenv`, `node_modules`, databases, generated CSV files, `celerybeat-schedule`, or MailHog.
- Upload the report and video separately on the submission portal.
- The code ZIP must contain exactly one project folder at its root.
