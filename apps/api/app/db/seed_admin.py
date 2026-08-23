import argparse

from sqlmodel import Session, select

from app.core.security import hash_password
from app.db.models.user import User, UserRole
from app.db.session import engine


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or promote an admin user")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--name", default="Administrator")
    args = parser.parse_args()
    if len(args.password) < 8:
        parser.error("password must contain at least 8 characters")

    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == args.email.lower())).first()
        if user:
            user.role = UserRole.ADMIN
            user.password_hash = hash_password(args.password)
            user.name = args.name
        else:
            user = User(
                email=args.email.lower(),
                password_hash=hash_password(args.password),
                name=args.name,
                role=UserRole.ADMIN,
            )
        session.add(user)
        session.commit()
        print(f"Admin user is ready: {user.email}")


if __name__ == "__main__":
    main()
