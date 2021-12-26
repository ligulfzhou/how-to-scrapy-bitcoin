from flask import Flask
from model import db
from route import router_bp
from errorhandler import eh_bp
from consts import database_url


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    db.init_app(app)
    with app.app_context():
        db.create_all()

    app.register_blueprint(router_bp)
    app.register_blueprint(eh_bp)
    return app
