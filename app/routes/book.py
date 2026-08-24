from flask import Blueprint, request, jsonify
from app import db
from app.models.book import Book

books_bp = Blueprint("books", __name__, url_prefix="/api/books")


# CREATE BOOK
@books_bp.route("/", methods=["POST"])
def create_book():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    title = data.get("title")
    author = data.get("author")

    if not title or not author:
        return jsonify({
            "error": "Title and author are required"
        }), 400

    isbn = data.get("isbn")

    if isbn:
        existing_book = Book.query.filter_by(isbn=isbn).first()

        if existing_book:
            return jsonify({
                "error": "A book with this ISBN already exists"
            }), 409

    book = Book(
        title=title,
        author=author,
        description=data.get("description"),
        isbn=isbn,
        published_year=data.get("published_year"),
        category=data.get("category"),
        available_copies=data.get("available_copies", 1)
    )

    db.session.add(book)
    db.session.commit()

    return jsonify({
        "message": "Book created successfully",
        "book": book.to_dict()
    }), 201


# GET ALL BOOKS
@books_bp.route("/", methods=["GET"])
def get_books():
    books = Book.query.order_by(Book.created_at.desc()).all()

    return jsonify({
        "books": [book.to_dict() for book in books],
        "count": len(books)
    }), 200


# GET ONE BOOK
@books_bp.route("/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = db.session.get(Book, book_id)

    if not book:
        return jsonify({
            "error": "Book not found"
        }), 404

    return jsonify({
        "book": book.to_dict()
    }), 200


# UPDATE BOOK
@books_bp.route("/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = db.session.get(Book, book_id)

    if not book:
        return jsonify({
            "error": "Book not found"
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    if "title" in data:
        if not data["title"]:
            return jsonify({
                "error": "Title cannot be empty"
            }), 400

        book.title = data["title"]

    if "author" in data:
        if not data["author"]:
            return jsonify({
                "error": "Author cannot be empty"
            }), 400

        book.author = data["author"]

    if "description" in data:
        book.description = data["description"]

    if "isbn" in data:
        isbn = data["isbn"]

        if isbn:
            existing_book = Book.query.filter(
                Book.isbn == isbn,
                Book.id != book.id
            ).first()

            if existing_book:
                return jsonify({
                    "error": "A book with this ISBN already exists"
                }), 409

        book.isbn = isbn

    if "published_year" in data:
        book.published_year = data["published_year"]

    if "category" in data:
        book.category = data["category"]

    if "available_copies" in data:
        if data["available_copies"] < 0:
            return jsonify({
                "error": "Available copies cannot be negative"
            }), 400

        book.available_copies = data["available_copies"]

    db.session.commit()

    return jsonify({
        "message": "Book updated successfully",
        "book": book.to_dict()
    }), 200


# DELETE BOOK
@books_bp.route("/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = db.session.get(Book, book_id)

    if not book:
        return jsonify({
            "error": "Book not found"
        }), 404

    db.session.delete(book)
    db.session.commit()

    return jsonify({
        "message": "Book deleted successfully"
    }), 200