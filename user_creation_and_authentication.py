from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import password_hashing as ph
import create_database as cd


def create_user(db: Session, username: str, password: str):
    hashed_password = ph.get_password_hash(password)
    db_user = cd.User(username=username, hashed_password=hashed_password)
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise ValueError("Username already taken")


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(cd.User).filter(cd.User.username == username).first()
    if user and ph.verify_password(password, user.hashed_password):
        return user
    return None
