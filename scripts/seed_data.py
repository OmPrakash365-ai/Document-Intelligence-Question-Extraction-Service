"""Seed script to create a default admin / test user."""

import uuid
from sqlalchemy import select
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User


def seed_user():
    db = SessionLocal()
    try:
        email = "evaluator@example.com"
        password = "Password123!"

        stmt = select(User).where(User.email == email)
        user = db.execute(stmt).scalar_one_or_none()
        if not user:
            user = User(
                id=uuid.uuid4(),
                email=email,
                password_hash=get_password_hash(password),
                is_active=True,
            )
            db.add(user)
            db.commit()
            print(f"Created demo user: {email} / {password}")
        else:
            print(f"Demo user {email} already exists.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_user()
