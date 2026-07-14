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

    # Redis API cache (Milestone 8). Use a separate Redis database from
    # Celery's broker (DB 0) and result backend (DB 1).
    app.config["CACHE_TYPE"] = "RedisCache"
    app.config["CACHE_REDIS_URL"] = "redis://localhost:6379/2"
    app.config["CACHE_DEFAULT_TIMEOUT"] = 60
    app.config["CACHE_KEY_PREFIX"] = "trekking-cache:"

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
# Make the cache available to route modules without importing app.py again.
app.cache = cache

# ---------------------------------------------------------------------------
# Celery + Redis background jobs (Milestone 7)
# ---------------------------------------------------------------------------
from application.celery_init import celery_init_app
from celery.schedules import crontab

celery = celery_init_app(app)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    from application.task import send_daily_trek_reminders, generate_monthly_admin_report

    # Daily reminders at 08:00 IST.
    sender.add_periodic_task(
        crontab(hour=8, minute=0),
        send_daily_trek_reminders.s(),
        name="daily trek reminders",
    )

    # Monthly activity report on the first day of each month at 06:00 IST.
    sender.add_periodic_task(
        crontab(day_of_month=1, hour=6, minute=0),
        generate_monthly_admin_report.s(),
        name="monthly admin report",
    )

from application.api import *
from application.initial_data import *


if __name__ == "__main__":
    app.run(debug=True)
