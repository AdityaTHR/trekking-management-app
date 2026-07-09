from flask import Flask
from application.models import db

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trekking.db'
    
    db.init_app(app)
    return app

app = create_app()
from application.api import *
if __name__ == '__main__':
    app.run(debug=True)
