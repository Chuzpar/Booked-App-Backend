import uuid
from datetime import datetime, timezone
from app.extensions import db


def _uuid():
    return str(uuid.uuid4())


class CartItem(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    book_id = db.Column(db.String(36), db.ForeignKey("books.id"), nullable=False)

    cart_type = db.Column(db.String(20), nullable=False)  # "purchase" | "lending"
    quantity = db.Column(db.Integer, default=1)  # only used for purchase carts
    loan_period_days = db.Column(db.Integer, nullable=True)  # only used for lending carts

    added_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    book = db.relationship("Book")

    __table_args__ = (
        db.UniqueConstraint("user_id", "book_id", "cart_type", name="uq_user_book_cart_type"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "book_id": self.book_id,
            "book": self.book.to_dict() if self.book else None,
            "cart_type": self.cart_type,
            "quantity": self.quantity,
            "loan_period_days": self.loan_period_days,
            "added_at": self.added_at.isoformat(),
        }