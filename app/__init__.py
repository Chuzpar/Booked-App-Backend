import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv


load_dotenv()

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so Flask-Migrate can detect them
    from app.models.user import User
    from app.models.book import Book

    from app.routes.book import books_bp
    app.register_blueprint(books_bp)

    @app.route("/")
    def home():
        return {
            "message": "Booked API is running!"
        }

    return app