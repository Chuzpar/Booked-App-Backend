import uuid
from datetime import datetime, timezone
from app.extensions import db


def _uuid():
    return str(uuid.uuid4())


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    title = db.Column(db.String(200), nullable=False, index=True)
    author = db.Column(db.String(150), nullable=False, index=True)
    genre_id = db.Column(db.Integer, db.ForeignKey("genres.id"), nullable=False)
    genre = db.relationship("Genre")

    synopsis = db.Column(db.Text)
    cover_image_url = db.Column(db.String(500))
    tags = db.Column(db.String(300))

    rating_avg = db.Column(db.Float, default=0.0)
    review_count = db.Column(db.Integer, default=0)

    is_purchasable = db.Column(db.Boolean, default=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_qty = db.Column(db.Integer, default=0)

    is_lendable = db.Column(db.Boolean, default=False)
    lending_status = db.Column(db.String(20), default="available")
    current_due_at = db.Column(db.DateTime, nullable=True)

    date_uploaded = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id, "title": self.title, "author": self.author,
            "genre": self.genre.name if self.genre else None,
            "synopsis": self.synopsis, "cover_image_url": self.cover_image_url,
            "tags": self.tags.split(",") if self.tags else [],
            "rating_avg": self.rating_avg, "review_count": self.review_count,
            "is_purchasable": self.is_purchasable,
            "price": str(self.price) if self.price is not None else None,
            "stock_qty": self.stock_qty, "is_lendable": self.is_lendable,
            "lending_status": self.lending_status if self.is_lendable else None,
            "current_due_at": self.current_due_at.isoformat() if self.current_due_at else None,
            "date_uploaded": self.date_uploaded.isoformat(),
        }