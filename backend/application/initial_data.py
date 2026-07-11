from .models import db, User, Role
from flask import current_app as app
from flask_security.utils import hash_password

with app.app_context():
    db.create_all()
    ds = app.security.datastore

    ds.find_or_create_role(name="admin", desc="superuser")
    ds.find_or_create_role(name="staff", desc="trek staff, created by admin only")
    ds.find_or_create_role(name="trekker", desc="self-registering user")
    db.session.commit()

    # Only ONE admin, created programmatically — no admin registration route exists.
    # BETTERMENT: password is hashed via flask_security's hash_password(), unlike
    # the reference app which stored/compared plaintext passwords.
    if not ds.find_user(email="admin@trekking.com"):
        ds.create_user(
            name="System Admin",
            email="admin@trekking.com",
            password=hash_password("Admin@123"),
            active=True,
            roles=["admin"],
        )
        db.session.commit()
        print("✔ Admin created -> admin@trekking.com / Admin@123 (change this before deploying)")
