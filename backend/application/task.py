import csv
import os
from datetime import datetime, timedelta

from celery import shared_task

from .models import db, User, Role, Trek, Booking
from .mail import send_email
from .utils import prepare_template

BACKEND_DIR = os.path.dirname(os.path.dirname(__file__))
TEMPLATES_DIR = os.path.join(BACKEND_DIR, "templates")
STATIC_DIR = os.path.join(BACKEND_DIR, "static")
os.makedirs(STATIC_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# 7a — Scheduled Job: Daily reminders for upcoming treks
# Runs daily (wired up in app.py via Celery Beat). Emails every trekker who
# holds an active ("Booked") booking for a trek starting in the next 3 days.
# ---------------------------------------------------------------------------
@shared_task(name="send_daily_trek_reminders", ignore_result=True)
def send_daily_trek_reminders():
    today = datetime.utcnow().date()
    window_end = today + timedelta(days=3)

    upcoming_bookings = (
        db.session.query(Booking)
        .join(Trek, Booking.trek_id == Trek.id)
        .filter(Booking.booking_status == "Booked")
        .filter(Trek.start_date.isnot(None))
        .filter(Trek.start_date >= today)
        .filter(Trek.start_date <= window_end)
        .all()
    )

    sent = 0
    mail_statuses = []
    for booking in upcoming_bookings:
        html = prepare_template(
            os.path.join(TEMPLATES_DIR, "trek-reminder-mail.html"),
            data={"user": booking.user, "trek": booking.trek},
        )
        status = send_email(booking.user.email, f"Upcoming Trek Reminder: {booking.trek.name}", html)
        mail_statuses.append(status)
        sent += 1

    return f"Sent {sent} reminder email(s). Mail statuses: {mail_statuses}"


# ---------------------------------------------------------------------------
# 7b — Scheduled Job: Monthly trekking activity report for Admin
# Runs on the 1st of every month (wired up in app.py). Reports on the
# PREVIOUS calendar month's completed treks.
# ---------------------------------------------------------------------------
@shared_task(name="generate_monthly_admin_report", ignore_result=True)
def generate_monthly_admin_report():
    today = datetime.utcnow().date()
    first_of_this_month = today.replace(day=1)
    last_day_prev_month = first_of_this_month - timedelta(days=1)
    first_day_prev_month = last_day_prev_month.replace(day=1)

    treks_conducted = (
        Trek.query.filter(Trek.status == "Completed")
        .filter(Trek.start_date.isnot(None))
        .filter(Trek.start_date >= first_day_prev_month)
        .filter(Trek.start_date <= last_day_prev_month)
        .all()
    )

    total_participants = sum(
        sum(1 for b in t.bookings if b.booking_status in ("Booked", "Completed"))
        for t in treks_conducted
    )

    popular_treks = sorted(treks_conducted, key=lambda t: len(t.bookings), reverse=True)[:5]

    html = prepare_template(
        os.path.join(TEMPLATES_DIR, "admin-monthly-report.html"),
        data={
            "month_label": first_day_prev_month.strftime("%B %Y"),
            "treks_conducted": treks_conducted,
            "total_participants": total_participants,
            "popular_treks": popular_treks,
        },
    )

    admin = User.query.join(User.roles).filter(Role.name == "admin").first()
    mail_status = "No admin found to email"
    if admin:
        mail_status = send_email(
            admin.email,
            f"Monthly Trekking Activity Report - {first_day_prev_month.strftime('%B %Y')}",
            html,
        )

    return f"Done. Mail status: {mail_status}"


# ---------------------------------------------------------------------------
# 7c — User-triggered async job: export booking history as CSV
# Triggered from the User Dashboard. The frontend polls /result/<task_id>
# and downloads the file from /static/<filename> once ready.
# ---------------------------------------------------------------------------
@shared_task(name="export_user_booking_history_csv", ignore_result=False)
def export_user_booking_history_csv(user_id):
    bookings = (
        Booking.query.filter_by(user_id=user_id)
        .order_by(Booking.id.desc())
        .all()
    )

    filename = f"booking-history-user-{user_id}.csv"
    filepath = os.path.join(STATIC_DIR, filename)

    with open(filepath, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["User ID", "Trek Name", "Location", "Booking Status", "Booking Date"])
        for b in bookings:
            writer.writerow([b.user_id, b.trek.name, b.trek.location, b.booking_status, b.booking_date])

    return filename
