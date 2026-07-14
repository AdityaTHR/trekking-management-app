from datetime import datetime
from flask import current_app as app
from .models import db, User, Role, StaffProfile, Trek, Booking
from flask import request
from flask_security import auth_required, roles_required, current_user
from flask_security.utils import hash_password, verify_password
from celery.result import AsyncResult
from .task import (
    export_user_booking_history_csv,
    generate_monthly_admin_report,
    send_daily_trek_reminders,
)


# ---------------------------------------------------------------------------
# Small serialization helpers (kept as plain functions, same flat style as
# the reference app — no Marshmallow/serializer library introduced)
# ---------------------------------------------------------------------------
def trek_to_dict(trek):
    return {
        "id": trek.id,
        "name": trek.name,
        "location": trek.location,
        "difficulty": trek.difficulty,
        "duration": trek.duration,
        "available_slots": trek.available_slots,
        "start_date": trek.start_date.isoformat() if trek.start_date else None,
        "end_date": trek.end_date.isoformat() if trek.end_date else None,
        "status": trek.status,
        "assigned_staff_id": trek.assigned_staff_id,
        "assigned_staff_name": trek.assigned_staff.name if trek.assigned_staff else None,
        "registered_count": sum(1 for b in trek.bookings if b.booking_status == "Booked"),
    }


def user_to_dict(user):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "contact_number": user.contact_number,
        "status": user.status,
        "role": user.roles[0].name if user.roles else None,
    }


def booking_to_dict(b):
    return {
        "id": b.id,
        "user_id": b.user_id,
        "user_name": b.user.name,
        "trek_id": b.trek_id,
        "trek_name": b.trek.name,
        "booking_date": b.booking_date.isoformat() if b.booking_date else None,
        "booking_status": b.booking_status,
        "payment_status": b.payment_status,
    }


@app.route("/")
def home():
    return "Trekking Management Application API"


# ---------------------------------------------------------------------------
# Redis caching helpers (Milestone 8)
# Cache the complete list of open treks once, then apply user filters in
# Python. Every operation that can change the listing invalidates this key.
# ---------------------------------------------------------------------------
OPEN_TREKS_CACHE_KEY = "open-treks"
OPEN_TREKS_CACHE_TIMEOUT = 60


def get_open_treks_cached():
    cached = app.cache.get(OPEN_TREKS_CACHE_KEY)
    if cached is not None:
        return cached, True

    treks = Trek.query.filter_by(status="Open").all()
    data = [trek_to_dict(trek) for trek in treks]
    app.cache.set(
        OPEN_TREKS_CACHE_KEY,
        data,
        timeout=OPEN_TREKS_CACHE_TIMEOUT,
    )
    return data, False


def invalidate_open_treks_cache():
    app.cache.delete(OPEN_TREKS_CACHE_KEY)


# ---------------------------------------------------------------------------
# AUTH  (Milestone 2)
# ---------------------------------------------------------------------------
@app.route("/login", methods=["POST"])
def login():
    email = request.json.get("email")
    pwd = request.json.get("password")

    user = User.query.filter_by(email=email).first()
    if not user:
        return {"message": "Email doesn't exist"}, 404

    # BETTERMENT over reference app: real hash verification, not `user.password == pwd`
    if not verify_password(pwd, user.password):
        return {"message": "Incorrect password"}, 401

    if user.status == "blacklisted":
        return {"message": "This account has been blacklisted/deactivated"}, 403

    return {
        "message": "Login Successful!",
        "role": user.roles[0].name,
        "token": user.get_auth_token(),
        "name": user.name,
        "id": user.id,
    }


@app.route("/register", methods=["POST"])
def register():
    email = request.json.get("email")
    pwd = request.json.get("password")
    confirm_pwd = request.json.get("confirm_password")
    name = request.json.get("name")
    contact_number = request.json.get("contact_number")

    ds = app.security.datastore

    if not email or not pwd or not name:
        return {"message": "name, email and password are required"}, 400

    if pwd != confirm_pwd:
        return {"message": "Passwords do not match"}, 400

    if ds.find_user(email=email):
        return {"message": "Email Already Exists"}, 409

    # BETTERMENT over reference app: role is NEVER taken from client input.
    ds.create_user(
        name=name,
        email=email,
        password=hash_password(pwd),
        contact_number=contact_number,
        active=True,
        roles=["trekker"],
    )
    db.session.commit()
    return {"message": "Account created successfully"}, 200


# ---------------------------------------------------------------------------
# ADMIN — Dashboard & Stats  (Milestone 3)
# ---------------------------------------------------------------------------
@app.route("/admin/dashboard", methods=["GET"])
@auth_required("token")
@roles_required("admin")
def admin_dashboard():
    total_treks = Trek.query.count()
    total_staff = User.query.join(User.roles).filter(Role.name == "staff").count()
    total_users = User.query.join(User.roles).filter(Role.name == "trekker").count()
    total_bookings = Booking.query.count()

    recent_bookings = Booking.query.order_by(Booking.id.desc()).limit(5).all()

    return {
        "total_treks": total_treks,
        "total_staff": total_staff,
        "total_users": total_users,
        "total_bookings": total_bookings,
        "recent_bookings": [booking_to_dict(b) for b in recent_bookings],
    }


# ---------------------------------------------------------------------------
# ADMIN — Manage Treks  (Milestone 3)
# ---------------------------------------------------------------------------
@app.route("/admin/treks", methods=["GET"])
@auth_required("token")
@roles_required("admin")
def admin_list_treks():
    treks = Trek.query.all()
    return [trek_to_dict(t) for t in treks], 200


@app.route("/admin/treks", methods=["POST"])
@auth_required("token")
@roles_required("admin")
def admin_create_trek():
    data = request.json or {}
    name = data.get("name")
    location = data.get("location")
    difficulty = data.get("difficulty")
    duration = data.get("duration")
    available_slots = data.get("available_slots")

    if not all([name, location, difficulty, duration is not None, available_slots is not None]):
        return {"message": "name, location, difficulty, duration and available_slots are required"}, 400

    trek = Trek(
        name=name,
        location=location,
        difficulty=difficulty,
        duration=duration,
        available_slots=available_slots,
        status="Pending",
        start_date=datetime.strptime(data["start_date"], "%Y-%m-%d").date() if data.get("start_date") else None,
        end_date=datetime.strptime(data["end_date"], "%Y-%m-%d").date() if data.get("end_date") else None,
    )
    db.session.add(trek)
    db.session.commit()
    invalidate_open_treks_cache()
    return {"message": "Trek created successfully", "trek": trek_to_dict(trek)}, 200


@app.route("/admin/treks/<int:trek_id>", methods=["PUT"])
@auth_required("token")
@roles_required("admin")
def admin_update_trek(trek_id):
    trek = Trek.query.get(trek_id)
    if not trek:
        return {"message": "Trek not found"}, 404

    data = request.json or {}

    for field in ["name", "location", "difficulty", "status"]:
        if field in data:
            setattr(trek, field, data[field])

    if "duration" in data:
        trek.duration = data["duration"]
    if "available_slots" in data:
        trek.available_slots = data["available_slots"]
    if "start_date" in data and data["start_date"]:
        trek.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
    if "end_date" in data and data["end_date"]:
        trek.end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()

    # Assigning staff — validate the target user actually IS staff
    if "assigned_staff_id" in data:
        staff_id = data["assigned_staff_id"]
        if staff_id is None:
            trek.assigned_staff_id = None
        else:
            staff_user = User.query.get(staff_id)
            if not staff_user or not any(r.name == "staff" for r in staff_user.roles):
                return {"message": "assigned_staff_id must reference an existing Trek Staff user"}, 400
            trek.assigned_staff_id = staff_id

    db.session.commit()
    invalidate_open_treks_cache()
    return {"message": "Trek updated successfully", "trek": trek_to_dict(trek)}, 200


@app.route("/admin/treks/<int:trek_id>", methods=["DELETE"])
@auth_required("token")
@roles_required("admin")
def admin_delete_trek(trek_id):
    trek = Trek.query.get(trek_id)
    if not trek:
        return {"message": "Trek not found"}, 404
    db.session.delete(trek)
    db.session.commit()
    invalidate_open_treks_cache()
    return {"message": "Trek deleted successfully"}, 200


# ---------------------------------------------------------------------------
# ADMIN — Create & Manage Trek Staff  (Milestone 3)
# ---------------------------------------------------------------------------
@app.route("/admin/staff", methods=["GET"])
@auth_required("token")
@roles_required("admin")
def admin_list_staff():
    staff_role = Role.query.filter_by(name="staff").first()
    staff_users = staff_role.bearers if staff_role else []
    result = []
    for s in staff_users:
        d = user_to_dict(s)
        d["experience_years"] = s.staff_profile.experience_years if s.staff_profile else None
        d["specialization"] = s.staff_profile.specialization if s.staff_profile else None
        result.append(d)
    return result, 200


@app.route("/admin/staff", methods=["POST"])
@auth_required("token")
@roles_required("admin")
def admin_create_staff():
    data = request.json or {}
    name = data.get("name")
    email = data.get("email")
    pwd = data.get("password")
    contact_number = data.get("contact_number")
    experience_years = data.get("experience_years")
    specialization = data.get("specialization")

    ds = app.security.datastore

    if not all([name, email, pwd]):
        return {"message": "name, email and password are required"}, 400

    if ds.find_user(email=email):
        return {"message": "Email Already Exists"}, 409

    # Same pattern as trekker registration, but role is forced to "staff" and
    # this endpoint itself is admin-only — matches "Trek Staff: created by
    # Admin only, no self-registration" from the problem statement.
    staff_user = ds.create_user(
        name=name,
        email=email,
        password=hash_password(pwd),
        contact_number=contact_number,
        active=True,
        roles=["staff"],
    )
    db.session.commit()

    profile = StaffProfile(
        user_id=staff_user.id,
        experience_years=experience_years,
        specialization=specialization,
    )
    db.session.add(profile)
    db.session.commit()

    return {"message": "Trek staff account created successfully"}, 200


# ---------------------------------------------------------------------------
# ADMIN — Manage Users (Trekkers)  (Milestone 3)
# ---------------------------------------------------------------------------
@app.route("/admin/users", methods=["GET"])
@auth_required("token")
@roles_required("admin")
def admin_list_users():
    trekker_role = Role.query.filter_by(name="trekker").first()
    trekkers = trekker_role.bearers if trekker_role else []
    return [user_to_dict(u) for u in trekkers], 200


# ---------------------------------------------------------------------------
# ADMIN — Blacklist / Whitelist a Staff or Trekker  (Milestone 3)
# Deliberately does NOT allow targeting an admin account.
# ---------------------------------------------------------------------------
@app.route("/admin/users/<int:user_id>/status", methods=["PUT"])
@auth_required("token")
@roles_required("admin")
def admin_set_user_status(user_id):
    target = User.query.get(user_id)
    if not target:
        return {"message": "User not found"}, 404

    if any(r.name == "admin" for r in target.roles):
        return {"message": "Cannot blacklist an Admin account"}, 400

    new_status = request.json.get("status")
    if new_status not in ("active", "blacklisted"):
        return {"message": "status must be 'active' or 'blacklisted'"}, 400

    target.status = new_status
    db.session.commit()
    return {"message": f"User status updated to {new_status}", "user": user_to_dict(target)}, 200


# ---------------------------------------------------------------------------
# ADMIN — Search treks / staff / users  (Milestone 3)
# ---------------------------------------------------------------------------
@app.route("/admin/search", methods=["GET"])
@auth_required("token")
@roles_required("admin")
def admin_search():
    q_type = request.args.get("type")   # "trek" | "staff" | "user"
    q = (request.args.get("q") or "").lower().strip()

    if q_type == "trek":
        treks = Trek.query.all()
        matches = [t for t in treks if q in t.name.lower() or q in str(t.id)]
        return [trek_to_dict(t) for t in matches], 200

    if q_type == "staff":
        staff_role = Role.query.filter_by(name="staff").first()
        staff_users = staff_role.bearers if staff_role else []
        matches = [s for s in staff_users if q in s.name.lower() or q in s.email.lower() or q in str(s.id)]
        return [user_to_dict(s) for s in matches], 200

    if q_type == "user":
        trekker_role = Role.query.filter_by(name="trekker").first()
        trekkers = trekker_role.bearers if trekker_role else []
        matches = [u for u in trekkers if q in u.name.lower() or q in u.email.lower() or q in str(u.id)]
        return [user_to_dict(u) for u in matches], 200

    return {"message": "type must be one of: trek, staff, user"}, 400


# ---------------------------------------------------------------------------
# ADMIN — View all bookings / trekking history  (Milestone 3)
# ---------------------------------------------------------------------------
@app.route("/admin/bookings", methods=["GET"])
@auth_required("token")
@roles_required("admin")
def admin_list_bookings():
    bookings = Booking.query.order_by(Booking.id.desc()).all()
    return [booking_to_dict(b) for b in bookings], 200


# ---------------------------------------------------------------------------
# STAFF — Dashboard  (Milestone 4)
# ---------------------------------------------------------------------------
@app.route("/staff/dashboard", methods=["GET"])
@auth_required("token")
@roles_required("staff")
def staff_dashboard():
    assigned = current_user.assigned_treks
    total_participants = sum(
        sum(1 for b in t.bookings if b.booking_status == "Booked") for t in assigned
    )
    ongoing = sum(1 for t in assigned if t.status == "Ongoing")

    return {
        "name": current_user.name,
        "assigned_trek_count": len(assigned),
        "total_participants": total_participants,
        "ongoing_trek_count": ongoing,
        "treks": [trek_to_dict(t) for t in assigned],
    }


# ---------------------------------------------------------------------------
# STAFF — Trek Operations  (Milestone 4)
# Every route below re-checks that the trek is actually assigned to the
# logged-in staff member — "Ensure only assigned staff can manage their trek".
# ---------------------------------------------------------------------------
def _get_own_trek_or_403(trek_id):
    trek = Trek.query.get(trek_id)
    if not trek:
        return None, ({"message": "Trek not found"}, 404)
    if trek.assigned_staff_id != current_user.id:
        return None, ({"message": "You are not assigned to this trek"}, 403)
    return trek, None


@app.route("/staff/treks/<int:trek_id>", methods=["GET"])
@auth_required("token")
@roles_required("staff")
def staff_get_trek(trek_id):
    trek, error = _get_own_trek_or_403(trek_id)
    if error:
        return error

    participants = [
        {
            "booking_id": b.id,
            "user_id": b.user_id,
            "name": b.user.name,
            "email": b.user.email,
            "booking_date": b.booking_date.isoformat() if b.booking_date else None,
            "booking_status": b.booking_status,
        }
        for b in trek.bookings
    ]

    result = trek_to_dict(trek)
    result["participants"] = participants
    return result, 200


@app.route("/staff/treks/<int:trek_id>/slots", methods=["PUT"])
@auth_required("token")
@roles_required("staff")
def staff_update_slots(trek_id):
    trek, error = _get_own_trek_or_403(trek_id)
    if error:
        return error

    new_slots = request.json.get("available_slots")
    if new_slots is None or new_slots < 0:
        return {"message": "available_slots must be a non-negative number"}, 400

    trek.available_slots = new_slots
    db.session.commit()
    invalidate_open_treks_cache()
    return {"message": "Available slots updated", "trek": trek_to_dict(trek)}, 200


@app.route("/staff/treks/<int:trek_id>/status", methods=["PUT"])
@auth_required("token")
@roles_required("staff")
def staff_update_status(trek_id):
    trek, error = _get_own_trek_or_403(trek_id)
    if error:
        return error

    new_status = request.json.get("status")
    allowed = ("Open", "Closed", "Ongoing", "Completed")
    if new_status not in allowed:
        return {"message": f"status must be one of {allowed}"}, 400

    trek.status = new_status
    db.session.commit()
    invalidate_open_treks_cache()
    return {"message": f"Trek status updated to {new_status}", "trek": trek_to_dict(trek)}, 200


# ---------------------------------------------------------------------------
# USER (Trekker) — Dashboard  (Milestone 5)
# ---------------------------------------------------------------------------
@app.route("/user/dashboard", methods=["GET"])
@auth_required("token")
@roles_required("trekker")
def user_dashboard():
    available_treks, _ = get_open_treks_cached()
    my_bookings = (
        Booking.query.filter_by(user_id=current_user.id, booking_status="Booked")
        .order_by(Booking.id.desc())
        .all()
    )
    return {
        "name": current_user.name,
        "available_treks": available_treks[:6],
        "my_bookings": [booking_to_dict(b) for b in my_bookings],
    }


# ---------------------------------------------------------------------------
# USER — Browse / Search Treks  (Milestone 5)
# Only status == "Open" treks are ever shown to trekkers.
# ---------------------------------------------------------------------------
@app.route("/user/treks", methods=["GET"])
@auth_required("token")
@roles_required("trekker")
def user_list_treks():
    treks, cache_hit = get_open_treks_cached()

    difficulty = request.args.get("difficulty")
    if difficulty:
        treks = [trek for trek in treks if trek["difficulty"] == difficulty]

    location = request.args.get("location")
    if location:
        location = location.lower()
        treks = [
            trek for trek in treks
            if location in trek["location"].lower()
        ]

    duration = request.args.get("duration")
    if duration:
        try:
            duration = int(duration)
        except ValueError:
            return {"message": "duration must be an integer"}, 400
        treks = [trek for trek in treks if trek["duration"] == duration]

    # Helpful during the viva: MISS on the first request, HIT afterwards.
    return treks, 200, {"X-Cache": "HIT" if cache_hit else "MISS"}


@app.route("/user/treks/<int:trek_id>", methods=["GET"])
@auth_required("token")
@roles_required("trekker")
def user_get_trek(trek_id):
    trek = Trek.query.get(trek_id)
    if not trek:
        return {"message": "Trek not found"}, 404
    return trek_to_dict(trek), 200


# ---------------------------------------------------------------------------
# USER — Book a Trek  (Milestone 5 & 6)
# Enforces, in this order: trek must be Open, must have slots left, and the
# user must not already hold an active ("Booked") booking for this trek.
# ---------------------------------------------------------------------------
@app.route("/user/treks/<int:trek_id>/book", methods=["POST"])
@auth_required("token")
@roles_required("trekker")
def user_book_trek(trek_id):
    trek = Trek.query.get(trek_id)
    if not trek:
        return {"message": "Trek not found"}, 404

    if trek.status != "Open":
        return {"message": "This trek is not open for booking"}, 400

    # Duplicate-booking check MUST come before the slots check: otherwise, once
    # a user's own booking consumes the last slot, their second attempt would
    # be misreported as "No slots available" instead of "already booked".
    existing = Booking.query.filter_by(
        user_id=current_user.id, trek_id=trek_id, booking_status="Booked"
    ).first()
    if existing:
        return {"message": "You have already booked this trek"}, 409

    if trek.available_slots <= 0:
        return {"message": "No slots available for this trek"}, 400

    booking = Booking(
        user_id=current_user.id,
        trek_id=trek_id,
        booking_date=datetime.utcnow().date(),
        booking_status="Booked",
        payment_status="Pending",
    )
    trek.available_slots -= 1
    db.session.add(booking)
    db.session.commit()
    invalidate_open_treks_cache()

    return {"message": "Trek booked successfully", "booking": booking_to_dict(booking)}, 200


# ---------------------------------------------------------------------------
# USER — Cancel a Booking  (Milestone 6)
# Slot is released back to the trek on cancellation.
# ---------------------------------------------------------------------------
@app.route("/user/bookings/<int:booking_id>/cancel", methods=["PUT"])
@auth_required("token")
@roles_required("trekker")
def user_cancel_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking or booking.user_id != current_user.id:
        return {"message": "Booking not found"}, 404

    if booking.booking_status != "Booked":
        return {"message": f"Cannot cancel a booking that is already {booking.booking_status}"}, 400

    booking.booking_status = "Cancelled"
    booking.trek.available_slots += 1
    db.session.commit()
    invalidate_open_treks_cache()
    return {"message": "Booking cancelled", "booking": booking_to_dict(booking)}, 200


# ---------------------------------------------------------------------------
# USER — Trekking History  (Milestone 6)
# "Users can access only their own booking/trekking history" — always scoped
# to current_user.id, never accepts a user_id from the client.
# ---------------------------------------------------------------------------
@app.route("/user/history", methods=["GET"])
@auth_required("token")
@roles_required("trekker")
def user_history():
    bookings = (
        Booking.query.filter_by(user_id=current_user.id)
        .order_by(Booking.id.desc())
        .all()
    )
    return [booking_to_dict(b) for b in bookings], 200


# ---------------------------------------------------------------------------
# USER — View / Update Profile  (Milestone 5)
# ---------------------------------------------------------------------------
@app.route("/user/profile", methods=["GET"])
@auth_required("token")
@roles_required("trekker")
def user_get_profile():
    return user_to_dict(current_user), 200


@app.route("/user/profile", methods=["PUT"])
@auth_required("token")
@roles_required("trekker")
def user_update_profile():
    data = request.json or {}
    if "name" in data and data["name"]:
        current_user.name = data["name"]
    if "contact_number" in data:
        current_user.contact_number = data["contact_number"]
    db.session.commit()
    return {"message": "Profile updated", "user": user_to_dict(current_user)}, 200

# ---------------------------------------------------------------------------
# USER — Trigger asynchronous CSV export of booking history (Milestone 7)
# ---------------------------------------------------------------------------
@app.route("/user/export-csv", methods=["GET"])
@auth_required("token")
@roles_required("trekker")
def user_export_csv():
    task = export_user_booking_history_csv.delay(current_user.id)
    return {"message": "CSV export queued", "task_id": task.id}, 202


# ---------------------------------------------------------------------------
# ADMIN — Manual triggers for scheduled jobs, useful during demo/viva.
# ---------------------------------------------------------------------------
@app.route("/admin/trigger-daily-reminders", methods=["POST"])
@auth_required("token")
@roles_required("admin")
def admin_trigger_daily_reminders():
    task = send_daily_trek_reminders.delay()
    return {"message": "Daily reminder job queued", "task_id": task.id}, 202


@app.route("/admin/trigger-monthly-report", methods=["POST"])
@auth_required("token")
@roles_required("admin")
def admin_trigger_monthly_report():
    task = generate_monthly_admin_report.delay()
    return {"message": "Monthly report job queued", "task_id": task.id}, 202


# Poll the result of an asynchronous task. Used by the CSV export button.
@app.route("/result/<task_id>", methods=["GET"])
@auth_required("token")
def get_task_result(task_id):
    celery_app = app.extensions["celery"]
    result = AsyncResult(task_id, app=celery_app)

    if result.failed():
        return {"ready": True, "successful": False, "message": str(result.result)}, 500

    if result.ready():
        return {"ready": True, "successful": True, "value": result.result}, 200

    return {"ready": False}, 200
