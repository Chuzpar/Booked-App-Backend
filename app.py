import os
from flask import Flask
from flask_cors import CORS
from config import config_by_name
from dotenv import load_dotenv
from app.extensions import db, migrate

load_dotenv()

config_name = os.getenv("FLASK_ENV", "development")

app = Flask(__name__)
app.config.from_object(config_by_name[config_name])

CORS(app, resources={r"/*": {"origins": "*"}} )
db.init_app(app)
migrate.init_app(app, db)


from app import models
from app.routes.books import books_bp
app.register_blueprint(books_bp, url_prefix="/api/books")


@app.route("/")
def home():
    return {"message": "Booked API is running"}


if __name__ == "__main__":
    app.run(debug=True)
