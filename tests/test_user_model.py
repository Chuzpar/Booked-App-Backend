import pytest

from app import create_app, db
from app.models import User


@pytest.fixture
def app():
    app = create_app()
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
    )

    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_create_user(app):
    user = User(
        name="Test User",
        email="test@example.com",
        role="user",
    )
    user.set_password("password123")

    db.session.add(user)
    db.session.commit()

    saved_user = User.query.filter_by(email="test@example.com").first()

    assert saved_user is not None
    assert saved_user.name == "Test User"
    assert saved_user.email == "test@example.com"
    assert saved_user.role == "user"


def test_password_is_hashed(app):
    user = User(
        name="Test User",
        email="test@example.com",
        role="user",
    )
    user.set_password("password123")

    assert user.password_hash != "password123"


def test_password_check(app):
    user = User(
        name="Test User",
        email="test@example.com",
        role="user",
    )
    user.set_password("password123")

    assert user.check_password("password123") is True
    assert user.check_password("wrong-password") is False