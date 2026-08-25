from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import CartItem, Book

cart_bp = Blueprint("cart", __name__)


# NOTE: these routes assume a logged-in user's id is available.
# Since auth isn't merged yet, we temporarily accept user_id in the
# request body/query string instead of reading it from a JWT token.
# This must be replaced once feat/user-model merges.


@cart_bp.get("")
def list_cart():
    user_id = request.args.get("user_id")
    cart_type = request.args.get("cart_type")  # "purchase" | "lending" | omitted for both

    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    query = CartItem.query.filter_by(user_id=user_id)
    if cart_type:
        query = query.filter_by(cart_type=cart_type)

    items = query.all()
    return jsonify({"items": [i.to_dict() for i in items], "count": len(items)}), 200


@cart_bp.post("")
def add_to_cart():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    book_id = data.get("book_id")
    cart_type = data.get("cart_type")

    if not user_id or not book_id or not cart_type:
        return jsonify({"error": "user_id, book_id, and cart_type are required"}), 400

    if cart_type not in ("purchase", "lending"):
        return jsonify({"error": "cart_type must be 'purchase' or 'lending'"}), 400

    book = db.session.get(Book, book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404

    existing = CartItem.query.filter_by(
        user_id=user_id, book_id=book_id, cart_type=cart_type
    ).first()

    if existing:
        if cart_type == "purchase":
            existing.quantity += data.get("quantity", 1)
        db.session.commit()
        return jsonify({"item": existing.to_dict()}), 200

    item = CartItem(
        user_id=user_id,
        book_id=book_id,
        cart_type=cart_type,
        quantity=data.get("quantity", 1) if cart_type == "purchase" else 1,
        loan_period_days=data.get("loan_period_days") if cart_type == "lending" else None,
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({"item": item.to_dict()}), 201


@cart_bp.put("/<item_id>")
def update_cart_item(item_id):
    item = db.session.get(CartItem, item_id)
    if not item:
        return jsonify({"error": "Cart item not found"}), 404

    data = request.get_json(silent=True) or {}
    if "quantity" in data and item.cart_type == "purchase":
        item.quantity = max(1, data["quantity"])
    if "loan_period_days" in data and item.cart_type == "lending":
        item.loan_period_days = data["loan_period_days"]

    db.session.commit()
    return jsonify({"item": item.to_dict()}), 200


@cart_bp.delete("/<item_id>")
def remove_from_cart(item_id):
    item = db.session.get(CartItem, item_id)
    if not item:
        return jsonify({"error": "Cart item not found"}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item removed from cart"}), 200