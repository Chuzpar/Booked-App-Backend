import uuid
from datetime import datetime, timezone
from app.extensions import db


def _uuid():
    return str(uuid.uuid4())


class Purchase(db.Model):
    __tablename__ = "purchases"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)

    status = db.Column(db.String(20), default="pending")  # pending | approved | rejected | paid

    shipping_line1 = db.Column(db.String(200))
    shipping_line2 = db.Column(db.String(200))
    shipping_city = db.Column(db.String(100))
    shipping_state = db.Column(db.String(100))
    shipping_zip_code = db.Column(db.String(20))

    subtotal = db.Column(db.Numeric(10, 2), default=0)
    tax = db.Column(db.Numeric(10, 2), default=0)
    shipping_fee = db.Column(db.Numeric(10, 2), default=0)
    total = db.Column(db.Numeric(10, 2), default=0)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    approved_at = db.Column(db.DateTime, nullable=True)
    paid_at = db.Column(db.DateTime, nullable=True)

    items = db.relationship("PurchaseItem", backref="purchase", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "status": self.status,
            "shipping_address": {
                "line1": self.shipping_line1,
                "line2": self.shipping_line2,
                "city": self.shipping_city,
                "state": self.shipping_state,
                "zip_code": self.shipping_zip_code,
            },
            "subtotal": str(self.subtotal),
            "tax": str(self.tax),
            "shipping_fee": str(self.shipping_fee),
            "total": str(self.total),
            "created_at": self.created_at.isoformat(),
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
            "items": [item.to_dict() for item in self.items],
        }


class PurchaseItem(db.Model):
    __tablename__ = "purchase_items"

    id = db.Column(db.String(36), primary_key=True, default=_uuid)
    purchase_id = db.Column(db.String(36), db.ForeignKey("purchases.id"), nullable=False)
    book_id = db.Column(db.String(36), db.ForeignKey("books.id"), nullable=False)

    quantity = db.Column(db.Integer, default=1)
    price_at_purchase = db.Column(db.Numeric(10, 2), nullable=False)

    book = db.relationship("Book")

    def to_dict(self):
        return {
            "id": self.id,
            "purchase_id": self.purchase_id,
            "book_id": self.book_id,
            "book_title": self.book.title if self.book else None,
            "quantity": self.quantity,
            "price_at_purchase": str(self.price_at_purchase),
        }