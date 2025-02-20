"""Database models for the application"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for storing user details and auth info"""
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(db.String(80), unique=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(db.String(120), unique=True, nullable=True)
    password_hash: Mapped[Optional[str]] = mapped_column(db.String(512), nullable=True)
    github_id: Mapped[Optional[int]] = mapped_column(unique=True, nullable=True)
    github_login: Mapped[Optional[str]] = mapped_column(db.String(80), nullable=True)
    github_access_token: Mapped[Optional[str]] = mapped_column(db.String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    def set_password(self, password: str) -> None:
        """Set the user's password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the hash"""
        if self.password_hash is None:
            return False
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self) -> str:
        return f'<User {self.username}>'
