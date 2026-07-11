from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin

db = SQLAlchemy()


# ---------------------------------------------------------------------------
# USER  — same Flask-Security pattern as the bootcamp reference app:
# one User table, roles attached via a many-to-many "user_roles" table.
# Roles here: "admin", "staff", "trekker"
# ---------------------------------------------------------------------------
class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    contact_number = db.Column(db.String, nullable=True)

    roles = db.relationship("Role", secondary="user_roles", backref="bearers")
    fs_uniquifier = db.Column(db.String, nullable=False, unique=True)
    active = db.Column(db.Boolean, nullable=False, default=True)

    # BETTERMENT over reference app: explicit status field for blacklisting,
    # separate from Flask-Security's own `active` flag, so Admin actions
    # ("Blacklist" button in the wireframe) are unambiguous in the UI/API.
    status = db.Column(db.String, nullable=False, default="active")  # active | blacklisted

    # Staff-only extra profile (created when Admin adds a Trek Staff member)
    staff_profile = db.relationship(
        "StaffProfile", backref="user", uselist=False, cascade="all, delete-orphan"
    )

    # Treks this user manages (only meaningful when role == staff)
    assigned_treks = db.relationship(
        "Trek", foreign_keys="Trek.assigned_staff_id", backref="assigned_staff"
    )

    # Bookings made by this user (only meaningful when role == trekker)
    bookings = db.relationship(
        "Booking", foreign_keys="Booking.user_id", backref="user",
        cascade="all, delete-orphan"
    )

    def has_role_name(self, name):
        return any(r.name == name for r in self.roles)


class Role(db.Model, RoleMixin):
    __tablename__ = "role"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    desc = db.Column(db.String, nullable=False)


class UserRole(db.Model):
    __tablename__ = "user_roles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=False)


# ---------------------------------------------------------------------------
# STAFF PROFILE (extra fields, same 1-to-1-extension idea as reference app's
# structure, applied to our Trek Staff instead of "Professional")
# ---------------------------------------------------------------------------
class StaffProfile(db.Model):
    __tablename__ = "staff_profile"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)
    experience_years = db.Column(db.Integer, nullable=True)
    specialization = db.Column(db.String, nullable=True)  # e.g. "High Altitude, First Aid"


# ---------------------------------------------------------------------------
# TREK  (equivalent role in reference app: Package)
# ---------------------------------------------------------------------------
class Trek(db.Model):
    __tablename__ = "trek"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    difficulty = db.Column(db.String, nullable=False)   # Easy / Moderate / Hard
    duration = db.Column(db.Integer, nullable=False)     # in days
    available_slots = db.Column(db.Integer, nullable=False, default=0)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)

    # Pending / Approved / Open / Closed / Completed
    status = db.Column(db.String, nullable=False, default="Pending")

    assigned_staff_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)

    bookings = db.relationship(
        "Booking", foreign_keys="Booking.trek_id", backref="trek",
        cascade="all, delete-orphan"
    )


# ---------------------------------------------------------------------------
# BOOKING  (equivalent role in reference app: Booking, same shape)
# ---------------------------------------------------------------------------
class Booking(db.Model):
    __tablename__ = "booking"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("trek.id"), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)

    # Booked / Cancelled / Completed
    booking_status = db.Column(db.String, nullable=False, default="Booked")
    payment_status = db.Column(db.String, nullable=False, default="Pending")
