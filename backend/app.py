from flask import Flask
from application.models import db, User, Role
from flask_security import Security, SQLAlchemyUserDatastore
from flask_cors import CORS
from flask_caching import Cache


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trekking.sqlite3"
    app.config["SECRET_KEY"] = "mysecretkey"
    app.config["SECURITY_TOKEN_AUTHENTICATION_HEADER"] = "Authentication-Token"

    # BETTERMENT over reference app: the reference app's /login route compared
    # user.password == pwd directly (plaintext), bypassing Flask-Security's own
    # hashing entirely. We instead configure a real hash scheme and always go
    # through flask_security.utils.hash_password / verify_password (see api.py).
    app.config["SECURITY_PASSWORD_HASH"] = "bcrypt"
    app.config["SECURITY_PASSWORD_SALT"] = "a-fixed-dev-salt-change-me"

    app.config["CACHE_TYPE"] = "redis"
    app.config["CACHE_REDIS_HOST"] = "localhost"
    app.config["CACHE_REDIS_PORT"] = 6379
    app.config["CACHE_REDIS_DB"] = 0
    app.config["CACHE_REDIS_URL"] = "redis://localhost:6379"

    db.init_app(app)
    CORS(app)

    ds = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, datastore=ds, register_blueprint=False)

    cache = Cache(app)

    @app.security.unauthz_handler
    def unauthz_handler(func_name, params):
        return {"message": "You are not authorised to view this resource."}, 403

    @app.security.unauthn_handler
    def unauthn_handler(mechanisms, headers):
        return {"message": "Please provide a valid auth token."}, 401

    app.app_context().push()
    return app, cache


app, cache = create_app()

# Celery gets wired in here in the "Backend Jobs" milestone (Celery + Redis),
# same as the reference app's app.py — left out for now to match our current
# milestone scope (DB models + Auth only).

from application.api import *
from application.initial_data import *


if __name__ == "__main__":
    app.run(debug=True)
