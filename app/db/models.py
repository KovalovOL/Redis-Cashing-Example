from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base


community_followers = Table(
    "community_followers",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("community_id", ForeignKey("communities.id"), primary_key=True)
)


class Community(Base):
    __tablename__ = "communities"

    id = Column(Integer, primary_key=True)
    community_name = Column(String(50), unique=True, nullable=False)
    description = Column(String(500))
    photo_url = Column(String())

    followers = relationship("User", secondary=community_followers, back_populates="subscribes")
    posts = relationship("Post", cascade="all, delete-orphan")

    owner_id = Column(Integer, ForeignKey("users.id"))



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String)
    role = Column(String(50), nullable=False, default="user")
    avatar_url = Column(String, nullable=True)

    created_communities = relationship("Community", cascade="all, delete-orphan")
    created_posts = relationship("Post", cascade="all, delete-orphan")
    created_comments = relationship("Comment", cascade="all, delete-orphan")
    subscribes = relationship("Community", secondary=community_followers, back_populates="followers")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String(50), nullable=False)
    text = Column(String(500))

    community_id = Column(Integer, ForeignKey("communities.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))

    comments = relationship("Comment", cascade="all, delete-orphan")

    time_edited = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_edited = Column(Boolean, default=False)



class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    text = Column(String(500), nullable=False)

    post_id = Column(Integer, ForeignKey("posts.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))

    time_edited = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_edited = Column(Boolean, default=False)
