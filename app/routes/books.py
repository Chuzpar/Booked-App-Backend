from flask import Blueprint, request, jsonify
from sqlalchemy import or_
from app.extensions import db
from app.models import Book, Genre

books_bp = Blueprint("books", __name__)


@books_bp.get("")
def list_books():
    query = Book.query
    section = request.args.get("section")
    if section == "store":
        query = query.filter(Book.is_purchasable.is_(True))
    elif section == "library":
        query = query.filter(Book.is_lendable.is_(True))

    q = request.args.get("q", "").strip()
    genre_name = request.args.get("genre")
    joined_genre = False
    if q:
        query = query.join(Genre)
        joined_genre = True
        like = f"%{q}%"
        query = query.filter(or_(Book.title.ilike(like), Book.author.ilike(like), Genre.name.ilike(like)))
    if genre_name and genre_name.lower() != "all":
        if not joined_genre:
            query = query.join(Genre)
        query = query.filter(Genre.name.ilike(genre_name))

    min_price = request.args.get("min_price", type=float)
    if min_price is not None:
        query = query.filter(Book.price >= min_price)
    max_price = request.args.get("max_price", type=float)
    if max_price is not None:
        query = query.filter(Book.price <= max_price)

    sort = request.args.get("sort", "newest")
    if sort == "price_asc":
        query = query.order_by(Book.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Book.price.desc())
    elif sort == "popularity":
        query = query.order_by(Book.review_count.desc())
    else:
        query = query.order_by(Book.date_uploaded.desc())

    books = query.all()
    return jsonify({"books": [b.to_dict() for b in books], "count": len(books)}), 200


@books_bp.get("/genres")
def list_genres():
    genres = Genre.query.order_by(Genre.name).all()
    return jsonify({"genres": [g.to_dict() for g in genres]}), 200


@books_bp.get("/<book_id>")
def get_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify({"book": book.to_dict()}), 200


def _apply_book_fields(book, data):
    for field in ["title", "author", "synopsis", "cover_image_url", "price",
                  "stock_qty", "is_purchasable", "is_lendable", "rating_avg", "review_count"]:
        if field in data:
            setattr(book, field, data[field])
    if "tags" in data:
        tags = data["tags"]
        book.tags = ",".join(tags) if isinstance(tags, list) else tags


@books_bp.post("")
def create_book():
    data = request.get_json(silent=True) or {}
    required = ["title", "author", "genre", "price"]
    missing = [f for f in required if not data.get(f) and data.get(f) != 0]
    if missing:
        return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400
    genre = Genre.query.filter_by(name=data["genre"]).first()
    if not genre:
        return jsonify({"error": f"Unknown genre '{data['genre']}'"}), 400
    book = Book(genre_id=genre.id)
    _apply_book_fields(book, data)
    db.session.add(book)
    db.session.commit()
    return jsonify({"book": book.to_dict()}), 201


@books_bp.put("/<book_id>")
def update_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    data = request.get_json(silent=True) or {}
    if "genre" in data:
        genre = Genre.query.filter_by(name=data["genre"]).first()
        if not genre:
            return jsonify({"error": f"Unknown genre '{data['genre']}'"}), 400
        book.genre_id = genre.id
    _apply_book_fields(book, data)
    db.session.commit()
    return jsonify({"book": book.to_dict()}), 200


@books_bp.delete("/<book_id>")
def delete_book(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": "Book deleted"}), 200