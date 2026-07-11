from flask import current_app as app
from .models import db, User, Role
from flask import request
from flask_security import auth_required, roles_required, current_user
from flask_security.utils import hash_password, verify_password


@app.route("/")
def home():
    return "Trekking Management Application API"


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
    # Only Trekkers may self-register — Admin creates Staff separately
    # (Admin Dashboard milestone), and there is exactly one Admin (bootstrapped
    # in initial_data.py). The reference app's register route trusted
    # request.json.get("role"), which would let anyone register as staff.
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


# Example protected route for this milestone — proves RBAC works end to end.
# Full Admin Dashboard functionality comes in its own milestone.
@app.route("/admin/dashboard", methods=["GET"])
@auth_required("token")
@roles_required("admin")
def admin_dashboard():
    return {"message": f"Welcome to the admin dashboard, {current_user.name}"}


@app.route("/staff/dashboard", methods=["GET"])
@auth_required("token")
@roles_required("staff")
def staff_dashboard():
    return {"message": f"Welcome to the staff dashboard, {current_user.name}"}


@app.route("/user/dashboard", methods=["GET"])
@auth_required("token")
@roles_required("trekker")
def user_dashboard():
    return {"message": f"Welcome to your dashboard, {current_user.name}"}
