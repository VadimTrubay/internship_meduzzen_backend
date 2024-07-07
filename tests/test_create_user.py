from app.models.user_model import User


def test_create_user(db):
    user = User(username="test_user", email="test@gmail.com", password="qwerty")
    db.add(user)

    db.commit()
    db.refresh(user)

    assert db.query(User).filter(User.username == "test_user").first() == user
